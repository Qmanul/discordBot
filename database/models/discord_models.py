from . import Base, mapped_column, Mapped


class DiscordGuildModel(Base):
    __tablename__ = 'discord_guilds'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)


class DiscrodUserModel(Base):
    __tablename__ = 'discord_users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
