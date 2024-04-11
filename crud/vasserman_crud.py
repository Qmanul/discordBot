from typing import Sequence

from sqlalchemy import and_

from crud import select, AsyncSession, update_model, delete_model
from database.models import VassermanUserScoreModel


async def get_user(db_session: AsyncSession, user_id: int, guild_id: int) -> VassermanUserScoreModel:
    return await db_session.scalar(
        select(VassermanUserScoreModel).filter(and_(VassermanUserScoreModel.user_id == user_id,
                                                    VassermanUserScoreModel.guild_id == guild_id)))


async def get_users(db_session: AsyncSession, guild_id: int) -> Sequence[VassermanUserScoreModel]:
    return (await db_session.execute(
        select(VassermanUserScoreModel).filter(and_(VassermanUserScoreModel.guild_id == guild_id,
                                                    VassermanUserScoreModel.score > 0)))).unique().scalars().all()


async def insert_user(db_session: AsyncSession, user_id: int, guild_id: int, **kwargs) -> VassermanUserScoreModel:
    if (score := kwargs.pop('score', 0)) < 0:
        raise ValueError
    return await update_model(db_session, VassermanUserScoreModel(user_id=user_id, guild_id=guild_id, score=score))


async def update_user(db_session: AsyncSession, user: VassermanUserScoreModel, **kwargs) -> VassermanUserScoreModel:
    if (score := kwargs.pop('score')) < 0:
        raise ValueError
    user.score = score
    return await update_model(db_session, user)


async def change_score(db_session: AsyncSession, user_id: int, guild_id: int, score: int) -> VassermanUserScoreModel:
    if user := await get_user(db_session, user_id, guild_id):
        return await update_user(db_session, user, score=(score + user.score))
    return await insert_user(db_session, user_id, guild_id, score=score)


async def delete_user(db_session: AsyncSession, user: VassermanUserScoreModel):
    await delete_model(db_session, user)
    await db_session.commit()
