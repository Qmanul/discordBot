from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


async def update_model(db_session: AsyncSession, model):
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    return model


async def delete_model(db_session: AsyncSession, model):
    await db_session.delete(model)


async def get_model_by_id(db_session: AsyncSession, id: int, model):
    return await db_session.scalar(select(model).where(model.id == id))


async def delete_model_by_id(db_session: AsyncSession, id: int, model):
    await db_session.execute(delete(model).where(model.id == id))
    await db_session.commit()
