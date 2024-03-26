from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class OsuUserModel(Base):
    __tablename__ = "osu_users"

    discord_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True, )
    osu_user_id: Mapped[int] = mapped_column(nullable=True)
    osu_username: Mapped[str] = mapped_column(index=True, nullable=True)
    osu_gamemode: Mapped[int] = mapped_column(nullable=True)
