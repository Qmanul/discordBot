from . import Base, mapped_column, Mapped


class RenderedScoreModel(Base):
    __tablename__ = 'rendered_scores'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    render_url: Mapped[str] = mapped_column(unique=True)
