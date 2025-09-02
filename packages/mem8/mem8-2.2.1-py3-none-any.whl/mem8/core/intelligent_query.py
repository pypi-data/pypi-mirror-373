"""Intelligent query processing with natural language understanding."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from .thought_entity import ThoughtEntity
from .thought_discovery import ThoughtDiscoveryService


@dataclass
class QueryIntent:
    """Represents parsed intent from natural language query."""
    query_type: str  # 'find', 'list', 'show'
    target_type: Optional[str] = None  # 'plans', 'research', etc.
    status_filter: Optional[str] = None  # 'completed', 'active', etc. 
    scope_filter: Optional[str] = None  # 'shared', 'personal', etc.
    content_query: Optional[str] = None  # Actual search terms
    time_filter: Optional[str] = None  # 'older than 30d', 'recent', etc.
    relationship_filter: Optional[str] = None  # 'related to X', 'implements Y'


class IntelligentQueryEngine:
    """Processes natural language queries with semantic understanding."""
    
    # Intent pattern matching
    PATTERNS = {
        'completed_plans': r'completed?\s+plans?',
        'active_research': r'active|current|ongoing.*research',
        'stale_content': r'stale|old|outdated|obsolete', 
        'recent_content': r'recent|new|latest',
        'time_bounded': r'(older|newer)\s+than\s+(\d+)\s*(d|days?|w|weeks?|m|months?)',
        'type_specific': r'(plans?|research|tickets?|prs?|decisions?)',
        'scope_specific': r'(shared|personal|team)',
        'status_specific': r'(completed?|active|draft|failed|obsolete)',
    }
    
    def __init__(self, thought_discovery: ThoughtDiscoveryService):
        self.thought_discovery = thought_discovery
        
    def parse_query(self, query: str) -> QueryIntent:
        """Parse natural language query into structured intent."""
        query_lower = query.lower().strip()
        
        intent = QueryIntent(query_type='find')  # Default
        
        # Extract type filter
        for pattern_type, pattern in self.PATTERNS.items():
            match = re.search(pattern, query_lower)
            if match:
                if pattern_type == 'type_specific':
                    intent.target_type = match.group(1).rstrip('s')  # normalize plural
                elif pattern_type == 'status_specific':
                    intent.status_filter = match.group(1).rstrip('d')  # normalize past tense
                elif pattern_type == 'scope_specific':
                    intent.scope_filter = match.group(1)
                elif pattern_type == 'time_bounded':
                    intent.time_filter = f"{match.group(2)}{match.group(3)[0]}"  # "30d"
                elif pattern_type in ['completed_plans', 'active_research']:
                    # Combined patterns
                    if 'completed' in pattern_type:
                        intent.target_type = 'plan'
                        intent.status_filter = 'completed'
                    elif 'active' in pattern_type:
                        intent.target_type = 'research'
                        intent.status_filter = 'active'
        
        # Extract content query (remove matched patterns)
        content_query = query
        for pattern in self.PATTERNS.values():
            content_query = re.sub(pattern, '', content_query, flags=re.IGNORECASE)
        intent.content_query = content_query.strip()
        
        return intent
        
    def execute_query(self, intent: QueryIntent) -> List[ThoughtEntity]:
        """Execute parsed query intent against thought entities."""
        entities = self.thought_discovery.discover_all_thoughts()
        
        results = entities
        
        # Apply type filter
        if intent.target_type:
            results = [e for e in results if e.type == intent.target_type]
            
        # Apply status filter  
        if intent.status_filter:
            results = [e for e in results if e.lifecycle_state == intent.status_filter]
            
        # Apply scope filter
        if intent.scope_filter:
            results = [e for e in results if e.scope == intent.scope_filter]
            
        # Apply content filter
        if intent.content_query and intent.content_query.strip():
            content_results = []
            query_terms = intent.content_query.lower().split()
            for entity in results:
                # Search in title, content, and metadata
                searchable_text = (
                    entity.content.lower() + ' ' + 
                    str(entity.metadata.get('topic', '')).lower() + ' ' +
                    ' '.join(entity.metadata.get('tags', [])).lower()
                )
                
                # Simple term matching (can be enhanced with fuzzy matching)
                if any(term in searchable_text for term in query_terms):
                    content_results.append(entity)
                    
            results = content_results
        
        # Apply time filter (simplified implementation)
        if intent.time_filter:
            # Implementation would parse time filter and apply date comparisons
            pass
            
        return results
    
    def find_similar_thoughts(self, entity: ThoughtEntity, limit: int = 5) -> List[ThoughtEntity]:
        """Find thoughts similar to the given entity."""
        all_entities = self.thought_discovery.discover_all_thoughts()
        
        # Remove the entity itself
        candidates = [e for e in all_entities if e.path != entity.path]
        
        scored_entities = []
        for candidate in candidates:
            similarity_score = self._calculate_similarity(entity, candidate)
            if similarity_score > 0.2:  # Threshold for similarity
                scored_entities.append((candidate, similarity_score))
        
        # Sort by similarity score
        scored_entities.sort(key=lambda x: x[1], reverse=True)
        
        return [entity for entity, score in scored_entities[:limit]]
    
    def _calculate_similarity(self, entity1: ThoughtEntity, entity2: ThoughtEntity) -> float:
        """Calculate similarity score between two thought entities."""
        score = 0.0
        
        # Type similarity
        if entity1.type == entity2.type:
            score += 0.3
        
        # Scope similarity
        if entity1.scope == entity2.scope:
            score += 0.1
        
        # Tag similarity
        tags1 = set(entity1.metadata.get('tags', []))
        tags2 = set(entity2.metadata.get('tags', []))
        if tags1 and tags2:
            tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
            score += tag_overlap * 0.2
        
        # Content similarity (simple word overlap)
        words1 = set(entity1.content.lower().split())
        words2 = set(entity2.content.lower().split())
        if words1 and words2:
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            words1 = words1 - stop_words
            words2 = words2 - stop_words
            
            if words1 and words2:
                word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                score += word_overlap * 0.4
        
        return min(1.0, score)
    
    def get_related_thoughts(self, query: str, limit: int = 10) -> Dict[str, List[ThoughtEntity]]:
        """Get thoughts related to query, grouped by relationship type."""
        intent = self.parse_query(query)
        results = self.execute_query(intent)
        
        # Group results by type and status
        grouped_results = {
            'direct_matches': results[:limit],
            'related_plans': [],
            'related_research': [],
            'related_decisions': []
        }
        
        # Find related thoughts based on content similarity
        for result in results[:3]:  # Limit to avoid too many API calls
            similar = self.find_similar_thoughts(result, limit=3)
            for similar_entity in similar:
                if similar_entity.type == 'plan' and similar_entity not in grouped_results['related_plans']:
                    grouped_results['related_plans'].append(similar_entity)
                elif similar_entity.type == 'research' and similar_entity not in grouped_results['related_research']:
                    grouped_results['related_research'].append(similar_entity)
                elif similar_entity.type == 'decision' and similar_entity not in grouped_results['related_decisions']:
                    grouped_results['related_decisions'].append(similar_entity)
        
        return grouped_results
    
    def suggest_actions(self, entities: List[ThoughtEntity]) -> List[Dict[str, str]]:
        """Suggest actions based on found entities."""
        suggestions = []
        
        if not entities:
            return suggestions
        
        # Analyze the entities to suggest actions
        completed_count = sum(1 for e in entities if e.lifecycle_state == 'completed')
        obsolete_count = sum(1 for e in entities if e.lifecycle_state == 'obsolete')
        draft_count = sum(1 for e in entities if e.lifecycle_state == 'draft')
        
        if completed_count > 0:
            suggestions.append({
                'action': 'archive',
                'description': f'Archive {completed_count} completed thoughts',
                'confidence': 'high'
            })
        
        if obsolete_count > 0:
            suggestions.append({
                'action': 'delete',
                'description': f'Delete {obsolete_count} obsolete thoughts',
                'confidence': 'medium'
            })
        
        if draft_count > 2:
            suggestions.append({
                'action': 'review',
                'description': f'Review {draft_count} draft thoughts for completion',
                'confidence': 'low'
            })
        
        return suggestions