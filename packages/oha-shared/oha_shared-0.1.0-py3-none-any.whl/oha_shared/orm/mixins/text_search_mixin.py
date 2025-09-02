from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TSVECTOR


class TextSearchMixin:
    """Mixin to add full-text search capabilities for PostgreSQL."""

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        nullable=True,
        index=True
    )
