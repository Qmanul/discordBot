from __future__ import annotations

from typing import Any

import aiosu.models
from aiosu.exceptions import APIException
from aiosu.helpers import add_param, from_list
from aiosu.models import Gamemode

from osu.api.base_api import BaseClient
from osu.api.models.score import GatariScore
from osu.api.models.user import GatariUser, GatariUserInfo


class GatariClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.gatari.pw/{}'

    async def get_user_info(self, user_query: str | int):
        url = self.base_url.format('users/get')
        params: dict[str, object] = {
            'u': user_query
        }
        json = await self._request('GET', url, params=params)
        if not (stats := json.pop('users')):
            raise APIException(404, 'user not found')
        return GatariUserInfo.model_validate(stats.pop())

    async def get_user(self, user_query: int | str, **kwargs) -> GatariUser:
        url = self.base_url.format('user/stats')
        params: dict[str, object] = {
            'u': user_query
        }
        add_param(
            params,
            kwargs,
            key='gamemode',
            param_name='mode',
            converter=lambda x: aiosu.models.Gamemode(x).id
        )

        json = await self._request("GET", url, params=params)
        if not (stats := json.pop('stats')):
            raise APIException(404, 'user not found')
        stats['user_info'] = await self.get_user_info(user_query)
        return GatariUser.validate(stats)

    async def _get_type_scores(
            self,
            user_id: int,
            request_type: str,
            **kwargs: Any,
    ) -> list[GatariScore]:
        if not 1 <= (limit := kwargs.pop("limit", 100)) <= 100:
            raise ValueError("Invalid limit specified. Limit must be between 1 and 100")
        if request_type not in ("recent", "best"):
            raise ValueError(
                f'"{request_type}" is not a valid request_type. Valid options are: "recent", "best"',
            )
        url = self.base_url.format(f'user/scores/{request_type}')
        gamemode = kwargs.pop('gamemode', Gamemode.STANDARD)
        include_failed = kwargs.pop('failed', True)
        params: dict[str, object] = {
            'l': limit,
            'id': user_id,
            'mode': Gamemode(gamemode).id,
            'f': int(include_failed),
        }
        add_param(params, kwargs, key="page", param_name='p')
        json = await self._request("GET", url, params=params)
        print(json)
        return from_list(GatariScore.model_validate, scores if (scores := json.get('scores')) is not None else [])

    async def get_user_recents(
            self,
            user_id: int,
            **kwargs: Any,
    ) -> list[GatariScore]:

        return await self._get_type_scores(user_id, "recent", **kwargs)
