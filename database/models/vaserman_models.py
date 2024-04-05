from . import Base, mapped_column, Mapped


class VasermanUserScoreModel(Base):
    __tablename__ = 'vaserman_user_score'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    score: Mapped[int] = mapped_column()
