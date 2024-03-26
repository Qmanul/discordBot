from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def update_model(db_session: AsyncSession, model):
    db_session.add(model)
    await db_session.commit()
    return model


async def get_model_by_id(db_session: AsyncSession, id: int, model):
    return await db_session.scalar(select(model).where(model.id == id))
