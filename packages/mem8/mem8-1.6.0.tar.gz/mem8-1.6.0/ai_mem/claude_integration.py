"""Claude Code integration functionality for AI-Mem."""

from pathlib import Path
from typing import Dict, Any, Optional


def generate_claude_memory_integration(config: Dict[str, Any]) -> str:
    """Generate CLAUDE.md content for AI-Mem integration."""
    repos_config = ""
    if config.get('repositories'):
        repos_config = "\n".join([
            f"- {repo['name']}: {repo.get('thoughts_paths', ['No thoughts found'])[0] if repo.get('thoughts_paths') else 'No thoughts found'}" 
            for repo in config.get('repositories', [])
        ])
    else:
        repos_config = "- No repositories discovered (run ai-mem quick-start to discover)"
    
    claude_md_content = f"""
# AI Memory Integration

This project uses AI-Mem for memory management across repositories.

## Available Repositories
{repos_config}

## Memory Commands
- `/setup-memory` - Configure AI memory for this project
- `/browse-memories` - Search and explore thoughts across repositories
- `ai-mem search "query"` - Full-text search across all memories
- `ai-mem quick-start --web` - Launch visual memory browser
- `ai-mem dashboard` - Open web interface

## Shared Thoughts Location
Shared thoughts: `{config.get('shared_location', 'thoughts/shared/')}`

## Workflow Integration  
- Research documents: `thoughts/shared/research/`
- Implementation plans: `thoughts/shared/plans/` 
- PR discussions: `thoughts/shared/prs/`
- User notes: `thoughts/{config.get('username', 'user')}/`

## Quick Start
Run `ai-mem quick-start --web` to set up AI-Mem and launch the visual interface.
"""
    return claude_md_content


def update_claude_md_integration(config: Dict[str, Any]) -> bool:
    """Add AI-Mem integration section to existing CLAUDE.md."""
    claude_md_path = Path('.claude/CLAUDE.md')
    project_claude_md = Path('CLAUDE.md')
    
    # Try both locations
    target_file = None
    if claude_md_path.exists():
        target_file = claude_md_path
    elif project_claude_md.exists():
        target_file = project_claude_md
    
    if target_file:
        try:
            content = target_file.read_text(encoding='utf-8')
            if 'AI Memory Integration' not in content:
                integration = generate_claude_memory_integration(config)
                content += f"\n{integration}"
                target_file.write_text(content, encoding='utf-8')
                return True
        except (OSError, UnicodeDecodeError):
            return False
    
    return False


def create_minimal_claude_md(config: Dict[str, Any]) -> bool:
    """Create a minimal CLAUDE.md file with AI-Mem integration."""
    claude_md = Path('CLAUDE.md')
    
    if not claude_md.exists():
        integration = generate_claude_memory_integration(config)
        minimal_content = f"""# Project Memory

This project uses AI-Mem for intelligent memory management and team collaboration.
{integration}
"""
        try:
            claude_md.write_text(minimal_content, encoding='utf-8')
            return True
        except OSError:
            return False
    
    return False


def setup_claude_code_integration(config: Dict[str, Any]) -> Dict[str, Any]:
    """Set up Claude Code integration for AI-Mem."""
    results = {'updated': [], 'created': [], 'errors': []}
    
    # Try to update existing CLAUDE.md
    if update_claude_md_integration(config):
        if Path('.claude/CLAUDE.md').exists():
            results['updated'].append('.claude/CLAUDE.md')
        elif Path('CLAUDE.md').exists():
            results['updated'].append('CLAUDE.md')
    
    # If no CLAUDE.md exists and this isn't a Claude Code project, create one
    elif not Path('.claude').exists() and create_minimal_claude_md(config):
        results['created'].append('CLAUDE.md')
    
    return results