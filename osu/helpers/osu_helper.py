from __future__ import annotations

import aiosu
import discord
from sqlalchemy.ext.asyncio import AsyncSession

from crud import osu_user_crud
from osu.helpers import ApiHelper
from osu.osu_embed import create_user_info_embed, create_score_embed
from osu.rosu import get_score_performance


class OsuHelper:
    def __init__(self, api_helper: ApiHelper) -> None:
        self.api_helper = api_helper

    async def process_recent_scores(self, session: AsyncSession, **kwargs) -> str | discord.Embed:
        username = kwargs.pop('username', None)
        discord_id = kwargs.pop('discord_id')

        if not username:
            db_user = await osu_user_crud.get_user(session, discord_id)
            try:
                username = db_user.osu_username
            except AttributeError:
                return 'Your account is not linked osu profile'

        try:
            recent_score = (await self.api_helper.get_user_recent_scores(username, **kwargs)).pop()
        except ValueError:
            return 'Please provide a valid server'
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        if not recent_score:
            return f'{username} has no recent scores'

        filepath = await self.api_helper.get_beatmap_filepath(recent_score.beatmap)
        pp, fc_pp = await get_score_performance(filepath, recent_score)

        return await create_score_embed(recent_score, filepath=filepath, pp=pp, fc_pp=fc_pp, **kwargs)

    async def process_user_link(self, session: AsyncSession, **kwargs) -> str | discord.Embed:
        username = kwargs.pop('username')
        discord_id = kwargs.pop('discord_id')

        if not username:
            return 'Please provide a valid username'

        try:
            user_info = await self.api_helper.get_user_info(username, servrer=kwargs.pop('server', 'bancho'))
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        await osu_user_crud.update_or_create_user(session, discord_id=discord_id, osu_user_id=user_info.id,
                                                  osu_username=user_info.username, osu_gamemode=user_info.playmode.id)

        return f'Successfully linked to {user_info.username}'

    async def process_user_info(self, session: AsyncSession, **kwargs) -> str | discord.Embed:
        username = kwargs.pop('username', None)
        discord_id = kwargs.pop('discord_id')
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
            user_info = await self.api_helper.get_user_info(username, gamemode=gamemode, **kwargs)
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        return await create_user_info_embed(user_info, gamemode=gamemode, **kwargs)
