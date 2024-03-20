from pydantic import BaseModel


class OsuUserSchema(BaseModel):
    discord_id: int
    osu_user_id: int
    osu_username: str
    osu_gamemode: int
