from __future__ import annotations

import aiosu.models
import rosu_pp_py

from osu.api.models.score import RippleScoreUser, GatariScore


async def get_score_performance(
        filepath,
        score: aiosu.models.Score | RippleScoreUser | GatariScore
) -> tuple[float, float]:
    beatmap = rosu_pp_py.Beatmap(path=filepath)
    statistics = await get_score_statistics(score)

    calc = rosu_pp_py.Calculator(**statistics)
    pp = calc.performance(beatmap).pp

    fc_statistics = statistics
    fc_statistics.update({
        'n300': statistics['n300'] + statistics['n_misses'],
        'n_misses': 0,
    })
    fc_statistics.pop('combo')

    calc = rosu_pp_py.Calculator(**fc_statistics)
    fc_pp = calc.performance(beatmap).pp

    return pp, fc_pp


async def get_score_calc(filepath, score):
    beatmap = rosu_pp_py.Beatmap(path=filepath)
    statistics = await get_score_statistics(score)

    return rosu_pp_py.Calculator(**statistics).performance(beatmap)


async def get_score_statistics(
        score: aiosu.models.Score | RippleScoreUser | GatariScore
) -> dict[str, int]:
    statistics = {}

    if isinstance(score, aiosu.models.Score):
        statistics.update({
            'n_geki': score.statistics.count_geki,
            'n_katu': score.statistics.count_katu,
            'n300': score.statistics.count_300,
            'n100': score.statistics.count_100,
            'n50': score.statistics.count_50,
            'n_misses': score.statistics.count_miss,
            'mods': score.mods.bitwise,
            'mode': score.mode.id,
        })

    else:
        statistics.update({
            'n_geki': score.count_geki,
            'n_katu': score.count_katu,
            'n300': score.count_300,
            'n100': score.count_100,
            'n50': score.count_50,
            'n_misses': score.count_miss,
            'mods': score.mods,
            'mode': score.play_mode,
        })

    statistics['acc'] = score.accuracy
    statistics['combo'] = score.max_combo
    return statistics
