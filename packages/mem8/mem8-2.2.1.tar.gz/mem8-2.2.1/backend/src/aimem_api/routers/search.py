"""Search router."""

import time
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.thought import Thought
from ..schemas.search import SearchQuery, SearchResponse, SearchResult, SearchType
from ..services.search import SearchService

router = APIRouter()


@router.post("/search/", response_model=SearchResponse)
async def search_thoughts(
    search_query: SearchQuery,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Search thoughts using fulltext or experimental semantic search."""
    
    start_time = time.time()
    
    if search_query.search_type == SearchType.SEMANTIC:
        # Use semantic search service
        search_service = SearchService()
        results = await search_service.semantic_search(
            query=search_query.query,
            team_id=search_query.team_id,
            tags=search_query.tags,
            path_filter=search_query.path_filter,
            limit=search_query.limit,
            offset=search_query.offset,
            db=db,
        )
    else:
        # Use fulltext search
        results = await _fulltext_search(search_query, db)
    
    # Calculate execution time
    took_ms = (time.time() - start_time) * 1000
    
    return SearchResponse(
        results=results,
        total=len(results),  # TODO: Implement proper total counting
        query=search_query.query,
        search_type=search_query.search_type,
        took_ms=took_ms,
    )


async def _fulltext_search(
    search_query: SearchQuery,
    db: AsyncSession,
) -> list[SearchResult]:
    """Perform fulltext search using PostgreSQL."""
    
    # Build base query
    query = select(Thought).where(
        Thought.is_published == True,
        Thought.is_archived == False,
    )
    
    # Apply team filter
    if search_query.team_id:
        query = query.where(Thought.team_id == search_query.team_id)
    
    # Apply tag filters
    if search_query.tags:
        tag_filters = []
        for tag in search_query.tags:
            tag_filters.append(Thought.tags.contains([tag]))
        query = query.where(and_(*tag_filters))
    
    # Apply path filter
    if search_query.path_filter:
        query = query.where(Thought.path.ilike(f"%{search_query.path_filter}%"))
    
    # Apply text search
    search_terms = search_query.query.strip()
    if search_terms:
        # Simple text search in title and content
        text_filter = or_(
            Thought.title.ilike(f"%{search_terms}%"),
            Thought.content.ilike(f"%{search_terms}%")
        )
        query = query.where(text_filter)
    
    # Apply pagination
    query = query.offset(search_query.offset).limit(search_query.limit)
    
    # Execute query
    result = await db.execute(query)
    thoughts = result.scalars().all()
    
    # Convert to search results
    search_results = []
    for thought in thoughts:
        # Generate excerpt
        excerpt = _generate_excerpt(thought.content, search_query.query)
        
        # Calculate simple relevance score
        score = _calculate_relevance_score(thought, search_query.query)
        
        search_result = SearchResult(
            id=thought.id,
            title=thought.title,
            content_excerpt=excerpt,
            path=thought.path,
            score=score,
            team_id=thought.team_id,
            thought_metadata=thought.thought_metadata or {},
            tags=thought.tags or [],
            created_at=thought.created_at,
            updated_at=thought.updated_at,
        )
        search_results.append(search_result)
    
    # Sort by score descending
    search_results.sort(key=lambda x: x.score, reverse=True)
    
    return search_results


def _generate_excerpt(content: str, query: str, max_length: int = 200) -> str:
    """Generate an excerpt from content highlighting the search query."""
    
    if not query.strip():
        return content[:max_length] + ("..." if len(content) > max_length else "")
    
    query_lower = query.lower()
    content_lower = content.lower()
    
    # Find the first occurrence of any query term
    query_terms = query_lower.split()
    best_position = -1
    
    for term in query_terms:
        position = content_lower.find(term)
        if position != -1:
            if best_position == -1 or position < best_position:
                best_position = position
    
    if best_position == -1:
        # No query terms found, return beginning
        return content[:max_length] + ("..." if len(content) > max_length else "")
    
    # Calculate excerpt boundaries
    start = max(0, best_position - max_length // 3)
    end = min(len(content), start + max_length)
    
    excerpt = content[start:end]
    
    # Add ellipsis if needed
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(content):
        excerpt = excerpt + "..."
    
    return excerpt


def _calculate_relevance_score(thought: Thought, query: str) -> float:
    """Calculate a simple relevance score for fulltext search."""
    
    if not query.strip():
        return 0.0
    
    query_lower = query.lower()
    title_lower = thought.title.lower()
    content_lower = thought.content.lower()
    
    score = 0.0
    query_terms = query_lower.split()
    
    for term in query_terms:
        # Title matches are weighted higher
        title_matches = title_lower.count(term)
        content_matches = content_lower.count(term)
        
        score += title_matches * 2.0  # Title matches worth more
        score += content_matches * 1.0
    
    # Normalize by content length (prefer shorter, more focused content)
    if thought.word_count and thought.word_count > 0:
        score = score / (thought.word_count / 100.0)  # Normalize to per-100-words
    
    return score


@router.get("/search/suggestions/", response_model=list[str])
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    team_id: Optional[str] = Query(None, description="Team ID to filter by"),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """Get search suggestions based on partial query."""
    
    # Simple implementation: return frequent terms from titles
    query_filter = Thought.title.ilike(f"%{query}%")
    
    if team_id:
        query_filter = and_(query_filter, Thought.team_id == team_id)
    
    result = await db.execute(
        select(Thought.title)
        .where(
            query_filter,
            Thought.is_published == True,
            Thought.is_archived == False,
        )
        .limit(limit)
    )
    
    titles = result.scalars().all()
    
    # Extract unique words that start with the query
    suggestions = set()
    query_lower = query.lower()
    
    for title in titles:
        words = title.lower().split()
        for word in words:
            if word.startswith(query_lower) and len(word) > len(query):
                suggestions.add(word)
    
    return sorted(list(suggestions))[:limit]