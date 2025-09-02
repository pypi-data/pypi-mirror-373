"""Thought entity data model for semantic understanding of thoughts."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class ThoughtEntity:
    """Represents a thought as a semantic entity with lifecycle awareness."""
    path: Path
    content: str
    metadata: Dict[str, Any]
    type: str
    scope: str  # 'personal', 'shared', 'team', 'cross-repo'
    lifecycle_state: str
    relationships: List[Dict[str, Any]]
    quality_score: float
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'ThoughtEntity':
        """Create ThoughtEntity from markdown file."""
        content = file_path.read_text(encoding='utf-8')
        
        # Parse YAML frontmatter
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                yaml_content = content[4:yaml_end]
                try:
                    metadata = yaml.safe_load(yaml_content) or {}
                except yaml.YAMLError:
                    metadata = {}
                content_body = content[yaml_end + 3:].strip()
            else:
                metadata = {}
                content_body = content
        else:
            metadata = {}
            content_body = content
            
        return cls(
            path=file_path,
            content=content_body,
            metadata=metadata,
            type=cls._classify_type(file_path, metadata, content_body),
            scope=cls._determine_scope(file_path),
            lifecycle_state=cls._analyze_lifecycle(metadata, content_body),
            relationships=cls._extract_relationships(content_body),
            quality_score=cls._calculate_quality(metadata, content_body)
        )
    
    @staticmethod
    def _classify_type(path: Path, metadata: Dict, content: str) -> str:
        """Classify thought type based on path and content."""
        path_parts = path.parts
        if 'plans' in path_parts:
            return 'plan'
        elif 'research' in path_parts:
            return 'research'
        elif 'prs' in path_parts:
            return 'pr_discussion'
        elif 'tickets' in path_parts:
            return 'ticket'
        elif 'decisions' in path_parts:
            return 'decision'
        
        # Fallback to metadata or content analysis
        if metadata.get('tags'):
            for tag in metadata['tags']:
                if tag in ['plan', 'research', 'ticket', 'decision']:
                    return tag
        
        return 'unknown'
    
    @staticmethod 
    def _determine_scope(path: Path) -> str:
        """Determine sharing scope from file path."""
        path_parts = path.parts
        if 'shared' in path_parts:
            return 'shared'
        elif any(user in path_parts for user in ['vaski', 'allison', 'thoughts']):
            return 'personal' 
        else:
            return 'unknown'
            
    @staticmethod
    def _analyze_lifecycle(metadata: Dict, content: str) -> str:
        """Analyze lifecycle state from metadata and content."""
        status = metadata.get('status', '').lower()
        if status in ['complete', 'completed', 'done']:
            return 'completed'
        elif status in ['active', 'in_progress', 'in-progress']:
            return 'active'
        elif status in ['obsolete', 'deprecated', 'stale']:
            return 'obsolete'
        elif status in ['draft', 'wip', 'work-in-progress']:
            return 'draft'
        
        # Content-based analysis
        if '✅' in content and 'success criteria' in content.lower():
            return 'potentially_complete'
        elif '❌' in content or 'failed' in content.lower():
            return 'failed'
            
        return 'unknown'
    
    @staticmethod
    def _extract_relationships(content: str) -> List[Dict[str, Any]]:
        """Extract relationships from content."""
        relationships = []
        
        # Simple implementation - look for references to other files
        import re
        
        # Look for markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for link_text, link_url in md_links:
            if link_url.endswith('.md'):
                relationships.append({
                    'type': 'references',
                    'target': link_url,
                    'description': link_text,
                    'confidence': 0.8
                })
        
        # Look for @ mentions (like @thoughts/shared/...)
        at_mentions = re.findall(r'@([a-zA-Z0-9/_-]+)', content)
        for mention in at_mentions:
            relationships.append({
                'type': 'mentions',
                'target': mention,
                'description': f'References {mention}',
                'confidence': 0.6
            })
        
        return relationships
    
    @staticmethod
    def _calculate_quality(metadata: Dict, content: str) -> float:
        """Calculate quality score for the thought entity."""
        score = 0.0
        
        # Has metadata
        if metadata:
            score += 0.2
            
        # Has tags
        if metadata.get('tags'):
            score += 0.1
            
        # Has status
        if metadata.get('status'):
            score += 0.1
            
        # Content length (reasonable length gets higher score)
        content_length = len(content.strip())
        if content_length > 100:
            score += 0.2
        if content_length > 500:
            score += 0.2
            
        # Has structured content (headings)
        if content.count('#') > 0:
            score += 0.1
            
        # Has checkboxes (task lists)
        if '- [' in content:
            score += 0.1
            
        return min(1.0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'path': str(self.path),
            'type': self.type,
            'scope': self.scope,
            'lifecycle_state': self.lifecycle_state,
            'metadata': self.metadata,
            'relationships': self.relationships,
            'quality_score': self.quality_score,
        }