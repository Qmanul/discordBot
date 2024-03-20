from __future__ import annotations
from io import BytesIO
from typing import TYPE_CHECKING
from typing import Literal
import aiohttp
import orjson
from aiolimiter import AsyncLimiter
from aiosu.exceptions import APIException
from aiosu.helpers import add_param
from aiosu.helpers import from_list
from aiosu.models import Gamemode
from osu.api.models.beatmap import RippleBeatmapUserMostPlayed, RippleScoreUser, RippleScoreBeatmap
from osu.api.models.user import RippleUser, RippleUserFull
from utils.utils import process_query_type

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Any
    from typing import Optional

__all__ = ("RippleClient", "RippleRelaxClient")

ClientRequestType = Literal["GET", "POST", "DELETE", "PUT", "PATCH"]


def get_content_type(content_type: str) -> str:
    return content_type.split(";")[0]


class RippleClient:
    __slots__ = (
        "token",
        "base_url",
        "_session",
        "_limiter",
        'authorization_header',
        'relax_param_keyname',
        'relax'
    )

    def __init__(
            self,
            **kwargs: Any,
    ) -> None:
        max_rate, time_period = kwargs.pop("limiter", (2000, 60))
        self.token: str = kwargs.pop('token', '')
        self.base_url: str = kwargs.pop('base_url', 'https://ripple.moe')
        self.authorization_header: str = kwargs.pop('authorization_header', 'X-Ripple-Token')
        self.relax_param_keyname: str = kwargs.pop('relax_param_keyname', 'relax')
        self.relax: int = int(kwargs.pop('relax', False))
        self._limiter: AsyncLimiter = AsyncLimiter(
            max_rate=max_rate,
            time_period=time_period,
        )
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> RippleClient:
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    async def _get_headers(self) -> dict[str, str]:
        return {
            f"{self.authorization_header}": f"{self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
            self,
            request_type: ClientRequestType,
            *args: Any,
            **kwargs: Any,
    ) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=await self._get_headers())

        async with self._limiter:
            async with self._session.request(request_type, *args, **kwargs) as resp:
                if resp.status == 204:
                    return
                if resp.status != 200:
                    raise APIException(resp.status, await resp.text())
                content_type = get_content_type(resp.headers.get("content-type", ""))
                if content_type == "application/json":
                    return orjson.loads(await resp.read())
                if content_type == "application/octet-stream":
                    return BytesIO(await resp.read())
                if content_type.startswith("application/x-osu"):
                    return BytesIO(await resp.read())
                if content_type == "text/plain":
                    return await resp.text()
                raise APIException(
                    resp.status,
                    f"Unhandled Content Type '{content_type}'",
                )

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
        add_param(params, kwargs, key="mode", converter=lambda x: str(Gamemode(x)))
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
        qtype = await process_query_type(user_query, kwargs,)
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
        add_param(params, kwargs, key="mode", converter=lambda x: str(Gamemode(x)))
        json = await self._request("GET", url, params=params)
        return from_list(RippleScoreBeatmap.model_validate, json.get("scores", []))

    async def aclose(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None


class RippleRelaxClient(RippleClient):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.relax = 1
