from datetime import datetime

from pydantic import Field

from . import BaseModel


class RippleDifficulty(BaseModel):
    std: float
    taiko: float
    ctb: float
    mania: float


class RippleBeatmap(BaseModel):
    id: int = Field(alias='beatmap_id')
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


class GatariBeatmap(BaseModel):
    ar: float
    artist: str
    id: int = Field(alias='beatmap_id')
    beatmap_md5: str
    beatmapset_id: int
    bpm: int
    creator: str
    difficulty: float
    max_combo: int = Field(alias='fc')
    hit_length: int
    od: float
    ranked: int
    ranked_status_frozen: int
    song_name: str
    title: str
    version: str
