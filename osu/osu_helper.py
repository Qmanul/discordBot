from __future__ import annotations
from typing import List
import aiosu
import discord
from sqlalchemy.ext.asyncio import AsyncSession
from crud import osu_user_crud
from osu.osu_embed import create_user_info_embed, create_score_embed


class OsuClient:
    def __init__(self, server_dict: dict) -> None:
        self.server_dict = server_dict

    async def get_user_recent_scores(
            self,
            username: str,
            **kwargs
    ) -> List[aiosu.models.Score | aiosu.models.LazerScore]:

        if (server := kwargs.get('server', 'bancho')) not in self.server_dict.keys():
            raise ValueError('Please provide a valid server')

        async with self.server_dict[server] as client:
            user = await self.get_user_by_name(username, server=server)
            return await client.get_user_recents(user.id, **kwargs)

    async def get_user_by_name(
            self,
            username: str,
            **kwargs
    ) -> aiosu.models.User:

        gamemode = kwargs.pop('gamemode', aiosu.models.Gamemode.STANDARD)
        if (server := kwargs.get('server', 'bancho')) not in self.server_dict.keys():
            raise ValueError

        async with self.server_dict[server] as client:
            return await client.get_user(username, mode=gamemode)


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
            recent_scores = await self.osu_client.get_user_recent_scores(username, **kwargs)
        except ValueError:
            return 'Please provide a valid server'
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        if not recent_scores:
            return f'{username} has no recent scores'

        return await create_score_embed(recent_scores[0], **kwargs)

    async def process_user_link(self, session: AsyncSession, **kwargs) -> str | discord.Embed:
        username = kwargs.pop('username')
        discord_id = kwargs.pop('discord_id')

        if not username:
            return 'Please provide a valid username'

        try:
            user_info = await self.osu_client.get_user_by_name(username, servrer=kwargs.pop('server', 'bancho'))
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
            user_info = await self.osu_client.get_user_by_name(username, gamemode=gamemode, **kwargs)
        except aiosu.exceptions.APIException:
            return f'{username} was not found'

        return await create_user_info_embed(user_info, gamemode=gamemode, **kwargs)
