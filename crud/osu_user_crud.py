from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base_crud import update_model
from database.models import OsuUserModel as UserDBModel


async def get_user(db_session: AsyncSession, discord_id: int) -> UserDBModel:
    return await db_session.scalar(select(UserDBModel).where(UserDBModel.discord_id == discord_id))


async def update_or_create_user(db_session: AsyncSession, discord_id: int, **kwargs) -> UserDBModel:
    if db_user := await get_user(db_session, discord_id):
        db_user.osu_username = kwargs.pop('osu_username', db_user.osu_username)
        db_user.osu_user_id = kwargs.pop('osu_user_id', db_user.osu_user_id)
        db_user.osu_gamemode = kwargs.pop('osu_gamemode', db_user.osu_gamemode)
    else:
        db_user = UserDBModel(osu_username=kwargs.pop('osu_username', None), discord_id=discord_id,
                              osu_user_id=kwargs.pop('osu_user_id', None), osu_gamemode=kwargs.pop('osu_gamemode', 0))

    return await update_model(db_session, db_user)
