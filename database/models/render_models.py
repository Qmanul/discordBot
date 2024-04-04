from sqlalchemy.orm import mapped_column, Mapped

from . import Base


class RenderedScoreModel(Base):
    __tablename__ = 'rendered_scores'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    render_url: Mapped[str] = mapped_column(unique=True)
