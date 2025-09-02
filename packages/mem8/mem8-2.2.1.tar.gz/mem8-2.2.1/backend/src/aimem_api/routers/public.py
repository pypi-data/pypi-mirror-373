"""Public API endpoints that don't require authentication."""

from typing import List, Optional
from fastapi import APIRouter, Query

from ..services.filesystem_thoughts import get_filesystem_thoughts

router = APIRouter()


@router.get("/thoughts/local")
async def list_local_thoughts(
    search: Optional[str] = Query(None, description="Search in title and content"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of thoughts to return"),
):
    """List thoughts directly from local filesystem (no authentication required)."""
    
    thoughts = get_filesystem_thoughts(
        search=search,
        tags=tags,
        repository=repository,
        limit=limit
    )
    
    from pathlib import Path
    current_dir = Path.cwd()
    parent_dir = current_dir.parent if current_dir.name == "backend" else current_dir
    
    return {
        "thoughts": thoughts,
        "total": len(thoughts),
        "source": "local-filesystem",
        "repositories_found": list(set(t.get("repository", "unknown") for t in thoughts)),
        "debug_info": {
            "current_working_directory": str(current_dir),
            "search_directory": str(parent_dir),
            "thoughts_directory_exists": (parent_dir / "thoughts").exists(),
            "thoughts_directory_contents": list(str(p) for p in (parent_dir / "thoughts").iterdir()) if (parent_dir / "thoughts").exists() else [],
            "hot_reload_test": "working_after_restart"
        }
    }