"""Search schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """Search types. Semantic search is experimental."""
    FULLTEXT = "fulltext"
    SEMANTIC = "semantic"


class SearchQuery(BaseModel):
    """Search query schema."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    search_type: SearchType = Field(
        default=SearchType.FULLTEXT,
        description="Search type (semantic search is experimental)",
    )
    team_id: Optional[uuid.UUID] = Field(None, description="Team ID to filter by")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags to filter by")
    path_filter: Optional[str] = Field(None, description="Path filter pattern")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class SearchResult(BaseModel):
    """Search result schema."""
    
    id: uuid.UUID
    title: str
    content_excerpt: str
    path: str
    score: float = Field(..., description="Relevance score")
    team_id: uuid.UUID
    thought_metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response schema."""
    
    results: List[SearchResult]
    total: int
    query: str
    search_type: SearchType
    took_ms: float = Field(..., description="Search execution time in milliseconds")
