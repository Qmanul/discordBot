from __future__ import annotations

from io import BytesIO
from types import TracebackType
from typing import Self, Literal, Any

import aiohttp
from aiolimiter import AsyncLimiter
from aiosu.exceptions import APIException
from orjson import orjson

ClientRequestType = Literal["GET", "POST", "DELETE", "PUT", "PATCH"]


def get_content_type(content_type: str) -> str:
    return content_type.split(";")[0]


class BaseClient:
    __slots__ = {
        '_session',
        '_limiter',
        'base_url',
    }

    def __init__(self, **kwargs):
        max_rate, time_period = kwargs.pop("limiter", (2000, 60))
        self._session: aiohttp.ClientSession | None = None
        self._limiter: AsyncLimiter = AsyncLimiter(
            max_rate=max_rate,
            time_period=time_period,
        )
        self.base_url: str = kwargs.pop('base_url', '')

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def _get_headers(self) -> dict[str, str]:
        return {
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
                if content_type in ("application/octet-stream", 'image/jpg') or content_type.startswith(
                        "application/x-osu"):
                    return BytesIO(await resp.read())
                if content_type == "text/plain":
                    return await resp.text()
                raise APIException(resp.status, f"Unhandled Content Type '{content_type}'", )
