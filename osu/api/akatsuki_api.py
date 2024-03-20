from __future__ import annotations
from typing import Any
from osu.api.models.user import RippleUserFull
from osu.api.ripple_api import RippleClient
from utils.utils import process_query_type


class AkatsukiClient(RippleClient):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.base_url = "https://akatsuki.gg"
        self.authorization_header = ''
        self.relax_param_keyname = 'rx'
        self.relax = 0

    async def get_user(self, user_query: int | str, **kwargs: Any) -> RippleUserFull:
        url = f"{self.base_url}/api/v1/users/full"
        qtype = await process_query_type(user_query, kwargs)
        params: dict[str, object] = {
            qtype: user_query,
            self.relax_param_keyname: self.relax
        }
        json = await self._request("GET", url, params=params)

        json['favourite_relax'] = json['favourite_mode']  # set this shit because
        for mode in json['stats'][self.relax].values():  # change playtime to play_time
            mode['play_time'] = mode.pop('playtime')
        json = {**json['stats'][self.relax], **json}  # unpack dict of stats

        return RippleUserFull.model_validate(json)


class AkatsukiRelaxClient(AkatsukiClient):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.relax = 1
