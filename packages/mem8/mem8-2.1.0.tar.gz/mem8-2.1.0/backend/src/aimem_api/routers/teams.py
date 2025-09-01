"""Teams router."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.team import Team, TeamMember
from ..schemas.team import (
    TeamCreate,
    TeamResponse,
    TeamUpdate,
    TeamMemberResponse,
    TeamRole,
)

router = APIRouter()


@router.get("/teams/", response_model=List[TeamResponse])
async def list_teams(
    include_members: bool = False,
    db: AsyncSession = Depends(get_db),
) -> List[TeamResponse]:
    """List all teams."""
    
    query = select(Team).where(Team.is_active == True)
    
    if include_members:
        query = query.options(
            selectinload(Team.members).selectinload(TeamMember.user)
        )
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    return teams


@router.post("/teams/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Create a new team."""
    
    # Check if slug already exists
    existing_team_result = await db.execute(
        select(Team).where(Team.slug == team_data.slug)
    )
    existing_team = existing_team_result.scalar_one_or_none()
    
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this slug already exists"
        )
    
    # Create team
    team = Team(
        name=team_data.name,
        description=team_data.description,
        slug=team_data.slug,
        is_active=team_data.is_active,
    )
    
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    return team


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: uuid.UUID,
    include_members: bool = False,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Get a specific team by ID."""
    
    query = select(Team).where(Team.id == team_id)
    
    if include_members:
        query = query.options(
            selectinload(Team.members).selectinload(TeamMember.user)
        )
    
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: uuid.UUID,
    team_update: TeamUpdate,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Update a specific team."""
    
    # Get existing team
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Update fields
    update_data = team_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(team, field, value)
    
    await db.commit()
    await db.refresh(team)
    
    return team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific team (soft delete)."""
    
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Soft delete
    team.is_active = False
    await db.commit()


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[TeamMemberResponse]:
    """List all members of a team."""
    
    # Verify team exists
    team_result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = team_result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get team members
    members_result = await db.execute(
        select(TeamMember)
        .where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.is_active == True
            )
        )
        .options(selectinload(TeamMember.user))
    )
    members = members_result.scalars().all()
    
    return members


@router.post("/teams/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    role: TeamRole = TeamRole.MEMBER,
    db: AsyncSession = Depends(get_db),
) -> TeamMemberResponse:
    """Add a member to a team."""
    
    # Verify team exists
    team_result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = team_result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is already a member
    existing_member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
        )
    )
    existing_member = existing_member_result.scalar_one_or_none()
    
    if existing_member:
        if existing_member.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this team"
            )
        else:
            # Reactivate existing membership
            existing_member.is_active = True
            existing_member.role = role
            await db.commit()
            await db.refresh(existing_member)
            return existing_member
    
    # Create new membership
    team_member = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=role,
        is_active=True,
    )
    
    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)
    
    return team_member


@router.put("/teams/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    role: TeamRole,
    db: AsyncSession = Depends(get_db),
) -> TeamMemberResponse:
    """Update a team member's role."""
    
    # Get team member
    result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        )
    )
    team_member = result.scalar_one_or_none()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Update role
    team_member.role = role
    await db.commit()
    await db.refresh(team_member)
    
    return team_member


@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a member from a team."""
    
    # Get team member
    result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        )
    )
    team_member = result.scalar_one_or_none()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Soft delete
    team_member.is_active = False
    await db.commit()


@router.get("/teams/slug/{slug}", response_model=TeamResponse)
async def get_team_by_slug(
    slug: str,
    include_members: bool = False,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Get a team by its slug."""
    
    query = select(Team).where(
        and_(
            Team.slug == slug,
            Team.is_active == True
        )
    )
    
    if include_members:
        query = query.options(
            selectinload(Team.members).selectinload(TeamMember.user)
        )
    
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team