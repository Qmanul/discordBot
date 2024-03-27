from typing import List

from sqlalchemy import BigInteger, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

user_channel = Table(
    "user_channel",
    Base.metadata,
    Column("channel_id", ForeignKey("tracked_channels.id"), ),
    Column("user_id", ForeignKey("tracked_users.id"), ),
)


class TrackedChannelModel(Base):
    __tablename__ = 'tracked_channels'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    pp_cutoff: Mapped[int] = mapped_column()
    guild_id: Mapped[int] = mapped_column(ForeignKey('tracked_guilds.id'))


class TrackedUserModel(Base):
    __tablename__ = 'tracked_users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True, )
    osu_user_id: Mapped[int] = mapped_column(nullable=True)
    osu_gamemode: Mapped[int] = mapped_column(nullable=True)
    tracked_channels: Mapped[List[TrackedChannelModel]] = relationship(secondary=user_channel, lazy='joined')


class TrackedGuildModel(Base):
    __tablename__ = 'tracked_guilds'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True, )
    tracked_channels: Mapped[List[TrackedChannelModel]] = relationship(lazy='joined')
