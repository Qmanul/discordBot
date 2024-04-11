from sqlalchemy import BigInteger

from . import Base, mapped_column, Mapped


class VassermanUserScoreModel(Base):
    __tablename__ = 'vasserman_user_score'

    # TODO: у одного пользователя могут быть очки на разных серверах
    # это пиздец какое кривое решение нужен подход лучше
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    score: Mapped[int] = mapped_column()
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
