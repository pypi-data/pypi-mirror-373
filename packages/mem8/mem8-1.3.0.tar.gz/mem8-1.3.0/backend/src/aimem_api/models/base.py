"""Base model mixins."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from ..database_types import UuidType


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class UUIDMixin:
    """Mixin for UUID primary key."""
    
    @declared_attr
    def id(cls) -> Mapped[str]:
        return mapped_column(
            UuidType,
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            nullable=False
        )


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )# Force reload
