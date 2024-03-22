from __future__ import annotations

from typing import TYPE_CHECKING

from aiosu.helpers import add_param
from aiosu.helpers import from_list
from aiosu.models import Gamemode

from osu.api.base_api import BaseClient
from osu.api.models.beatmap import RippleBeatmapUserMostPlayed
from osu.api.models.score import RippleScoreUser, RippleScoreBeatmap
from osu.api.models.user import RippleUser, RippleUserFull
from utils.utils import process_query_type

if TYPE_CHECKING:
    from typing import Any

__all__ = ("RippleClient", "RippleRelaxClient")


class RippleClient(BaseClient):
    __slots__ = (
        'token',
        'authorization_header',
        'relax_param_keyname',
        'relax',
        'base_url'
    )

    def __init__(self, **kwargs: Any, ) -> None:
        super().__init__(**kwargs)
        self.token: str = kwargs.pop('token', '')
        self.authorization_header: str = kwargs.pop('authorization_header', 'X-Ripple-Token')
        self.relax_param_keyname: str = kwargs.pop('relax_param_keyname', 'relax')
        self.relax: int = int(kwargs.pop('relax', False))
        self.base_url: str = 'https://ripple.moe'

    async def _get_headers(self) -> dict[str, str]:
        return {
            f"{self.authorization_header}": f"{self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_user(self, user_query: int | str, **kwargs: Any) -> RippleUserFull:
        url = f"{self.base_url}/api/v1/users/full"
        qtype = await process_query_type(user_query, kwargs)
        params: dict[str, object] = {
            qtype: user_query,
            self.relax_param_keyname: self.relax
        }
        json = await self._request("GET", url, params=params)
        return RippleUserFull.model_validate(json)

    async def get_users(self, user_queries: list[str] | list[int], **kwargs: Any) -> list[RippleUser]:
        url = f"{self.base_url}/api/v1/users"
        qtype = await process_query_type(user_queries[0], kwargs, ('names', 'ids'))
        params: dict[str, object] = {
            qtype: user_queries
        }
        add_param(
            params,
            kwargs,
            key="countries",
            param_name="countries")
        json = await self._request("GET", url, params=params)
        return from_list(RippleUser.model_validate, json.get("users", []))

    async def _get_type_scores(
            self,
            user_query: int | str,
            request_type: str,
            **kwargs: Any,
    ) -> list[RippleScoreUser]:
        if not 1 <= (limit := kwargs.pop("limit", 100)) <= 100:
            raise ValueError("Invalid limit specified. Limit must be between 1 and 100")
        if request_type not in ("recent", "best"):
            raise ValueError(
                f'"{request_type}" is not a valid request_type. Valid options are: "recent", "best"',
            )
        url = f"{self.base_url}/api/v1/users/scores/{request_type}"
        qtype = await process_query_type(user_query, kwargs)
        params: dict[str, object] = {
            "l": limit,
            qtype: user_query,
            self.relax_param_keyname: self.relax
        }
        add_param(params, kwargs, key="page", param_name='p')
        add_param(params, kwargs, key="gamemode", param_name='mode', converter=lambda x: str(Gamemode(x)))
        json = await self._request("GET", url, params=params)
        return from_list(RippleScoreUser.model_validate, scores if (scores := json.get('scores')) is not None else [])

    async def get_user_recents(
            self,
            user_query: int | str,
            **kwargs: Any,
    ) -> list[RippleScoreUser]:

        return await self._get_type_scores(user_query, "recent", **kwargs)

    async def get_user_bests(
            self,
            user_query: int | str,
            **kwargs: Any,
    ) -> list[RippleScoreUser]:

        return await self._get_type_scores(user_query, "best", **kwargs)

    async def get_user_most_played(
            self,
            user_query: int | str,
            **kwargs: Any,
    ) -> list[RippleBeatmapUserMostPlayed]:

        url = f"{self.base_url}/api/v1/users/most_played"
        qtype = await process_query_type(user_query, kwargs, )
        params: dict[str, object] = {
            qtype: user_query
        }
        add_param(params, kwargs, key="limit", param_name='l')
        add_param(params, kwargs, key="page", param_name='p')
        json = await self._request("GET", url, params=params)
        return from_list(RippleBeatmapUserMostPlayed.model_validate, json.get('beatmaps', []))

    async def get_beatmap_scores(
            self,
            beatmap_query: int | str,
            **kwargs: Any
    ) -> list[RippleScoreBeatmap]:

        url = f"{self.base_url}/api/v1/scores"
        qtype = await process_query_type(beatmap_query, kwargs, ('md5', 'id'))
        params: dict[str, object] = {
            qtype: beatmap_query,
            self.relax_param_keyname: self.relax
        }
        add_param(params, kwargs, key='gamemode', param_name="mode", converter=lambda x: str(Gamemode(x)))
        json = await self._request("GET", url, params=params)
        return from_list(RippleScoreBeatmap.model_validate, json.get("scores", []))


class RippleRelaxClient(RippleClient):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.relax = 1
