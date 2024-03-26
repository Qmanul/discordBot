from __future__ import annotations

import aiosu.models
from aiosu.models import Gamemode
from discord import Embed

from osu.api.models.score import RippleScoreUser, GatariScore
from osu.api.models.user import RippleUserFull, GatariUser, OsutrackNewHiscore


# В пизду я не собираюсь прописывать эмбеды


async def bancho_user(user_info: aiosu.models.User, **kwargs) -> Embed:
    return Embed(title=f'{user_info.username}', description=f'{kwargs.pop("server")}')


async def ripple_user(user_info: RippleUserFull, **kwargs) -> Embed:
    return Embed(title=f'{user_info.username}', description=f'{kwargs.pop("server")}')


async def gatari_user(user_info: GatariUser, **kwargs) -> Embed:
    return Embed(title=f'{user_info.user_info.username}', description=f'{kwargs.pop("server")}')


async def bancho_score(score_info: aiosu.models.Score, **kwargs) -> Embed:
    return Embed(
        title=f'{score_info.beatmapset.title}', description=f'{kwargs.pop("server")}'
    ).add_field(
        name='fc_pp', value=kwargs.pop('fc_pp')
    )


async def ripple_score(score_info: RippleScoreUser, **kwargs) -> Embed:
    return Embed(title=f'{score_info.beatmap.song_name}', description=f'{kwargs.pop("server")}')


async def gatari_score(score_info: GatariScore, **kwargs) -> Embed:
    return Embed(title=f'{score_info.beatmap.title}', description=f'{kwargs.pop("server")}')


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


async def create_user_info_embed(user_info: aiosu.models.User | RippleUserFull, **kwargs) -> Embed:
    return await user_action_map[type(user_info)](user_info, **kwargs)


async def create_score_embed(score_info: aiosu.models.Score | RippleScoreUser, **kwargs) -> Embed:
    return await score_action_map[type(score_info)](score_info, **kwargs)


async def create_new_hiscore_embed(score: OsutrackNewHiscore, user_info: dict) -> Embed:
    embed = Embed(timestamp=score.date)
    embed.set_author(
        name=f'New #{score.ranking + 1} for {user_info["username"]} in {Gamemode(user_info["mode"]).name_full}',
        url=f'https://osu.ppy.sh/users/{score.user_id}',
        icon_url=f'https://a.ppy.sh/{score.user_id}')

    embed.add_field(name=f'{score.pp:.2f}pp', value=f'{score.rank}')
    return embed
