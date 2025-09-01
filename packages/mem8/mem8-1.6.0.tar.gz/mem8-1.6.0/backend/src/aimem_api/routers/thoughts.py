"""Thoughts router."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.thought import Thought
from ..models.user import User
from ..schemas.thought import (
    ThoughtCreate,
    ThoughtListResponse,
    ThoughtResponse,
    ThoughtUpdate,
)
from .auth import get_current_user, get_current_user_or_local
from ..services.filesystem_thoughts import get_filesystem_thoughts

router = APIRouter()


@router.get("/thoughts/", response_model=ThoughtListResponse)
async def list_thoughts(
    team_id: Optional[uuid.UUID] = Query(None, description="Filter by team ID"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archived status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user_or_local),
    db: AsyncSession = Depends(get_db),
) -> ThoughtListResponse:
    """List thoughts with filtering and pagination."""
    
    # Build query
    query = select(Thought)
    
    # Apply filters
    filters = []
    if team_id:
        filters.append(Thought.team_id == team_id)
    if is_published is not None:
        filters.append(Thought.is_published == is_published)
    if is_archived is not None:
        filters.append(Thought.is_archived == is_archived)
    if tags:
        # Filter by tags (PostgreSQL array contains)
        for tag in tags:
            filters.append(Thought.tags.contains([tag]))
    if search:
        # Search in title and content
        search_filter = or_(
            Thought.title.ilike(f"%{search}%"),
            Thought.content.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(func.count(Thought.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    thoughts = result.scalars().all()
    
    # Calculate pagination info
    total_pages = (total + page_size - 1) // page_size
    
    return ThoughtListResponse(
        thoughts=thoughts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/thoughts/", response_model=ThoughtResponse, status_code=status.HTTP_201_CREATED)
async def create_thought(
    thought_data: ThoughtCreate,
    current_user: User = Depends(get_current_user_or_local),
    db: AsyncSession = Depends(get_db),
) -> ThoughtResponse:
    """Create a new thought."""
    
    # Calculate word count
    word_count = len(thought_data.content.split())
    
    # Create thought
    thought = Thought(
        title=thought_data.title,
        content=thought_data.content,
        path=thought_data.path,
        team_id=thought_data.team_id,
        thought_metadata=thought_data.thought_metadata or {},
        tags=thought_data.tags or [],
        is_published=thought_data.is_published,
        is_archived=thought_data.is_archived,
        word_count=word_count,
    )
    
    # Generate content hash
    import hashlib
    content_hash = hashlib.sha256(thought_data.content.encode()).hexdigest()
    thought.content_hash = content_hash
    
    db.add(thought)
    await db.commit()
    await db.refresh(thought)
    
    return thought


@router.get("/thoughts/from-filesystem")
async def list_filesystem_thoughts(
    search: Optional[str] = Query(None, description="Search in title and content"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of thoughts to return"),
):
    """List thoughts directly from filesystem (including worktrees)."""
    
    thoughts = get_filesystem_thoughts(
        search=search,
        tags=tags,
        repository=repository,
        limit=limit
    )
    
    return {
        "thoughts": thoughts,
        "total": len(thoughts),
        "source": "filesystem",
        "repositories_found": list(set(t.get("repository", "unknown") for t in thoughts))
    }


@router.get("/thoughts/test-no-auth")
async def test_no_auth():
    """Test endpoint without authentication."""
    return {"message": "This works without auth", "thoughts_found": 0}


@router.get("/thoughts/{thought_id}", response_model=ThoughtResponse)
async def get_thought(
    thought_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ThoughtResponse:
    """Get a specific thought by ID."""
    
    result = await db.execute(
        select(Thought).where(Thought.id == thought_id)
    )
    thought = result.scalar_one_or_none()
    
    if not thought:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thought not found"
        )
    
    return thought


@router.put("/thoughts/{thought_id}", response_model=ThoughtResponse)
async def update_thought(
    thought_id: uuid.UUID,
    thought_update: ThoughtUpdate,
    db: AsyncSession = Depends(get_db),
) -> ThoughtResponse:
    """Update a specific thought."""
    
    # Get existing thought
    result = await db.execute(
        select(Thought).where(Thought.id == thought_id)
    )
    thought = result.scalar_one_or_none()
    
    if not thought:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thought not found"
        )
    
    # Update fields
    update_data = thought_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(thought, field, value)
    
    # Recalculate word count if content changed
    if "content" in update_data:
        thought.word_count = len(thought.content.split())
        
        # Recalculate content hash
        import hashlib
        thought.content_hash = hashlib.sha256(thought.content.encode()).hexdigest()
    
    await db.commit()
    await db.refresh(thought)
    
    return thought


@router.delete("/thoughts/{thought_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thought(
    thought_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific thought."""
    
    result = await db.execute(
        select(Thought).where(Thought.id == thought_id)
    )
    thought = result.scalar_one_or_none()
    
    if not thought:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thought not found"
        )
    
    await db.delete(thought)
    await db.commit()


@router.get("/thoughts/{thought_id}/related", response_model=List[ThoughtResponse])
async def get_related_thoughts(
    thought_id: uuid.UUID,
    limit: int = Query(5, ge=1, le=20, description="Number of related thoughts"),
    db: AsyncSession = Depends(get_db),
) -> List[ThoughtResponse]:
    """Get thoughts related to the specified thought."""
    
    # Get the source thought
    result = await db.execute(
        select(Thought).where(Thought.id == thought_id)
    )
    source_thought = result.scalar_one_or_none()
    
    if not source_thought:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thought not found"
        )
    
    # Find related thoughts by shared tags and same team
    filters = [
        Thought.id != thought_id,
        Thought.team_id == source_thought.team_id,
        Thought.is_published == True,
        Thought.is_archived == False,
    ]
    
    # If source thought has tags, prioritize thoughts with shared tags
    if source_thought.tags:
        tag_filters = []
        for tag in source_thought.tags:
            tag_filters.append(Thought.tags.contains([tag]))
        
        if tag_filters:
            filters.append(or_(*tag_filters))
    
    query = select(Thought).where(and_(*filters)).limit(limit)
    
    result = await db.execute(query)
    related_thoughts = result.scalars().all()
    
    return related_thoughts
