from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from . import BaseModel

AVATAR_URL_BASE = "https://a.ripple.moe/{}"


class RippleUser(BaseModel):
    code: int
    id: int
    username: str
    username_aka: str
    registered_on: datetime
    privileges: int
    latest_activity: datetime
    country: str


class RippleModeStats(BaseModel):
    ranked_score: int
    total_score: int
    playcount: int
    play_time: int
    replays_watched: int
    total_hits: int
    level: float
    accuracy: float
    pp: float
    global_leaderboard_rank: Optional[int]
    country_leaderboard_rank: Optional[int]


class RippleBadge(BaseModel):
    id: int
    name: str
    icon: str


class RippleSilenceInfo(BaseModel):
    reason: str
    end: datetime


class RippleUserFull(RippleUser):
    play_style: int
    favourite_mode: int
    favourite_relax: int
    badges: Optional[List[RippleBadge]]
    custom_badge: Optional[RippleBadge]
    std: RippleModeStats
    taiko: RippleModeStats
    ctb: RippleModeStats
    mania: RippleModeStats
    silence_info: RippleSilenceInfo


class GatariUser(BaseModel):
    a_count: int
    avg_accuracy: float
    avg_accuracy_ap: float
    avg_accuracy_rx: float
    avg_hits_play: float
    country_rank: int
    country_rank_ap: int
    country_rank_rx: int
    id: int
    level: int
    level_progress: int
    max_combo: int
    playcount: int
    playtime: int
    pp: int
    pp_4k: int
    pp_7k: int
    pp_ap: int | None
    pp_rx: int | None
    rank: int
    rank_ap: int
    rank_rx: int
    ranked_score: int
    replays_watched: int
    s_count: int
    sh_count: int
    total_hits: int
    total_score: int
    x_count: int
    xh_count: int
