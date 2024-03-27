from __future__ import annotations

from typing import Literal, TYPE_CHECKING

from aiosu.helpers import add_param
from aiosu.models import Gamemode

from osu.api import BaseClient
from osu.api.models.user import OsutrackUser

if TYPE_CHECKING:
    from typing import Any

HistoryRequestType = Literal['hiscores', 'stats_history']


# add validation
class OsutrackClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://osutrack-api.ameo.dev/{}'

    async def update_user(self, user_id: int, **kwargs):
        url = self.base_url.format('update')
        params: dict[str, object] = {
            'user': user_id,
            'mode': Gamemode(kwargs.pop('gamemode', Gamemode.STANDARD)).id
        }
        json = await self._request('POST', url, params=params)
        return OsutrackUser.model_validate(json)

    async def get_user_best_rank_and_accuracy(self, user_id: int, **kwargs):
        url = self.base_url.format('peak')
        params: dict[str, object] = {
            'user': user_id,
            'mode': Gamemode(kwargs.pop('gamemode', Gamemode.STANDARD)).id
        }
        json = await self._request('GET', url, params=params)
        return json

    async def _get_type_history(
            self,
            user_id: int,
            request_type: HistoryRequestType,
            **kwargs: Any,
    ):
        if request_type not in HistoryRequestType:
            raise ValueError(
                f'"{request_type}" is not a valid request_type. Valid options are: {HistoryRequestType = }',
            )
        url = self.base_url.format(request_type)
        params: dict[str, object] = {
            'user': user_id,
            'mode': Gamemode(kwargs.pop('gamemode', Gamemode.STANDARD)).id
        }
        add_param(params, kwargs, key="date_start", param_name='from')
        add_param(params, kwargs, key="date_end", param_name='to')
        json = await self._request("GET", url, params=params)
        return json

    async def get_user_stat_updates(self, user_id: int, **kwargs):
        return await self._get_type_history(user_id, 'stats_history', **kwargs)

    async def get_user_best_scores(self, user_id: int, **kwargs):
        return await self._get_type_history(user_id, 'hiscores', **kwargs)

    async def get_mode_best_scores(self, **kwargs):
        url = self.base_url.format('bestplays')
        params: dict[str, object] = {
            'mode': Gamemode(kwargs.pop('gamemode', Gamemode.STANDARD)).id
        }
        add_param(params, kwargs, key="date_start", param_name='from')
        add_param(params, kwargs, key="date_end", param_name='to')
        add_param(params, kwargs, key="limit ", converter=lambda x: int(x))
        json = await self._request("GET", url, params=params)
        return json
