from aiosu.models import Gamemode

from osu.api import BaseClient


class OsutrackClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://osutrack-api.ameo.dev/{}'

    async def update_user(self, user_id: int, **kwargs):
        url = self.base_url.format('update')
        params: [str, object] = {
            'user': user_id,
            'mode': Gamemode(kwargs.pop('gamemode', Gamemode.STANDARD)).id
        }
        json = await self._request('POST', url, params=params)
        return json  # Create model and validate

    async def get_user_stat_updates(self):
        ...

    async def get_user_best_scores(self):
        ...

    async def get_user_best_rank_and_accuracy(self):
        ...

    async def get_best_scores(self):
        ...
