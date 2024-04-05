from crud import get_model_by_id, AsyncSession, update_model
from database.models import VasermanUserScoreModel


async def get_user(db_session: AsyncSession, user_id: int) -> VasermanUserScoreModel:
    return await get_model_by_id(db_session, user_id, VasermanUserScoreModel)


async def insert_user(db_session: AsyncSession, user_id: int, **kwargs) -> VasermanUserScoreModel:
    return await update_model(db_session, VasermanUserScoreModel(id=user_id, score=kwargs.pop('score', 0)))


async def update_user(db_session: AsyncSession, user: VasermanUserScoreModel, **kwargs) -> VasermanUserScoreModel:
    user.score = kwargs.pop('score', user.score)
    return await update_model(db_session, user)


async def upsert_user(db_session: AsyncSession, user_id: int, **kwargs) -> VasermanUserScoreModel:
    if user := await get_user(db_session, user_id):
        return await update_user(db_session, user, **kwargs)

    return await insert_user(db_session, user_id, **kwargs)
