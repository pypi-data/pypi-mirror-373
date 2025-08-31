"""Utility functions for AI-Mem."""

import os
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_shared_directory() -> Path:
    """Get the shared directory path with cross-platform support."""
    system = platform.system().lower()
    
    if system == 'windows':
        return _get_windows_shared_directory()
    elif system in ['linux', 'darwin']:
        return _get_unix_shared_directory()
    else:
        # Fallback to user directory
        return Path.home() / "AI-Mem-Shared"


def _get_windows_shared_directory() -> Path:
    """Get Windows-specific shared directory."""
    # Check for common Windows shared locations
    candidates = [
        # Network drives
        Path("//shared/ai-mem"),
        Path("Z:/AI-Mem"),
        Path("Y:/AI-Mem"),
        # Local shared folders
        Path("C:/Shared/AI-Mem"),
        Path(os.environ.get('USERPROFILE', '')) / "Documents" / "AI-Mem-Shared",
        Path.home() / "AI-Mem-Shared",
    ]
    
    # Check for existing OneDrive or other cloud sync folders
    onedrive_path = os.environ.get('OneDrive')
    if onedrive_path:
        candidates.insert(0, Path(onedrive_path) / "AI-Mem-Shared")
    
    # Return first accessible location
    for path in candidates:
        if path.exists() or _can_create_directory(path):
            return path
    
    # Fallback
    return Path.home() / "AI-Mem-Shared"


def _get_unix_shared_directory() -> Path:
    """Get Unix-like system shared directory."""
    candidates = [
        # Common Unix shared locations
        Path("/shared/ai-mem"),
        Path("/mnt/shared/ai-mem"),
        Path("/opt/ai-mem"),
        Path.home() / "AI-Mem-Shared",
        # Check for mounted network drives
        Path("/media") / os.environ.get('USER', 'shared') / "ai-mem",
    ]
    
    # Return first accessible location
    for path in candidates:
        if path.exists() or _can_create_directory(path):
            return path
    
    # Fallback
    return Path.home() / "AI-Mem-Shared"


def _can_create_directory(path: Path) -> bool:
    """Check if we can create a directory at the given path."""
    try:
        parent = path.parent
        if not parent.exists():
            return False
        return os.access(parent, os.W_OK)
    except (OSError, PermissionError):
        return False


def is_symlink_supported() -> bool:
    """Check if the current platform supports symlinks."""
    if platform.system().lower() == 'windows':
        # Windows requires special privileges for symlinks in older versions
        try:
            # Try creating a test symlink
            test_dir = Path.home() / ".ai-mem-test"
            test_link = Path.home() / ".ai-mem-test-link"
            
            test_dir.mkdir(exist_ok=True)
            if test_link.exists():
                test_link.unlink()
            
            os.symlink(test_dir, test_link)
            test_link.unlink()
            test_dir.rmdir()
            return True
        except (OSError, NotImplementedError):
            return False
    
    return True


def find_claude_code_workspace() -> Optional[Path]:
    """Find the nearest Claude Code workspace (.claude directory)."""
    current = Path.cwd()
    
    while current != current.parent:
        claude_dir = current / ".claude"
        if claude_dir.is_dir():
            return current
        current = current.parent
    
    return None


def get_claude_memory_files() -> List[Path]:
    """Get all Claude Code memory files in hierarchy."""
    memory_files = []
    workspace = find_claude_code_workspace()
    
    if not workspace:
        return memory_files
    
    # Look for CLAUDE.md files from workspace up to root
    current = workspace
    while current != current.parent:
        claude_md = current / "CLAUDE.md"
        if claude_md.exists():
            memory_files.append(claude_md)
        current = current.parent
    
    # Also check user-level memory
    user_claude = Path.home() / ".claude" / "CLAUDE.md"
    if user_claude.exists():
        memory_files.append(user_claude)
    
    return memory_files


def parse_claude_imports(content: str) -> List[str]:
    """Parse @import directives from Claude memory content."""
    imports = []
    lines = content.split('\\n')
    
    for line in lines:
        line = line.strip()
        # Look for @path imports outside code blocks
        if '@' in line and not line.startswith('```') and '`@' not in line:
            # Extract paths starting with @
            import_start = line.find('@')
            if import_start != -1:
                # Find the end of the path (space, newline, or end of line)
                import_path = ""
                for char in line[import_start + 1:]:
                    if char.isspace():
                        break
                    import_path += char
                
                if import_path:
                    imports.append(import_path)
    
    return imports


def resolve_import_path(import_path: str, base_path: Path) -> Optional[Path]:
    """Resolve an import path relative to base path."""
    if import_path.startswith('~/'):
        # User home directory
        return Path.home() / import_path[2:]
    elif import_path.startswith('/'):
        # Absolute path
        return Path(import_path)
    else:
        # Relative to base path
        return base_path.parent / import_path


def get_git_info() -> Dict[str, Any]:
    """Get git repository information if available."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = Path(result.stdout.strip())
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        current_branch = branch_result.stdout.strip()
        
        return {
            'is_git_repo': True,
            'repo_root': repo_root,
            'current_branch': current_branch,
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'is_git_repo': False,
            'repo_root': None,
            'current_branch': None,
        }


def create_symlink(target: Path, link_path: Path) -> bool:
    """Create a symlink with cross-platform support."""
    try:
        if link_path.exists():
            if link_path.is_symlink():
                link_path.unlink()
            else:
                return False
        
        # On Windows, try junction for directories
        if platform.system().lower() == 'windows' and target.is_dir():
            try:
                subprocess.run(['mklink', '/J', str(link_path), str(target)], 
                              shell=True, check=True)
                return True
            except subprocess.CalledProcessError:
                pass
        
        # Standard symlink
        os.symlink(target, link_path)
        return True
    except (OSError, NotImplementedError):
        return False


def ensure_directory_exists(path: Path) -> bool:
    """Ensure directory exists, creating if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False