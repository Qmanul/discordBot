from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from . import BaseModel


class OsutrackNewHiscore(BaseModel):
    beatmap_id: int
    score_id: int
    score: int
    maxcombo: int
    count50: int
    count100: int
    count300: int
    countmiss: int
    countkatu: int
    countgeki: int
    perfect: int
    enabled_mods: int
    is_classic: int
    user_id: int
    date: datetime
    rank: str
    pp: float
    replay_available: int
    ranking: int


class OsutrackUser(BaseModel):
    username: str
    mode: int
    playcount: int
    pp_rank: int
    pp_raw: float
    accuracy: float
    total_score: int
    ranked_score: int
    count300: int
    count50: int
    count100: int
    level: float
    count_rank_a: int
    count_rank_s: int
    count_rank_ss: int
    levelup: bool
    first: bool
    _exists: bool
    newhs: List[OsutrackNewHiscore]


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


class GatariUserInfo(BaseModel):
    abbr: None
    clanid: int | None
    country: str
    favourite_mode: int
    followers_count: int
    id: int
    latest_activity: datetime
    play_style: int
    privileges: int
    registered_on: datetime
    username: str
    username_aka: str


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
    pp_ap: int
    pp_rx: int
    rank: int | None
    rank_ap: int | None
    rank_rx: int | None
    ranked_score: int
    replays_watched: int
    s_count: int
    sh_count: int
    total_hits: int
    total_score: int
    x_count: int
    xh_count: int
    user_info: GatariUserInfo
