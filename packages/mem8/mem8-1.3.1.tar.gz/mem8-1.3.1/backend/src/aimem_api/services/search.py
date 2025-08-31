"""Search service with semantic capabilities."""

import uuid
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.thought import Thought
from ..schemas.search import SearchResult


class SearchService:
    """Service for advanced search capabilities."""
    
    def __init__(self):
        self._embeddings_model = None
    
    async def semantic_search(
        self,
        query: str,
        team_id: Optional[uuid.UUID] = None,
        tags: Optional[List[str]] = None,
        path_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None,
    ) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        
        # For now, fallback to simple text search
        # TODO: Implement proper semantic search with embeddings
        return await self._fallback_text_search(
            query=query,
            team_id=team_id,
            tags=tags,
            path_filter=path_filter,
            limit=limit,
            offset=offset,
            db=db,
        )
    
    async def _fallback_text_search(
        self,
        query: str,
        team_id: Optional[uuid.UUID] = None,
        tags: Optional[List[str]] = None,
        path_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None,
    ) -> List[SearchResult]:
        """Fallback text search implementation."""
        
        # Build query
        db_query = db.query(Thought).filter(
            Thought.is_published == True,
            Thought.is_archived == False,
        )
        
        # Apply filters
        if team_id:
            db_query = db_query.filter(Thought.team_id == team_id)
        
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(Thought.tags.contains([tag]))
            db_query = db_query.filter(and_(*tag_filters))
        
        if path_filter:
            db_query = db_query.filter(Thought.path.ilike(f"%{path_filter}%"))
        
        # Apply text search
        if query.strip():
            from sqlalchemy import or_
            text_filter = or_(
                Thought.title.ilike(f"%{query}%"),
                Thought.content.ilike(f"%{query}%")
            )
            db_query = db_query.filter(text_filter)
        
        # Apply pagination
        db_query = db_query.offset(offset).limit(limit)
        
        # Execute
        result = await db.execute(db_query)
        thoughts = result.scalars().all()
        
        # Convert to search results
        search_results = []
        for thought in thoughts:
            excerpt = self._generate_excerpt(thought.content, query)
            score = self._calculate_score(thought, query)
            
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
        
        # Sort by score
        search_results.sort(key=lambda x: x.score, reverse=True)
        
        return search_results
    
    def _generate_excerpt(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate content excerpt highlighting query terms."""
        
        if not query.strip():
            return content[:max_length] + ("..." if len(content) > max_length else "")
        
        # Find best position to start excerpt
        query_lower = query.lower()
        content_lower = content.lower()
        
        best_pos = content_lower.find(query_lower)
        if best_pos == -1:
            # Try individual terms
            terms = query_lower.split()
            for term in terms:
                pos = content_lower.find(term)
                if pos != -1:
                    best_pos = pos
                    break
        
        if best_pos == -1:
            best_pos = 0
        
        # Calculate excerpt boundaries
        start = max(0, best_pos - max_length // 3)
        end = min(len(content), start + max_length)
        
        excerpt = content[start:end]
        
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def _calculate_score(self, thought: Thought, query: str) -> float:
        """Calculate relevance score."""
        
        if not query.strip():
            return 0.0
        
        query_lower = query.lower()
        title_lower = thought.title.lower()
        content_lower = thought.content.lower()
        
        score = 0.0
        
        # Exact query match
        if query_lower in title_lower:
            score += 10.0
        if query_lower in content_lower:
            score += 5.0
        
        # Individual term matches
        terms = query_lower.split()
        for term in terms:
            if term in title_lower:
                score += 3.0
            if term in content_lower:
                score += 1.0
        
        # Normalize by word count
        if thought.word_count and thought.word_count > 0:
            score = score / (thought.word_count / 100.0)
        
        return score