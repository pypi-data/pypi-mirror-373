"""
Audit mixin for ORM models.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID


class AuditMixin:
    """
    Comprehensive audit mixin with all common fields.
    
    Provides:
    - UUID primary key
    - UTC timestamps (created_at_utc, updated_at_utc)
    - Soft delete functionality (is_deleted, deleted_at_utc)
    - User audit fields (created_by, updated_by, deleted_by)
    """

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False
    )

    created_at_utc: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    updated_at_utc: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    deleted_at_utc: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        index=True
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
