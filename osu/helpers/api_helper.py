from __future__ import annotations

import os
from random import choice

import aiosu

from osu.api.models.score import RippleScoreUser, GatariScore
from osu.api.models.user import RippleUserFull, GatariUser
from utils.file_utils import extract_maps_from_osz_bytes, path_exists


class ApiHelper:
    def __init__(self, api_client_map: dict) -> None:
        self.api_client_map = api_client_map
        self.beatmaps_filepath = os.path.join(os.getcwd(), 'osu', 'beatmaps')

    async def get_user_recent_scores(
            self,
            username: str,
            **kwargs
    ) -> list[aiosu.models.Score | aiosu.models.LazerScore | RippleScoreUser | GatariScore]:

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
