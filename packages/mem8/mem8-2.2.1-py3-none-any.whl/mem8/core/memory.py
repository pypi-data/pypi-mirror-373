"""Memory management functionality for mem8."""

import os
import shutil
import time
from importlib import resources
from pathlib import Path
from typing import Dict, List, Any, Optional
from cookiecutter.main import cookiecutter

from .config import Config
from .utils import (
    get_shared_directory, 
    find_claude_code_workspace,
    get_claude_memory_files,
    ensure_directory_exists,
    create_symlink,
    get_git_info
)
from .thought_entity import ThoughtEntity
from .thought_discovery import ThoughtDiscoveryService


class MemoryManager:
    """Manages AI memory workspace and shared memory integration."""
    
    def __init__(self, config: Config):
        """Initialize memory manager."""
        self.config = config
        self.thought_discovery = ThoughtDiscoveryService(config)
    
    def initialize_workspace(
        self, 
        shared_directory: Optional[Path] = None,
        template: str = "default",
        force: bool = False
    ) -> Dict[str, Any]:
        """Initialize mem8 workspace."""
        try:
            workspace_dir = self.config.workspace_dir
            
            # Determine shared directory
            if shared_directory:
                shared_dir = shared_directory
            else:
                shared_dir = self.config.shared_dir or get_shared_directory()
            
            # Check if workspace already exists
            claude_dir = workspace_dir / ".claude"
            thoughts_dir = workspace_dir / "thoughts"
            
            if (claude_dir.exists() or thoughts_dir.exists()) and not force:
                return {
                    'success': False,
                    'error': 'Workspace already exists. Use --force to reinitialize.'
                }
            
            # Create workspace structure
            result = self._create_workspace_structure(
                workspace_dir, shared_dir, template
            )
            
            if result['success']:
                # Update configuration
                self.config.set('shared.default_location', str(shared_dir))
                
                return {
                    'success': True,
                    'shared_dir': shared_dir,
                    'local_workspace': workspace_dir,
                    'template': template,
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Initialization failed: {e}"
            }
    
    def _create_workspace_structure(
        self, 
        workspace_dir: Path, 
        shared_dir: Path, 
        template: str
    ) -> Dict[str, Any]:
        """Create the workspace directory structure."""
        try:
            # Ensure shared directory exists
            if not ensure_directory_exists(shared_dir):
                return {
                    'success': False,
                    'error': f"Cannot create shared directory: {shared_dir}"
                }
            
            # Get template configuration
            template_config = self._get_template_config(template)
            
            # Create .claude directory if needed
            claude_dir = workspace_dir / ".claude"
            ensure_directory_exists(claude_dir)
            
            # Create CLAUDE.md if it doesn't exist
            claude_md = claude_dir / "CLAUDE.md"
            if not claude_md.exists():
                self._create_claude_md(claude_md, template_config)
            
            # Create thoughts directory structure
            thoughts_dir = workspace_dir / "thoughts"
            shared_thoughts_dir = shared_dir / "thoughts"
            
            # Initialize shared thoughts if needed
            if not shared_thoughts_dir.exists():
                self._initialize_shared_thoughts(shared_thoughts_dir, template_config)
            
            # Create local thoughts structure and link to shared
            self._setup_thoughts_directory(thoughts_dir, shared_thoughts_dir)
            
            # Copy agents and commands if requested
            if template_config.get('include_agents', True):
                self._setup_agents(claude_dir)
            
            if template_config.get('include_commands', True):
                self._setup_commands(claude_dir)
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create workspace structure: {e}"
            }
    
    def _get_template_config(self, template: str) -> Dict[str, Any]:
        """Get configuration for the specified template."""
        templates = {
            'minimal': {
                'include_agents': False,
                'include_commands': False,
                'thoughts_structure': 'basic',
            },
            'default': {
                'include_agents': True,
                'include_commands': True,
                'thoughts_structure': 'full',
            },
            'team': {
                'include_agents': True,
                'include_commands': True,
                'thoughts_structure': 'collaborative',
                'shared_focus': True,
            }
        }
        
        return templates.get(template, templates['default'])
    
    def _create_claude_md(self, claude_md: Path, config: Dict[str, Any]) -> None:
        """Create CLAUDE.md with template content."""
        git_info = get_git_info()
        
        content = f"""# mem8 Workspace Configuration

## Project Information
- Workspace: {self.config.workspace_dir.name}
- Shared memory enabled: Yes
- Template: {config.get('template', 'default')}
"""
        
        if git_info['is_git_repo']:
            content += f"- Git repository: {git_info['repo_root'].name}\\n"
            content += f"- Current branch: {git_info['current_branch']}\\n"
        
        content += """
## Memory Management
- Use `mem8 sync` to synchronize with shared memory
- Use `mem8 status` to check workspace status
- Use `mem8 search` to find content across memory

## Shared Thoughts
Access team thoughts via: @thoughts/shared/

## Import Additional Instructions
# Individual preferences (not tracked in git)
# @~/.claude/my-project-instructions.md

"""
        
        with open(claude_md, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _initialize_shared_thoughts(
        self, 
        shared_thoughts_dir: Path, 
        config: Dict[str, Any]
    ) -> None:
        """Initialize shared thoughts directory structure."""
        ensure_directory_exists(shared_thoughts_dir)
        
        # Create standard directories
        directories = [
            'shared/decisions',
            'shared/plans', 
            'shared/research',
            'shared/tickets',
            'shared/prs',
            'global/shared',
            'searchable'
        ]
        
        for directory in directories:
            ensure_directory_exists(shared_thoughts_dir / directory)
        
        # Create README
        readme_content = """# Shared AI Memory

This directory contains shared thoughts and memory for the team.

## Structure

- `shared/` - Team-shared thoughts and decisions
  - `decisions/` - Architecture and design decisions
  - `plans/` - Implementation plans and strategies  
  - `research/` - Research notes and findings
  - `tickets/` - Ticket analysis and solutions
  - `prs/` - Pull request discussions and reviews
- `global/shared/` - Global shared resources
- `searchable/` - Content optimized for search

## Usage

Use `mem8 sync` to keep your local workspace in sync with shared memory.
Use `mem8 search` to find relevant content across all memories.
"""
        
        readme_path = shared_thoughts_dir / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
    
    def _setup_thoughts_directory(
        self, 
        thoughts_dir: Path, 
        shared_thoughts_dir: Path
    ) -> None:
        """Set up local thoughts directory with shared integration."""
        ensure_directory_exists(thoughts_dir)
        
        # Create user-specific directory
        username = os.environ.get('USERNAME', os.environ.get('USER', 'user'))
        user_dir = thoughts_dir / username
        ensure_directory_exists(user_dir)
        ensure_directory_exists(user_dir / "notes")
        ensure_directory_exists(user_dir / "tickets")
        ensure_directory_exists(user_dir / "archive")
        
        # Link or copy shared directory
        shared_link = thoughts_dir / "shared"
        if not shared_link.exists():
            if create_symlink(shared_thoughts_dir, shared_link):
                pass  # Symlink created successfully
            else:
                # Fallback: create directory and note in README
                ensure_directory_exists(shared_link)
                note_file = shared_link / "README.md"
                with open(note_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Shared Memory\\n\\nShared directory: {shared_thoughts_dir}\\n\\nUse `mem8 sync` to synchronize.")
    
    def _setup_agents(self, claude_dir: Path) -> None:
        """Set up AI agents from template."""
        agents_dir = claude_dir / "agents"
        ensure_directory_exists(agents_dir)
        
        # Copy from template if available
        try:
            import mem8.templates
            template_agents_dir = resources.files(mem8.templates) / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "agents"
        except (ImportError, AttributeError):
            # Fallback for development
            template_agents_dir = Path(__file__).parent.parent.parent / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "agents"
        
        if template_agents_dir.exists():
            for agent_file in template_agents_dir.glob("*.md"):
                target_file = agents_dir / agent_file.name
                if not target_file.exists():
                    shutil.copy2(agent_file, target_file)
    
    def _setup_commands(self, claude_dir: Path) -> None:
        """Set up commands from template."""
        commands_dir = claude_dir / "commands"
        ensure_directory_exists(commands_dir)
        
        # Copy from template if available
        try:
            import mem8.templates
            template_commands_dir = resources.files(mem8.templates) / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "commands"
        except (ImportError, AttributeError):
            # Fallback for development
            template_commands_dir = Path(__file__).parent.parent.parent / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "commands"
        
        if template_commands_dir.exists():
            for command_file in template_commands_dir.glob("*.md"):
                target_file = commands_dir / command_file.name
                if not target_file.exists():
                    shutil.copy2(command_file, target_file)
    
    def get_status(self, detailed: bool = False) -> Dict[str, Any]:
        """Get workspace status information."""
        workspace_dir = self.config.workspace_dir
        
        components = {
            'claude_directory': {
                'path': workspace_dir / ".claude",
                'exists': (workspace_dir / ".claude").exists(),
            },
            'thoughts_directory': {
                'path': workspace_dir / "thoughts", 
                'exists': (workspace_dir / "thoughts").exists(),
            },
            'shared_directory': {
                'path': self.config.shared_dir,
                'exists': self.config.shared_dir.exists() if self.config.shared_dir else False,
            },
            'claude_memory': {
                'path': workspace_dir / ".claude" / "CLAUDE.md",
                'exists': (workspace_dir / ".claude" / "CLAUDE.md").exists(),
            }
        }
        
        # Sync status
        sync_status = self._get_sync_status()
        
        status = {
            'components': components,
            'sync_status': sync_status,
        }
        
        if detailed:
            status['details'] = self._get_detailed_status()
        
        return status
    
    def _get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status."""
        try:
            # Check for sync metadata
            sync_file = self.config.data_dir / "last_sync"
            
            last_sync = None
            if sync_file.exists():
                last_sync = time.ctime(sync_file.stat().st_mtime)
            
            # Count pending changes (simplified)
            pending_changes = 0
            thoughts_dir = self.config.thoughts_dir
            if thoughts_dir.exists():
                for file_path in thoughts_dir.rglob("*.md"):
                    if file_path.is_file():
                        # Check if file is newer than last sync
                        if not sync_file.exists() or file_path.stat().st_mtime > sync_file.stat().st_mtime:
                            pending_changes += 1
            
            return {
                'last_sync': last_sync,
                'pending_changes': pending_changes,
            }
        except Exception:
            return {
                'last_sync': None,
                'pending_changes': 0,
            }
    
    def _get_detailed_status(self) -> List[str]:
        """Get detailed status information."""
        details = []
        
        # Git information
        git_info = get_git_info()
        if git_info['is_git_repo']:
            details.append(f"Git repository: {git_info['repo_root'].name}")
            details.append(f"Current branch: {git_info['current_branch']}")
        
        # Claude Code integration
        claude_workspace = find_claude_code_workspace()
        if claude_workspace:
            details.append(f"Claude Code workspace: {claude_workspace}")
            memory_files = get_claude_memory_files()
            details.append(f"Memory files found: {len(memory_files)}")
        
        # Template information
        template_info = self.config.get('workspace.default_template', 'default')
        details.append(f"Workspace template: {template_info}")
        
        return details
    
    def get_thought_entities(self, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Get all thought entities with semantic understanding.""" 
        return self.thought_discovery.discover_all_thoughts(force_rescan)
    
    def find_thoughts_by_type(self, thought_type: str) -> List[ThoughtEntity]:
        """Find thoughts by semantic type."""
        entities = self.get_thought_entities()
        return [e for e in entities if e.type == thought_type]
        
    def find_thoughts_by_status(self, status: str) -> List[ThoughtEntity]:
        """Find thoughts by lifecycle status."""
        entities = self.get_thought_entities()
        return [e for e in entities if e.lifecycle_state == status]
    
    def search_content(
        self, 
        query: str, 
        limit: int = 10,
        content_type: str = 'all',
        search_method: str = 'fulltext',
        path_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search through memory content."""
        results = []
        
        # Search in thoughts directory
        thoughts_dir = self.config.thoughts_dir
        if thoughts_dir.exists() and content_type in ['all', 'thoughts']:
            search_dir = Path(thoughts_dir) / path_filter if path_filter else thoughts_dir
            if search_dir.exists():
                if search_method == 'semantic':
                    results.extend(self._semantic_search_directory(search_dir, query, 'thoughts'))
                else:
                    results.extend(self._search_directory(search_dir, query, 'thoughts'))
        
        # Search in Claude memory files
        if content_type in ['all', 'memories']:
            memory_files = get_claude_memory_files()
            for memory_file in memory_files:
                if path_filter and path_filter not in str(memory_file):
                    continue
                if search_method == 'semantic':
                    matches = self._semantic_search_file(memory_file, query, 'memory')
                else:
                    matches = self._search_file(memory_file, query, 'memory')
                results.extend(matches)
        
        # Sort by relevance (simplified scoring)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'query': query,
            'method': search_method,
            'matches': results[:limit],
            'total_found': len(results),
        }
    
    def _search_directory(self, directory: Path, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search files in a directory."""
        results = []
        query_lower = query.lower()
        
        for file_path in directory.rglob("*.md"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content_lower = content.lower()
                        
                        if query_lower in content_lower:
                            # Simple scoring based on frequency and position
                            score = content_lower.count(query_lower)
                            if content_lower.startswith(query_lower):
                                score += 5
                            
                            # Get title from first line or filename
                            lines = content.strip().split('\\n')
                            title = lines[0].strip('# ') if lines and lines[0].startswith('#') else file_path.stem
                            
                            results.append({
                                'type': content_type,
                                'title': title,
                                'path': str(file_path),
                                'score': score,
                            })
                except (IOError, UnicodeDecodeError):
                    continue
        
        return results
    
    def _search_file(self, file_path: Path, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if query.lower() in content.lower():
                return [{
                    'type': content_type,
                    'title': f"Memory: {file_path.name}",
                    'path': file_path,
                    'score': content.lower().count(query.lower()),
                }]
        except (IOError, UnicodeDecodeError):
            pass
        
        return []
    
    def _semantic_search_directory(self, directory: Path, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Semantic search files in a directory using sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(query)
            
            results = []
            for file_path in directory.rglob("*.md"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Get content embedding
                        content_embedding = model.encode(content[:2000])  # Limit content for performance
                        
                        # Calculate similarity
                        similarity = np.dot(query_embedding, content_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
                        )
                        
                        if similarity > 0.3:  # Threshold for relevance
                            lines = content.strip().split('\n')
                            title = lines[0].strip('# ') if lines and lines[0].startswith('#') else file_path.stem
                            
                            results.append({
                                'type': content_type,
                                'title': title,
                                'path': str(file_path),
                                'score': float(similarity) * 10,  # Scale for display
                            })
                    except (IOError, UnicodeDecodeError):
                        continue
            
            return results
            
        except ImportError:
            # Fallback to fulltext search if sentence-transformers not available
            return self._search_directory(directory, query, content_type)
    
    def _semantic_search_file(self, file_path: Path, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Semantic search a single file."""
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(query)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content_embedding = model.encode(content[:2000])
            similarity = np.dot(query_embedding, content_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
            )
            
            if similarity > 0.3:
                return [{
                    'type': content_type,
                    'title': f"Memory: {file_path.name}",
                    'path': str(file_path),
                    'score': float(similarity) * 10,
                }]
        except (ImportError, IOError, UnicodeDecodeError):
            # Fallback to fulltext search
            return self._search_file(file_path, query, content_type)
        
        return []
    
    def diagnose_workspace(self, auto_fix: bool = False) -> Dict[str, Any]:
        """Diagnose workspace health and optionally fix issues."""
        issues = []
        fixes_applied = []
        
        workspace_dir = self.config.workspace_dir
        
        # Check critical components
        claude_dir = workspace_dir / ".claude"
        if not claude_dir.exists():
            issues.append({
                'severity': 'error',
                'description': '.claude directory missing',
                'fix': 'Create .claude directory'
            })
            if auto_fix:
                ensure_directory_exists(claude_dir)
                fixes_applied.append('Created .claude directory')
        
        thoughts_dir = workspace_dir / "thoughts"
        if not thoughts_dir.exists():
            issues.append({
                'severity': 'warning', 
                'description': 'thoughts directory missing',
                'fix': 'Create thoughts directory'
            })
            if auto_fix:
                ensure_directory_exists(thoughts_dir)
                fixes_applied.append('Created thoughts directory')
        
        # Check shared directory connectivity
        shared_dir = self.config.shared_dir
        if shared_dir and not shared_dir.exists():
            issues.append({
                'severity': 'error',
                'description': f'Shared directory not accessible: {shared_dir}',
                'fix': 'Check network connectivity or path'
            })
        
        # Calculate health score
        total_checks = 4
        critical_issues = len([i for i in issues if i['severity'] == 'error'])
        warning_issues = len([i for i in issues if i['severity'] == 'warning'])
        
        health_score = max(0, 100 - (critical_issues * 25) - (warning_issues * 10))
        
        return {
            'issues': issues,
            'fixes_applied': fixes_applied,
            'health_score': health_score,
        }