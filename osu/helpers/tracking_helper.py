import asyncio

import aiosu
import discord
from sqlalchemy.ext.asyncio import AsyncSession

from crud import tracking_crud, osu_user_crud
from osu.helpers import ApiHelper
from osu.osu_embed import create_new_hiscore_embed


class TrackingHelper:
    def __init__(self, api_helper: ApiHelper):
        self.api_helper = api_helper

    async def process_tracking_link(self, session, discord_id: int, **kwargs):
        username = kwargs.pop('username', None)
        gamemode = kwargs.pop('gamemode', None)

        if not username:
            db_user = await osu_user_crud.get_user(session, discord_id)

            try:
                username = db_user.osu_username

                if not gamemode:
                    gamemode = db_user.osu_gamemode

            except AttributeError:
                return 'You are not linked to osu account'

        try:
            gamemode = aiosu.models.Gamemode(gamemode)
        except ValueError:
            return 'Please provide a valid gamemode'

        try:
            user_info = await self.api_helper.get_user_info(username, **kwargs)
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        await tracking_crud.create_or_update_user(session, discord_id, osu_gamemode=gamemode, osu_user_id=user_info.id)

        return f'Successfully linked <@{discord_id}> to **{user_info.username}**'

    async def process_tracking_register(
            self,
            session: AsyncSession,
            discord_id: int,
            channel: discord.TextChannel
    ) -> str:
        try:
            await tracking_crud.register_user(session, discord_id, channel.id)
        except ValueError:
            return f'Tracking is not enabled in **{channel.name}**'

        return f'Successfully registered <@{discord_id}> in channel **{channel.name}**'

    async def process_tracking_enable(self, session: AsyncSession, channel: discord.TextChannel):
        if await tracking_crud.get_channel(session, channel_id=channel.id):
            return f'Tracking is already enabled in channel **{channel.name}**'

        await tracking_crud.insert_channel(session, channel_id=channel.id, guild_id=channel.guild.id)
        return f'Successfully enabled tracking in channel **{channel.name}**'

    async def process_tracking_disable(self, session: AsyncSession, channel: discord.TextChannel):
        try:
            await tracking_crud.delete_channel(session, channel_id=channel.id)
        except ValueError:
            return f'Tracking is not enabled in **{channel.name}**'

        return f'Successfully disabled tracking in channel **{channel.name}**'

    async def process_tracked_users(self, session: AsyncSession):
        async def process_user(user):
            if not ((osu_user_id := user.osu_user_id) and (channels := user.tracked_channels)):
                return

            update_info = await self.api_helper.update_user(osu_user_id, gamemode=user.osu_gamemode)
            if not (scores := update_info.newhs):
                return

            for score in scores[:3]:
                channel_ids = [channel.id for channel in channels if channel.pp_cutoff < int(score.pp)]
                embed = await create_new_hiscore_embed(score, update_info.dict(exclude={'newhs'}))
                return channel_ids, embed

        tracked_users = await tracking_crud.get_users(session)
        for completed in asyncio.as_completed(map(process_user, tracked_users)):
            yield await completed
