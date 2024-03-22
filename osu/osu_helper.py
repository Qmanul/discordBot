from __future__ import annotations

import os.path
from typing import List

import aiosu
import discord
from sqlalchemy.ext.asyncio import AsyncSession

from crud import osu_user_crud
from osu.api.models.score import GatariScore, RippleScoreUser
from osu.api.models.user import GatariUser, RippleUserFull
from osu.osu_embed import create_user_info_embed, create_score_embed
from osu.rosu import get_score_performance
from utils.file_utils import path_exists, extract_osu_from_osz_bytes


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

    async def get_beatmap_filepath(self, beatmap):
        filepath = os.path.join(self.beatmaps_filepath, f'{beatmap.id}.osu')
        if await path_exists(filepath):
            return filepath

        async with self.api_client_map['direct'] as client:
            await extract_osu_from_osz_bytes(await client.get_beatmapset_file(beatmap.beatmapset_id))

        return filepath


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
                if not gamemode:
                    gamemode = db_user.osu_gamemode

                username = db_user.osu_username

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
