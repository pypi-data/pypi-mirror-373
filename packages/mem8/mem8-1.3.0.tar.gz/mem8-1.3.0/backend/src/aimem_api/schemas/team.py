"""Team schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TeamRole(str, Enum):
    """Team member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member" 
    VIEWER = "viewer"


class TeamBase(BaseModel):
    """Base team schema."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    slug: str = Field(..., min_length=1, max_length=100, description="Team slug")
    is_active: bool = Field(default=True, description="Is active")


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""
    
    id: uuid.UUID
    user_id: uuid.UUID
    role: TeamRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    """Schema for team response."""
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: Optional[List[TeamMemberResponse]] = None
    
    class Config:
        from_attributes = True