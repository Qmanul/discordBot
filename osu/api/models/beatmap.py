from datetime import datetime
from . import BaseModel
from .user import RippleUser


class RippleDifficulty(BaseModel):
    std: float
    taiko: float
    ctb: float
    mania: float


class RippleBeatmap(BaseModel):
    beatmap_id: int
    beatmapset_id: int
    beatmap_md5: str
    song_name: str
    ar: float
    od: float
    difficulty: float
    difficulty2: RippleDifficulty
    max_combo: int
    hit_length: int
    ranked: int
    ranked_status_frozen: int
    latest_update: datetime


class RippleBeatmapUserMostPlayed(BaseModel):
    beatmap: RippleBeatmap
    playcount: int


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
