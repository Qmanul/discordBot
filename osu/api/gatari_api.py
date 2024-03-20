from __future__ import annotations

from osu.api.base_api import BaseClient


class GatariClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.gatari.pw'
