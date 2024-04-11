from sqlalchemy import BigInteger, Table, Column, ForeignKey
from sqlalchemy.orm import relationship

from . import Base, mapped_column, Mapped

user_channel = Table(
    "user_channel",
    Base.metadata,
    Column("channel_id", ForeignKey("tracked_channels.id", ondelete='CASCADE'), ),
    Column("user_id", ForeignKey("tracked_users.id", ), ),
)


class TrackedChannelModel(Base):
    __tablename__ = 'tracked_channels'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    pp_cutoff: Mapped[int] = mapped_column()
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)


class TrackedUserModel(Base):
    __tablename__ = 'tracked_users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True, )
    osu_user_id: Mapped[int] = mapped_column(nullable=True)
    osu_gamemode: Mapped[int] = mapped_column(nullable=True)
    tracked_channels: Mapped[list[TrackedChannelModel]] = relationship(secondary=user_channel, lazy='joined')
