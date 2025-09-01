"""Thought model."""

import uuid
from typing import Dict, Optional, Any

from sqlalchemy import ForeignKey, Index, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import event
from sqlalchemy.engine import Engine

from ..database import Base
from .base import TimestampMixin, UUIDMixin
from ..database_types import JsonType, UuidType


class Thought(Base, UUIDMixin, TimestampMixin):
    """Thought model for storing AI memory content."""
    
    __tablename__ = "thoughts"
    
    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    
    # Organization
    team_id: Mapped[uuid.UUID] = mapped_column(
        UuidType,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Metadata and search
    thought_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JsonType, default=dict)
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JsonType, default=list)
    
    # Content analysis
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    word_count: Mapped[Optional[int]] = mapped_column(default=0)
    
    # Git integration
    git_commit_hash: Mapped[Optional[str]] = mapped_column(String(40))
    git_branch: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Status
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="thoughts")
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_thoughts_team_path", "team_id", "path"),
        Index("ix_thoughts_team_title", "team_id", "title"),
        Index("ix_thoughts_content_hash", "content_hash"),
        Index("ix_thoughts_published_team", "is_published", "team_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Thought(id={self.id}, title='{self.title[:50]}...', team_id={self.team_id})>"
    
    @property
    def excerpt(self) -> str:
        """Get content excerpt for display."""
        if len(self.content) <= 200:
            return self.content
        return self.content[:197] + "..."