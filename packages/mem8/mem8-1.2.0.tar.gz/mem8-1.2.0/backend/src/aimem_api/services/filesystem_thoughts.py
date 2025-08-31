"""Filesystem-based thoughts service."""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


def extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from markdown content or filename."""
    lines = content.strip().split('\n')
    
    # Look for first heading
    for line in lines:
        if line.startswith('#'):
            return line.lstrip('#').strip()
    
    # Fallback to filename without extension
    return filename.replace('-', ' ').replace('_', ' ').title()


def extract_tags_from_content(content: str, path: Path) -> List[str]:
    """Extract tags from content and path."""
    tags = []
    
    # Add path-based tags
    path_parts = path.parts
    if 'shared' in path_parts:
        tags.append('shared')
    if 'research' in path_parts:
        tags.append('research')
    if 'plans' in path_parts:
        tags.append('plans')
    if 'prs' in path_parts:
        tags.append('prs')
    if 'notes' in path_parts:
        tags.append('notes')
    
    # Look for YAML frontmatter tags
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx > 0:
            frontmatter = content[3:end_idx]
            for line in frontmatter.split('\n'):
                if line.strip().startswith('tags:'):
                    tags_str = line.split(':', 1)[1].strip()
                    # Handle both array and string formats
                    if tags_str.startswith('[') and tags_str.endswith(']'):
                        tags_str = tags_str[1:-1]
                    tags.extend([tag.strip().strip('"\'') for tag in tags_str.split(',')])
    
    return [tag for tag in tags if tag]


def scan_thoughts_directory(thoughts_dir: Path) -> List[Dict[str, Any]]:
    """Scan thoughts directory and return list of thought objects."""
    if not thoughts_dir.exists():
        return []
    
    thoughts = []
    
    for md_file in thoughts_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Get file stats
            stat = md_file.stat()
            
            # Extract metadata
            title = extract_title_from_content(content, md_file.stem)
            tags = extract_tags_from_content(content, md_file.relative_to(thoughts_dir))
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Determine source type
            source_type = "local"
            if "shared" in str(md_file):
                source_type = "shared"
            
            thought = {
                "id": content_hash[:12],  # Use content hash as ID
                "title": title,
                "content": content,
                "path": str(md_file.relative_to(thoughts_dir.parent)),
                "content_hash": content_hash,
                "word_count": len(content.split()),
                "tags": tags,
                "source_type": source_type,
                "is_published": True,
                "is_archived": False,
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "updated_at": datetime.fromtimestamp(stat.st_mtime),
                "file_path": str(md_file),
            }
            
            thoughts.append(thought)
            
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue
    
    # Sort by last modified
    thoughts.sort(key=lambda x: x["updated_at"], reverse=True)
    return thoughts


def discover_worktree_thoughts(base_dir: Path) -> List[Dict[str, Any]]:
    """Discover thoughts from git worktrees and other repositories."""
    all_thoughts = []
    
    # Look for thoughts in current directory
    thoughts_dir = base_dir / "thoughts"
    if thoughts_dir.exists():
        current_thoughts = scan_thoughts_directory(thoughts_dir)
        for thought in current_thoughts:
            thought["repository"] = base_dir.name
        all_thoughts.extend(current_thoughts)
    
    # Look for thoughts in sibling directories (other repos)
    parent_dir = base_dir.parent
    if parent_dir.exists():
        for repo_dir in parent_dir.iterdir():
            if not repo_dir.is_dir() or repo_dir.name.startswith('.'):
                continue
            if repo_dir == base_dir:
                continue
                
            repo_thoughts_dir = repo_dir / "thoughts"
            if repo_thoughts_dir.exists():
                repo_thoughts = scan_thoughts_directory(repo_thoughts_dir)
                for thought in repo_thoughts:
                    thought["repository"] = repo_dir.name
                    thought["source_type"] = "worktree"
                all_thoughts.extend(repo_thoughts)
    
    return all_thoughts


def get_filesystem_thoughts(
    base_path: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None,
    repository: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get thoughts from filesystem with optional filtering."""
    
    if base_path:
        base_dir = Path(base_path)
    else:
        # Look for the main project directory (go up from backend)
        base_dir = Path.cwd()
        if base_dir.name == "backend":
            base_dir = base_dir.parent
    
    # Discover all thoughts
    thoughts = discover_worktree_thoughts(base_dir)
    
    # Apply filters
    if search:
        search_lower = search.lower()
        thoughts = [
            t for t in thoughts 
            if search_lower in t["title"].lower() or search_lower in t["content"].lower()
        ]
    
    if tags:
        thoughts = [
            t for t in thoughts 
            if any(tag in t["tags"] for tag in tags)
        ]
    
    if repository:
        thoughts = [
            t for t in thoughts 
            if t.get("repository", "").lower() == repository.lower()
        ]
    
    return thoughts[:limit]