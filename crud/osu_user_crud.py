from models import OsuUserModel as UserDBModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user(db_session: AsyncSession, discord_id: int) -> UserDBModel:
    user = (await db_session.scalar(select(UserDBModel).where(UserDBModel.discord_id == discord_id)))
    return user


async def update_user(db_session: AsyncSession, user: UserDBModel) -> None:
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)


async def update_or_create_user(db_session: AsyncSession, discord_id: int, **kwargs) -> None:
    db_user = await get_user(db_session, discord_id=discord_id)
    try:
        db_user.osu_username = kwargs.pop('osu_username', db_user.osu_username)
        db_user.osu_user_id = kwargs.pop('osu_user_id', db_user.osu_username)
        db_user.osu_gamemode = kwargs.pop('osu_gamemode', db_user.osu_gamemode)
    except AttributeError:
        db_user = UserDBModel(osu_username=kwargs.pop('osu_username'), discord_id=discord_id,
                              osu_user_id=kwargs.pop('osu_user_id'), osu_gamemode=kwargs.pop('osu_gamemode', 0))

    await update_user(db_session, db_user)
