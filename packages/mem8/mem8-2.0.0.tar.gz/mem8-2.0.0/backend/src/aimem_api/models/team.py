"""Team models."""

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .base import TimestampMixin, UUIDMixin
from ..database_types import UuidType


class TeamRole(str, Enum):
    """Team member roles."""
    OWNER = "owner"
    ADMIN = "admin" 
    MEMBER = "member"
    VIEWER = "viewer"


class Team(Base, UUIDMixin, TimestampMixin):
    """Team model."""
    
    __tablename__ = "teams"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    thoughts = relationship(
        "Thought",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class TeamMember(Base, UUIDMixin, TimestampMixin):
    """Team membership model."""
    
    __tablename__ = "team_members"
    
    team_id: Mapped[uuid.UUID] = mapped_column(
        UuidType,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UuidType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[TeamRole] = mapped_column(default=TeamRole.MEMBER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")
    
    def __repr__(self) -> str:
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"