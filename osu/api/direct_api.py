from __future__ import annotations

from io import BytesIO

from aiosu.helpers import add_param

from osu.api.base_api import BaseClient


class DirectClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.osu.direct/{}'

    async def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/octet-stream",
        }

    async def get_beatmap_file(self, beatmap_id, **kwargs) -> str:
        url = self.base_url.format(f'osu/{beatmap_id}')
        params: [str, object] = {}
        add_param(params, kwargs, 'raw')
        return await self._request('GET', url, params=params)

    async def get_beatmapset_file(self, beatmapset_id: int) -> BytesIO:
        url = self.base_url.format(f'd/{beatmapset_id}')
        return await self._request('GET', url)

    async def get_beatmap_background(self, beatmap_id: int) -> BytesIO:
        url = self.base_url.format(f'media/background/{beatmap_id}')
        return await self._request('GET', url)
