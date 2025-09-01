"""Thought schemas."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ThoughtBase(BaseModel):
    """Base thought schema."""
    
    title: str = Field(..., min_length=1, max_length=500, description="Thought title")
    content: str = Field(..., min_length=1, description="Thought content")
    path: str = Field(..., min_length=1, max_length=1000, description="File path")
    thought_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    is_published: bool = Field(default=True, description="Is published")
    is_archived: bool = Field(default=False, description="Is archived")


class ThoughtCreate(ThoughtBase):
    """Schema for creating a thought."""
    
    team_id: uuid.UUID = Field(..., description="Team ID")


class ThoughtUpdate(BaseModel):
    """Schema for updating a thought."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    path: Optional[str] = Field(None, min_length=1, max_length=1000)
    thought_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_archived: Optional[bool] = None


class ThoughtResponse(ThoughtBase):
    """Schema for thought response."""
    
    id: uuid.UUID
    team_id: uuid.UUID
    content_hash: Optional[str]
    word_count: Optional[int]
    git_commit_hash: Optional[str]
    git_branch: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ThoughtListResponse(BaseModel):
    """Schema for paginated thought list response."""
    
    thoughts: List[ThoughtResponse]
    total: int
    page: int
    page_size: int
    total_pages: int