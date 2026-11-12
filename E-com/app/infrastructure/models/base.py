"""
SQLAlchemy base model with common columns and utilities.
All database models inherit from this base.
"""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete support."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False, index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None,
    )


class TenantMixin:
    """Mixin that adds tenant_id for multi-tenancy."""

    tenant_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True,
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Abstract base model with ID, timestamps, and soft delete.
    All entity models should inherit from this.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True,
    )


class TenantBaseModel(BaseModel, TenantMixin):
    """
    Abstract base model with tenant_id for multi-tenant entities.
    """

    __abstract__ = True
