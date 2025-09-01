"""Smart setup functionality for AI-Mem quick-start workflow."""

import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

from .utils import get_git_info, get_shared_directory, create_symlink, ensure_directory_exists


def detect_project_context() -> Dict[str, Any]:
    """Detect project type, git repos, and optimal configuration."""
    git_info = get_git_info()
    
    context = {
        'is_claude_code_project': Path('.claude').exists(),
        'git_repos': discover_local_repositories(),
        'project_type': infer_project_type(),
        'username': get_git_username(),
        'shared_location': find_optimal_shared_location(),
        'git_info': git_info,
        'current_dir': Path.cwd(),
        'parent_dir': Path.cwd().parent,
    }
    return context


def discover_local_repositories() -> List[Dict[str, Any]]:
    """Find all git repositories in parent and sibling directories."""
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    repos = []
    
    # Search current directory
    repos.extend(find_git_repos(current_dir))
    
    # Search sibling directories (orchestr8, agenticinsights, etc.)
    repos.extend(find_git_repos(parent_dir, max_depth=2))
    
    return repos


def find_git_repos(base_path: Path, max_depth: int = 1) -> List[Dict[str, Any]]:
    """Find git repositories in a directory tree."""
    repos = []
    
    def _scan_directory(path: Path, current_depth: int = 0):
        if current_depth > max_depth:
            return
            
        try:
            # Check if this directory is a git repository
            if (path / '.git').exists():
                repo_info = analyze_git_repository(path)
                if repo_info:
                    repos.append(repo_info)
                return  # Don't scan inside git repos
            
            # Scan subdirectories if we haven't reached max depth
            if current_depth < max_depth:
                for subdir in path.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith('.'):
                        _scan_directory(subdir, current_depth + 1)
                        
        except (PermissionError, OSError):
            # Skip directories we can't read
            pass
    
    _scan_directory(base_path)
    return repos


def analyze_git_repository(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze a git repository for AI-Mem relevant information."""
    try:
        # Get basic git info
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        repo_root = Path(result.stdout.strip())
        repo_name = repo_root.name
        
        # Get remote URL if available
        try:
            remote_result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = remote_result.stdout.strip()
        except subprocess.CalledProcessError:
            remote_url = None
        
        # Check for thoughts directories
        thoughts_paths = []
        candidate_paths = [
            repo_root / 'thoughts',
            repo_root / 'docs' / 'thoughts', 
            repo_root / 'thoughts' / 'shared'
        ]
        
        for candidate in candidate_paths:
            if candidate.exists() and candidate.is_dir():
                thoughts_paths.append(str(candidate))
        
        # Check if it's an AI-Mem project
        is_ai_mem_project = (repo_root / 'ai_mem').exists() or repo_name == 'ai-mem'
        
        # Check if it's a Claude Code project
        is_claude_project = (repo_root / '.claude').exists()
        
        return {
            'name': repo_name,
            'path': str(repo_root),
            'remote_url': remote_url,
            'thoughts_paths': thoughts_paths,
            'is_ai_mem_project': is_ai_mem_project,
            'is_claude_project': is_claude_project,
            'has_thoughts': len(thoughts_paths) > 0,
        }
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def infer_project_type() -> str:
    """Infer the type of project based on files present."""
    cwd = Path.cwd()
    
    # Check for common project indicators
    if (cwd / 'package.json').exists():
        return 'nodejs'
    elif (cwd / 'pyproject.toml').exists() or (cwd / 'setup.py').exists():
        return 'python'
    elif (cwd / 'Cargo.toml').exists():
        return 'rust'
    elif (cwd / 'go.mod').exists():
        return 'go'
    elif (cwd / '.claude').exists():
        return 'claude-code'
    elif (cwd / 'thoughts').exists():
        return 'ai-mem'
    else:
        return 'general'


def get_git_username() -> str:
    """Get git username from config."""
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to system username
        return os.environ.get('USER', os.environ.get('USERNAME', 'user'))


def find_optimal_shared_location() -> Path:
    """Find the optimal shared directory location."""
    # Use existing utility but with some intelligence
    shared_dir = get_shared_directory()
    
    # If we're in a projects directory, try to find a shared location nearby
    cwd = Path.cwd()
    if 'projects' in str(cwd).lower():
        # Look for existing shared directories in the projects area
        projects_parent = None
        current = cwd
        while current != current.parent:
            if 'projects' in current.name.lower():
                projects_parent = current.parent
                break
            current = current.parent
        
        if projects_parent:
            candidate_shared = projects_parent / 'ai-mem-shared'
            if candidate_shared.exists() or can_create_directory(candidate_shared):
                return candidate_shared
    
    return shared_dir


def can_create_directory(path: Path) -> bool:
    """Check if we can create a directory at the given path."""
    try:
        parent = path.parent
        if not parent.exists():
            return False
        return os.access(parent, os.W_OK)
    except (OSError, PermissionError):
        return False


def generate_smart_config(context: Dict[str, Any], repos_arg: Optional[str] = None) -> Dict[str, Any]:
    """Generate configuration based on detected context."""
    repos = context['git_repos']
    
    # If repos were specified via command line, filter to those
    if repos_arg:
        repo_names = [name.strip() for name in repos_arg.split(',')]
        repos = [repo for repo in repos if repo['name'] in repo_names or repo['path'] in repo_names]
    
    config = {
        'username': context['username'],
        'shared_location': context['shared_location'],
        'project_type': context['project_type'],
        'is_claude_project': context['is_claude_code_project'],
        'repositories': repos,
        'current_repo': context.get('git_info', {}).get('repo_root'),
    }
    
    return config


def setup_minimal_structure(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create minimal AI-Mem structure with smart defaults."""
    results = {'created': [], 'linked': [], 'errors': []}
    
    # Create thoughts directory
    thoughts_dir = Path('thoughts')
    if ensure_directory_exists(thoughts_dir):
        results['created'].append(str(thoughts_dir))
    else:
        results['errors'].append(f"Failed to create {thoughts_dir}")
        return results
    
    # Create shared symlink or junction
    shared_dir = thoughts_dir / 'shared'
    if not shared_dir.exists():
        shared_location = Path(config['shared_location'])
        
        # Ensure shared location exists
        if ensure_directory_exists(shared_location):
            results['created'].append(str(shared_location))
        
        # Create the link
        if create_shared_link(shared_dir, shared_location):
            results['linked'].append(f"{shared_dir} -> {shared_location}")
        else:
            results['errors'].append(f"Failed to create symlink {shared_dir} -> {shared_location}")
    
    # Create user directory
    user_dir = thoughts_dir / config['username']
    if ensure_directory_exists(user_dir):
        results['created'].append(str(user_dir))
    else:
        results['errors'].append(f"Failed to create user directory {user_dir}")
    
    # Create basic structure
    subdirs = ['research', 'plans', 'tickets', 'notes']
    for subdir_name in subdirs:
        subdir = user_dir / subdir_name
        if ensure_directory_exists(subdir):
            results['created'].append(str(subdir))
        else:
            results['errors'].append(f"Failed to create {subdir}")
    
    return results


def create_shared_link(link_path: Path, target_path: Path) -> bool:
    """Create shared directory link with fallback options."""
    # Try symlink first
    if create_symlink(target_path, link_path):
        return True
    
    # If symlink fails, create the directory locally as fallback
    if ensure_directory_exists(link_path):
        return True
    
    return False


def launch_web_ui() -> bool:
    """Launch web UI if backend is running, otherwise provide instructions."""
    try:
        # Check if backend is running
        response = requests.get('http://localhost:8000/api/v1/health', timeout=2)
        if response.status_code == 200:
            webbrowser.open('http://localhost:20040')
            return True
        else:
            return False
    except requests.RequestException:
        return False


def show_setup_instructions():
    """Show instructions for setting up backend."""
    instructions = """
🚀 To launch the AI-Mem web interface:

1. Start the backend:
   cd backend && uv run uvicorn aimem_api.main:app --reload --host 127.0.0.1 --port 8000

2. Start the frontend:
   cd frontend && npm run dev -- --port 20040

3. Open your browser to: http://localhost:20040

Or use Docker:
   docker-compose up -d
"""
    return instructions