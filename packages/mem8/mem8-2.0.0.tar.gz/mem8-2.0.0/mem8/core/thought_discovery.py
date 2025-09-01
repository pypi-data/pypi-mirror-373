"""Thought discovery service for indexing and finding thought entities."""

import time
from pathlib import Path
from typing import Dict, List, Optional
from .config import Config
from .thought_entity import ThoughtEntity


class ThoughtDiscoveryService:
    """Discovers and indexes thought entities across repositories."""
    
    def __init__(self, config: Config):
        self.config = config
        self._entity_cache = {}
        self._last_scan = None
        self._cache_ttl = 300  # 5 minutes
        
    def discover_all_thoughts(self, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Discover all thought entities across all configured repositories."""
        if not force_rescan and self._entity_cache and self._is_cache_fresh():
            return list(self._entity_cache.values())
            
        entities = []
        
        # Scan local thoughts
        thoughts_dir = self.config.thoughts_dir
        if thoughts_dir and thoughts_dir.exists():
            entities.extend(self._scan_directory(thoughts_dir))
            
        # Scan cross-repository thoughts  
        discovered_repos = self._discover_repositories()
        for repo_path in discovered_repos:
            repo_thoughts_dir = repo_path / 'thoughts'
            if repo_thoughts_dir.exists():
                entities.extend(self._scan_directory(repo_thoughts_dir, repo_name=repo_path.name))
        
        # Update cache
        self._entity_cache = {str(entity.path): entity for entity in entities}
        self._last_scan = time.time()
        
        return entities
    
    def _is_cache_fresh(self) -> bool:
        """Check if entity cache is still fresh."""
        if not self._last_scan:
            return False
        return (time.time() - self._last_scan) < self._cache_ttl
        
    def _scan_directory(self, directory: Path, repo_name: str = None) -> List[ThoughtEntity]:
        """Scan directory for thought files."""
        entities = []
        for md_file in directory.rglob("*.md"):
            if md_file.is_file() and not self._should_skip_file(md_file):
                try:
                    entity = ThoughtEntity.from_file(md_file)
                    if repo_name:
                        entity.metadata['repository'] = repo_name
                    entities.append(entity)
                except Exception as e:
                    # Log error but continue scanning
                    print(f"Warning: Could not parse {md_file}: {e}")
                    continue
        return entities
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scanning."""
        skip_patterns = [
            '.git/',
            'node_modules/',
            '__pycache__/',
            '.venv/',
            'venv/',
            '.pytest_cache/'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _discover_repositories(self) -> List[Path]:
        """Discover repositories that might contain thoughts."""
        repos = []
        
        # Check configured shared directory
        if self.config.shared_dir and self.config.shared_dir.exists():
            parent_dir = self.config.shared_dir.parent
            if parent_dir.exists():
                # Look for sibling directories that might be repos
                for item in parent_dir.iterdir():
                    if item.is_dir() and (item / '.git').exists():
                        repos.append(item)
        
        # Check parent directory of current workspace
        workspace_parent = self.config.workspace_dir.parent
        if workspace_parent.exists():
            for item in workspace_parent.iterdir():
                if item.is_dir() and (item / '.git').exists() and item != self.config.workspace_dir:
                    repos.append(item)
                    
        return repos
    
    def find_by_type(self, thought_type: str, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Find thoughts by semantic type."""
        entities = self.discover_all_thoughts(force_rescan)
        return [e for e in entities if e.type == thought_type]
        
    def find_by_status(self, status: str, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Find thoughts by lifecycle status."""
        entities = self.discover_all_thoughts(force_rescan)
        return [e for e in entities if e.lifecycle_state == status]
    
    def find_by_scope(self, scope: str, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Find thoughts by sharing scope."""
        entities = self.discover_all_thoughts(force_rescan)
        return [e for e in entities if e.scope == scope]
    
    def find_by_path_pattern(self, pattern: str, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Find thoughts matching path pattern."""
        entities = self.discover_all_thoughts(force_rescan)
        return [e for e in entities if pattern.lower() in str(e.path).lower()]
    
    def get_statistics(self, force_rescan: bool = False) -> Dict[str, any]:
        """Get statistics about discovered thoughts."""
        entities = self.discover_all_thoughts(force_rescan)
        
        stats = {
            'total_thoughts': len(entities),
            'by_type': {},
            'by_scope': {},
            'by_status': {},
            'by_repository': {},
            'quality_distribution': {
                'high': 0,  # > 0.7
                'medium': 0,  # 0.4 - 0.7
                'low': 0  # < 0.4
            }
        }
        
        for entity in entities:
            # Count by type
            stats['by_type'][entity.type] = stats['by_type'].get(entity.type, 0) + 1
            
            # Count by scope
            stats['by_scope'][entity.scope] = stats['by_scope'].get(entity.scope, 0) + 1
            
            # Count by status
            stats['by_status'][entity.lifecycle_state] = stats['by_status'].get(entity.lifecycle_state, 0) + 1
            
            # Count by repository
            repo = entity.metadata.get('repository', 'local')
            stats['by_repository'][repo] = stats['by_repository'].get(repo, 0) + 1
            
            # Quality distribution
            if entity.quality_score > 0.7:
                stats['quality_distribution']['high'] += 1
            elif entity.quality_score > 0.4:
                stats['quality_distribution']['medium'] += 1
            else:
                stats['quality_distribution']['low'] += 1
        
        return stats
    
    def clear_cache(self):
        """Clear the entity cache to force fresh discovery."""
        self._entity_cache = {}
        self._last_scan = None