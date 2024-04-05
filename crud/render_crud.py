from database.models import RenderedScoreModel
from . import AsyncSession, update_model, get_model_by_id


async def get_render(db_session: AsyncSession, score_id: int) -> RenderedScoreModel:
    return await get_model_by_id(db_session, score_id, RenderedScoreModel)


async def insert_render(db_session: AsyncSession, score_id: int, render_url: str):
    render = RenderedScoreModel(id=score_id, render_url=render_url)
    return await update_model(db_session, render)
