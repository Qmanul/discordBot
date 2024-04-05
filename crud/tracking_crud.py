from typing import Sequence

from sqlalchemy.exc import IntegrityError

from database.models import TrackedUserModel, TrackedChannelModel, TrackedGuildModel
from . import select, AsyncSession, update_model, get_model_by_id, delete_model_by_id


async def register_user(db_session: AsyncSession, user_id, channel_id, **kwargs) -> None:
    if not (channel := await get_channel(db_session, channel_id)):
        raise ValueError

    await create_or_update_user(db_session, user_id, channels=[channel], **kwargs)


# ------ user part ------
async def get_users(db_session: AsyncSession) -> Sequence[TrackedUserModel]:
    return (await db_session.execute(select(TrackedUserModel))).unique().scalars().all()


async def get_user(db_session: AsyncSession, user_id: int) -> TrackedUserModel:
    return await get_model_by_id(db_session, user_id, TrackedUserModel)


async def create_or_update_user(db_session: AsyncSession, user_id: int, **kwargs) -> TrackedUserModel:
    if user := await get_user(db_session, user_id):
        user.osu_user_id = kwargs.pop('osu_user_id', user.osu_user_id)
        user.osu_gamemode = kwargs.pop('osu_gamemode', user.osu_gamemode)
    else:
        user = TrackedUserModel(id=user_id, osu_user_id=kwargs.pop('osu_user_id', None),
                                osu_gamemode=kwargs.pop('osu_gamemode', None), )

    if channels := kwargs.pop('channels', []):
        user.tracked_channels.append(*channels)

    return await update_model(db_session, user)


# ------ channel part ------
async def get_channel(db_session: AsyncSession, channel_id: int, ) -> TrackedChannelModel:
    return await get_model_by_id(db_session, channel_id, TrackedChannelModel)


async def insert_channel(db_session: AsyncSession, channel_id: int, guild_id: int, **kwargs) -> TrackedChannelModel:
    channel = TrackedChannelModel(id=channel_id, pp_cutoff=kwargs.pop('pp_cutoff', 0), guild_id=guild_id)

    try:
        return await update_model(db_session, channel)
    except IntegrityError:
        # this shouldn't happen in the first place, but oh well
        await db_session.rollback()
        guild = TrackedGuildModel(id=guild_id)
        await update_model(db_session, guild)
        return await update_model(db_session, channel)


async def create_or_update_channel(db_session: AsyncSession, channel_id: int, **kwargs) -> TrackedChannelModel:
    if channel := await get_channel(db_session, channel_id):
        channel.pp_cutoff = kwargs.pop('pp_cutoff', channel.pp_cutoff)
    else:
        channel = TrackedChannelModel(id=channel_id, pp_cutoff=kwargs.pop('pp_cutoff', 0))

    return await update_model(db_session, channel)


async def delete_channel(db_session: AsyncSession, channel_id: int):
    await delete_model_by_id(db_session, channel_id, TrackedChannelModel)


# ------ guild part ------
async def get_guild(db_session: AsyncSession, guild_id: int) -> TrackedGuildModel:
    return await get_model_by_id(db_session, guild_id, TrackedGuildModel)


async def insert_guild(db_session: AsyncSession, guild_id: int) -> TrackedGuildModel:
    guild = TrackedGuildModel(id=guild_id)
    return await update_model(db_session, guild)


async def delete_guild(db_session: AsyncSession, guild_id: int):
    await delete_model_by_id(db_session, guild_id, TrackedGuildModel)
