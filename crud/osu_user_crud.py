from database.models import OsuUserModel
from . import select, AsyncSession, update_model


async def get_user(db_session: AsyncSession, discord_id: int) -> OsuUserModel:
    return await db_session.scalar(select(OsuUserModel).where(OsuUserModel.discord_id == discord_id))


async def update_or_create_user(db_session: AsyncSession, discord_id: int, **kwargs) -> OsuUserModel:
    if db_user := await get_user(db_session, discord_id):
        db_user.osu_username = kwargs.pop('osu_username', db_user.osu_username)
        db_user.osu_user_id = kwargs.pop('osu_user_id', db_user.osu_user_id)
        db_user.osu_gamemode = kwargs.pop('osu_gamemode', db_user.osu_gamemode)
    else:
        db_user = OsuUserModel(osu_username=kwargs.pop('osu_username', None), discord_id=discord_id,
                               osu_user_id=kwargs.pop('osu_user_id', None), osu_gamemode=kwargs.pop('osu_gamemode', 0))

    return await update_model(db_session, db_user)
