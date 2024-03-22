from datetime import datetime

from aiosu.models import BaseModel
from pydantic import Field

from osu.api.models.beatmap import GatariBeatmap, RippleBeatmap
from osu.api.models.user import RippleUser


class GatariScore(BaseModel):
    accuracy: float
    beatmap: GatariBeatmap
    comments_count: int
    completed: int
    count_300: int
    count_100: int
    count_50: int
    count_geki: int = Field(alias='count_gekis')
    count_katu: int
    count_miss: int
    full_combo: bool
    id: int
    isfav: bool
    max_combo: int
    mods: int
    play_mode: int
    pp: float
    ranking: str
    score: int
    time: datetime
    verified: bool
    views: int


class RippleScore(BaseModel):
    id: int
    beatmap_md5: str
    score: int
    max_combo: int
    full_combo: int
    mods: int
    count_300: int
    count_100: int
    count_50: int
    count_geki: int
    count_katu: int
    count_miss: int
    time: datetime
    play_mode: int
    accuracy: float
    pp: float
    rank: str
    completed: int


class RippleScoreBeatmap(RippleScore):
    user: RippleUser


class RippleScoreUser(RippleScore):
    beatmap: RippleBeatmap
