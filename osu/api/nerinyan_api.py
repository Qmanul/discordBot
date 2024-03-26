from io import BytesIO

from . import BaseClient


class NerinyanClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.nerinyan.moe/{}}'

    async def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/octet-stream",
        }

    async def download_beatmapset(self, beatmapset_id: int, **kwargs) -> BytesIO:
        url = self.base_url.format(f'd/{beatmapset_id}')
        params: [str, object] = {
            'nh': kwargs.pop('no_hitsound', True),
            'nsb': kwargs.pop('no_storyboard', True),
            'nb': kwargs.pop('no_background', True),
            'nv': kwargs.pop('no_video', True),
        }
        return await self._request('GET', url, params=params)

    async def get_beatmap_background(self, beatmap_id: int) -> BytesIO:
        url = self.base_url.format(f'bg/{beatmap_id}')
        return await self._request('GET', url)
