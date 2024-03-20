from __future__ import annotations
from datetime import datetime
from typing import List, Optional

import aiosu.models

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
