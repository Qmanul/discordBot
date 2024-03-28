from __future__ import annotations

import asyncio
import os.path
from random import choice
from typing import List

import aiosu
import discord
from sqlalchemy.ext.asyncio import AsyncSession

from crud import osu_user_crud
from crud import tracking_crud
from osu.api.models.score import GatariScore, RippleScoreUser
from osu.api.models.user import GatariUser, RippleUserFull, OsutrackUser
from osu.api.rdr_api import OrdrClient
from osu.osu_embed import create_user_info_embed, create_score_embed, create_new_hiscore_embed
from osu.rosu import get_score_performance
from utils.file_utils import path_exists, extract_maps_from_osz_bytes


class OsuClient:
    def __init__(self, api_client_map: dict) -> None:
        self.api_client_map = api_client_map
        self.beatmaps_filepath = os.path.join(os.getcwd(), 'osu', 'beatmaps')

    async def get_user_recent_scores(
            self,
            username: str,
            **kwargs
    ) -> List[aiosu.models.Score | aiosu.models.LazerScore | RippleScoreUser | GatariScore]:

        if (server := kwargs.get('server', 'bancho')) not in self.api_client_map.keys():
            raise ValueError('Please provide a valid server')

        async with self.api_client_map[server] as client:
            if server in ('bancho', 'gatari',):
                user = await client.get_user(username, **kwargs)
                return await client.get_user_recents(user.id, **kwargs)

            return await client.get_user_recents(username, **kwargs)

    async def get_user_info(
            self,
            username: str,
            **kwargs
    ) -> aiosu.models.User | RippleUserFull | GatariUser:
        if (server := kwargs.get('server', 'bancho')) not in self.api_client_map.keys():
            raise ValueError

        async with self.api_client_map[server] as client:
            return await client.get_user(username, **kwargs)

    async def get_user_id(
            self,
            username: str,
            **kwargs
    ) -> int:
        if (server := kwargs.get('server', 'bancho')) not in self.api_client_map.keys():
            raise ValueError

        async with self.api_client_map[server] as client:
            return (await client.get_user(username, **kwargs)).id

    async def get_beatmap_filepath(self, beatmap) -> str:
        filepath = os.path.join(self.beatmaps_filepath, f'{beatmap.id}.osu')
        if await path_exists(filepath):
            return filepath

        async with self.api_client_map[choice(['nerinyan', 'direct'])] as client:
            await extract_maps_from_osz_bytes(await client.download_betmapset(beatmap.beatmapset_id))

        return filepath

    async def update_user(self, user_id: int, **kwargs) -> OsutrackUser:
        async with self.api_client_map['osutrack'] as client:
            return await client.update_user(user_id, **kwargs)

    async def get_score(self, score_id, gamemode, **kwargs) -> aiosu.models.Score:
        async with self.api_client_map['bancho'] as client:
            return await client.get_score(score_id, gamemode, **kwargs)


class OsuHelper:
    def __init__(self, osu_client: OsuClient) -> None:
        self.osu_client = osu_client

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
            recent_score = (await self.osu_client.get_user_recent_scores(username, **kwargs)).pop()
        except ValueError:
            return 'Please provide a valid server'
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        if not recent_score:
            return f'{username} has no recent scores'

        filepath = await self.osu_client.get_beatmap_filepath(recent_score.beatmap)
        pp, fc_pp = await get_score_performance(filepath, recent_score)

        return await create_score_embed(recent_score, filepath=filepath, pp=pp, fc_pp=fc_pp, **kwargs)

    async def process_user_link(self, session: AsyncSession, **kwargs) -> str | discord.Embed:
        username = kwargs.pop('username')
        discord_id = kwargs.pop('discord_id')

        if not username:
            return 'Please provide a valid username'

        try:
            user_info = await self.osu_client.get_user_info(username, servrer=kwargs.pop('server', 'bancho'))
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
            user_info = await self.osu_client.get_user_info(username, gamemode=gamemode, **kwargs)
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        return await create_user_info_embed(user_info, gamemode=gamemode, **kwargs)


class RenderHelper:
    def __init__(self, ordr_client: OrdrClient) -> None:
        self.ordr_client = ordr_client

    async def process_render(self, ):
        return


class TrackingHelper:
    def __init__(self, osu_client: OsuClient):
        self.osu_client = osu_client

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
            user_info = await self.osu_client.get_user_info(username, **kwargs)
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

        await tracking_crud.create_or_update_channel(session, channel_id=channel.id)
        return f'Successfully enabled tracking in channel **{channel.name}**'

    async def process_tracking_disable(self, session: AsyncSession, channel: discord.TextChannel):
        try:
            await tracking_crud.remove_tracked_channel(session, channel_id=channel.id)
        except ValueError:
            return f'Tracking is not enabled in **{channel.name}**'

        return f'Successfully disabled tracking in channel **{channel.name}**'

    async def process_tracked_users(self, session: AsyncSession):
        async def process_user(user):
            if not ((osu_user_id := user.osu_user_id) and (channels := user.tracked_channels)):
                return

            update_info = await self.osu_client.update_user(osu_user_id, gamemode=user.osu_gamemode)
            if not (scores := update_info.newhs):
                return

            for score in scores[:3]:
                channel_ids = [channel.id for channel in channels if channel.pp_cutoff < int(score.pp)]
                embed = (await create_new_hiscore_embed(score, update_info.dict(exclude={'newhs'})))
                return channel_ids, embed

        tracked_users = await tracking_crud.get_users(session)
        for completed in asyncio.as_completed(map(process_user, tracked_users)):
            yield await completed
