"""Health check router."""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.thought import Thought
from ..models.team import Team

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mem8-api",
        "version": "0.1.0"
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check with database connectivity."""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_healthy = result.scalar() == 1
        
        return {
            "status": "ready" if db_healthy else "not ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "healthy" if db_healthy else "unhealthy"
            }
        }
    except Exception as e:
        return {
            "status": "not ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": f"unhealthy: {str(e)}"
            }
        }


@router.get("/system/stats", response_model=Dict[str, Any])
async def system_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get system statistics."""
    try:
        # Get total thoughts count
        thoughts_result = await db.execute(select(func.count(Thought.id)))
        total_thoughts = thoughts_result.scalar()
        
        # Get active teams count  
        teams_result = await db.execute(
            select(func.count(Team.id)).where(Team.is_active == True)
        )
        active_teams = teams_result.scalar()
        
        return {
            "totalThoughts": total_thoughts,
            "activeTeams": active_teams,
            # Not yet implemented: return nulls instead of magic numbers
            "syncStatus": None,
            "memoryUsage": None,
        }
    except Exception as e:
        # Prefer explicit error over fabricated fallback values
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"stats_unavailable: {str(e)}")
