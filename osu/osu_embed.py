from __future__ import annotations

import aiosu.models
import discord

from osu.api.models.score import RippleScoreUser, GatariScore
from osu.api.models.user import RippleUserFull, GatariUser


# В пизду я не собираюсь прописывать эмбеды


async def bancho_user(user_info: aiosu.models.User, **kwargs) -> discord.Embed:
    return discord.Embed(title=f'{user_info.username}', description=f'{kwargs.pop("server")}')


async def ripple_user(user_info: RippleUserFull, **kwargs) -> discord.Embed:
    return discord.Embed(title=f'{user_info.username}', description=f'{kwargs.pop("server")}')


async def gatari_user(user_info: GatariUser, **kwargs) -> discord.Embed:
    return discord.Embed(title=f'{user_info.user_info.username}', description=f'{kwargs.pop("server")}')


async def bancho_score(score_info: aiosu.models.Score, **kwargs) -> discord.Embed:
    return discord.Embed(
        title=f'{score_info.beatmapset.title}', description=f'{kwargs.pop("server")}'
    ).add_field(
        name='fc_pp', value=kwargs.pop('fc_pp')
    )


async def ripple_score(score_info: RippleScoreUser, **kwargs) -> discord.Embed:
    return discord.Embed(title=f'{score_info.beatmap.song_name}', description=f'{kwargs.pop("server")}')


async def gatari_score(score_info: GatariScore, **kwargs) -> discord.Embed:
    return discord.Embed(title=f'{score_info.beatmap.title}', description=f'{kwargs.pop("server")}')


user_action_map = {
    aiosu.models.User: bancho_user,
    RippleUserFull: ripple_user,
    GatariUser: gatari_user,
}

score_action_map = {
    aiosu.models.Score: bancho_score,
    RippleScoreUser: ripple_score,
    GatariScore: gatari_score
}


async def create_user_info_embed(user_info: aiosu.models.User | RippleUserFull, **kwargs) -> discord.Embed:
    return await user_action_map[type(user_info)](user_info, **kwargs)


async def create_score_embed(score_info: aiosu.models.Score | RippleScoreUser, **kwargs) -> discord.Embed:
    return await score_action_map[type(score_info)](score_info, **kwargs)
