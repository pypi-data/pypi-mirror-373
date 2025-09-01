#!/usr/bin/env python3
"""
Typer-based CLI implementation for mem8.
Modern CLI framework with enhanced type safety and developer experience.
"""

import typer
from typing import Annotated, Optional
from enum import Enum
from pathlib import Path

from rich.console import Console

from . import __version__
from .core.config import Config
from .core.memory import MemoryManager
from .core.sync import SyncManager
from .core.utils import setup_logging
from .core.intelligent_query import IntelligentQueryEngine
from .core.thought_actions import ThoughtActionEngine

# Create Rich console with UTF-8 support
console = Console(
    force_terminal=True,
    legacy_windows=None  # Auto-detect Windows compatibility
)

# Create Typer app
typer_app = typer.Typer(
    name="mem8",
    help="Memory management CLI for the orchestr8 ecosystem",
    add_completion=False,  # We'll manage this ourselves
    rich_markup_mode="rich"
)


# Enums for type safety
class ShellType(str, Enum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    POWERSHELL = "powershell"


class TemplateType(str, Enum):
    CLAUDE_CONFIG = "claude-config"
    THOUGHTS_REPO = "thoughts-repo"
    FULL = "full"


class SearchMethod(str, Enum):
    FULLTEXT = "fulltext"
    SEMANTIC = "semantic"


class SearchScope(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    TEAM = "team"
    ALL = "all"


class ThoughtType(str, Enum):
    PLAN = "plan"
    RESEARCH = "research"
    TICKET = "ticket"
    PR = "pr"
    DECISION = "decision"
    ALL = "all"


class ContentType(str, Enum):
    THOUGHTS = "thoughts"
    MEMORIES = "memories"
    ALL = "all"


class ActionType(str, Enum):
    SHOW = "show"
    DELETE = "delete"
    ARCHIVE = "archive"
    PROMOTE = "promote"


class SyncDirection(str, Enum):
    PULL = "pull"
    PUSH = "push"
    BOTH = "both"


class DeployEnvironment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


# Enhanced state management with lazy initialization (Phase 2)
class AppState:
    def __init__(self):
        self._config = None
        self._memory_manager = None
        self._sync_manager = None
        self._query_engine = None
        self._action_engine = None
        self._initialized = False
        self._verbose = False
        self._config_dir = None
        
    def initialize(self, verbose: bool = False, config_dir: Optional[Path] = None):
        """Initialize state with parameters."""
        if self._initialized and self._verbose == verbose and self._config_dir == config_dir:
            return  # Already initialized with same parameters
            
        self._verbose = verbose
        self._config_dir = config_dir
        
        if verbose:
            setup_logging(True)
            
        # Initialize components
        self._config = Config(config_dir)
        self._memory_manager = MemoryManager(self._config)
        self._sync_manager = SyncManager(self._config)
        self._query_engine = IntelligentQueryEngine(self._config)
        self._action_engine = ThoughtActionEngine(self._config)
        self._initialized = True
    
    @property
    def config(self) -> Config:
        if not self._config:
            self.initialize()
        return self._config
        
    @property
    def memory_manager(self) -> MemoryManager:
        if not self._memory_manager:
            self.initialize()
        return self._memory_manager
        
    @property
    def sync_manager(self) -> SyncManager:
        if not self._sync_manager:
            self.initialize()
        return self._sync_manager
        
    @property
    def query_engine(self) -> IntelligentQueryEngine:
        if not self._query_engine:
            self.initialize()
        return self._query_engine
        
    @property
    def action_engine(self) -> ThoughtActionEngine:
        if not self._action_engine:
            self.initialize()
        return self._action_engine


# Global app state instance
app_state = AppState()


def get_state() -> AppState:
    """Dependency injection helper for accessing app state."""
    return app_state


# Dependency injection helpers
def get_memory_manager() -> MemoryManager:
    """Get memory manager instance."""
    return app_state.memory_manager


def get_query_engine() -> IntelligentQueryEngine:
    """Get query engine instance."""
    return app_state.query_engine


def get_action_engine() -> ThoughtActionEngine:
    """Get action engine instance."""
    return app_state.action_engine


def get_sync_manager() -> SyncManager:
    """Get sync manager instance."""
    return app_state.sync_manager


def get_config() -> Config:
    """Get configuration instance."""
    return app_state.config


def set_app_state(verbose: bool = False, config_dir: Optional[Path] = None):
    """Initialize app state with parameters."""
    app_state.initialize(verbose=verbose, config_dir=config_dir)


# ============================================================================
# Simple Commands (Phase 1)
# ============================================================================

@typer_app.command()
def version():
    """Show version information."""
    console.print(f"mem8 version {__version__}")


@typer_app.command()
def status(
    detailed: Annotated[bool, typer.Option("--detailed", help="Show detailed status information")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Show mem8 workspace status."""
    set_app_state(verbose=verbose)
    state = get_state()
    memory_manager = state.memory_manager
    
    console.print("[bold blue]mem8 Workspace Status[/bold blue]")
    
    try:
        status_info = memory_manager.get_status(detailed=detailed)
        
        # Basic status table
        from rich.table import Table
        table = Table()
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Path", style="dim")
        
        for component, info in status_info['components'].items():
            status_icon = "✅" if info['exists'] else "❌"
            table.add_row(
                component.title().replace('_', ' '),
                f"{status_icon} {'Ready' if info['exists'] else 'Missing'}",
                str(info['path'])
            )
        
        console.print(table)
        
        # Show thought counts if detailed
        if detailed and 'thought_counts' in status_info:
            counts = status_info['thought_counts']
            console.print("\n[bold blue]Thought Statistics:[/bold blue]")
            
            count_table = Table()
            count_table.add_column("Type", style="cyan")
            count_table.add_column("Count", style="yellow")
            
            for thought_type, count in counts.items():
                count_table.add_row(thought_type.title(), str(count))
            
            console.print(count_table)
        
        # Show any issues
        if 'issues' in status_info and status_info['issues']:
            console.print("\n⚠️  [bold yellow]Issues:[/bold yellow]")
            for issue in status_info['issues']:
                console.print(f"  • {issue}")
                
    except Exception as e:
        console.print(f"❌ [bold red]Error checking status: {e}[/bold red]")
        if verbose:
            console.print_exception()


@typer_app.command()
def doctor(
    auto_fix: Annotated[bool, typer.Option("--auto-fix", help="Attempt to automatically fix issues")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Diagnose and fix mem8 workspace issues."""
    set_app_state(verbose=verbose)
    state = get_state()
    memory_manager = state.memory_manager
    
    console.print("[bold blue]Running mem8 diagnostics...[/bold blue]")
    
    try:
        diagnosis = memory_manager.diagnose_workspace(auto_fix=auto_fix)
        
        # Show issues
        if diagnosis['issues']:
            console.print("\n⚠️  [bold yellow]Issues found:[/bold yellow]")
            for issue in diagnosis['issues']:
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_icon} {issue['description']}")
                if auto_fix and issue.get('fixed'):
                    console.print(f"    ✅ [green]Fixed automatically[/green]")
        
        # Show fixes applied
        if auto_fix and diagnosis['fixes_applied']:
            console.print("\n✅ [bold green]Fixes applied:[/bold green]")
            for fix in diagnosis['fixes_applied']:
                console.print(f"  • {fix}")
        
        # Show recommendations
        if diagnosis.get('recommendations'):
            console.print("\n💡 [bold blue]Recommendations:[/bold blue]")
            for rec in diagnosis['recommendations']:
                console.print(f"  • {rec}")
        
        # Overall health
        if not diagnosis['issues']:
            console.print("\n✅ [bold green]All checks passed! Your mem8 workspace is healthy.[/bold green]")
        elif auto_fix:
            console.print(f"\n🔧 [blue]Fixed {len(diagnosis['fixes_applied'])} of {len(diagnosis['issues'])} issues.[/blue]")
        else:
            console.print(f"\n⚠️  [yellow]Found {len(diagnosis['issues'])} issues. Run with --auto-fix to attempt repairs.[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [bold red]Error running diagnostics: {e}[/bold red]")
        if verbose:
            console.print_exception()


@typer_app.command()
def dashboard():
    """Launch mem8 web dashboard."""
    console.print("🌐 [bold blue]Launching mem8 dashboard...[/bold blue]")
    
    from .core.smart_setup import launch_web_ui, show_setup_instructions
    
    if launch_web_ui():
        console.print("✅ [green]Dashboard opened in your browser![/green]")
        console.print("💡 [dim]Use 'mem8 status' to check backend health.[/dim]")
    else:
        console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
        instructions = show_setup_instructions()
        console.print(instructions)


@typer_app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", help="Maximum number of results to return")] = 10,
    content_type: Annotated[ContentType, typer.Option("--type", help="Type of content to search")] = ContentType.ALL,
    method: Annotated[SearchMethod, typer.Option("--method", help="Search method")] = SearchMethod.FULLTEXT,
    path: Annotated[Optional[str], typer.Option("--path", help="Restrict search to specific path")] = None,
    web: Annotated[bool, typer.Option("--web", help="Open results in web UI")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Search through AI memory and thoughts."""
    import urllib.parse
    import webbrowser
    from rich.table import Table
    
    set_app_state(verbose=verbose)
    
    # Handle web UI search
    if web and query:
        console.print(f"🌐 [bold blue]Opening search for '{query}' in web UI...[/bold blue]")
        # Open web UI with pre-populated search
        search_url = f'http://localhost:20040?search={urllib.parse.quote(query)}'
        
        from .core.smart_setup import launch_web_ui, show_setup_instructions
        if launch_web_ui():
            webbrowser.open(search_url)
            console.print("✅ [green]Search opened in web browser![/green]")
        else:
            console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
            instructions = show_setup_instructions()
            console.print(instructions)
        return
    
    # Traditional CLI search
    state = get_state()
    memory_manager = state.memory_manager
    
    search_method = f"[cyan]{method.value}[/cyan]"
    console.print(f"[bold blue]Searching for: '{query}' ({search_method})[/bold blue]")
    
    if method == SearchMethod.SEMANTIC:
        console.print("[yellow]⚠️  Semantic search requires sentence-transformers library[/yellow]")
    
    try:
        results = memory_manager.search_content(
            query=query,
            limit=limit,
            content_type=content_type.value,
            search_method=method.value,
            path_filter=path
        )
        
        if results['matches']:
            table = Table(title=f"Search Results ({len(results['matches'])} found)")
            table.add_column("Type", style="cyan", width=10)
            table.add_column("Title", style="green")
            table.add_column("Path", style="dim")
            table.add_column("Score", justify="right", style="yellow", width=8)
            
            for match in results['matches']:
                # Format score
                score_str = f"{match.get('score', 0.0):.2f}" if 'score' in match else "N/A"
                
                # Get title from match
                title = match.get('title', match.get('name', 'Untitled'))
                path_display = str(match.get('path', ''))
                
                # Truncate long paths
                if len(path_display) > 50:
                    path_display = "..." + path_display[-47:]
                
                table.add_row(
                    match.get('type', 'Unknown'),
                    title,
                    path_display,
                    score_str
                )
            
            console.print(table)
            
            # Show summary
            console.print(f"\\n💡 [dim]Found {len(results['matches'])} matches. Use --limit to see more results.[/dim]")
            if web:
                console.print("💡 [dim]Add --web to open results in web UI for better browsing.[/dim]")
                
        else:
            console.print(f"🔍 [yellow]No results found for '{query}' in {content_type.value}[/yellow]")
            console.print("💡 [dim]Try:")
            console.print("   • Different search terms")
            console.print("   • --method semantic for meaning-based search")
            console.print("   • --type all to search all content types")
            
    except Exception as e:
        console.print(f"❌ [bold red]Error during search: {e}[/bold red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Intelligent Completion Functions
# ============================================================================

def complete_thought_queries(incomplete: str):
    """Provide intelligent completion for thought queries."""
    try:
        # Initialize app state for completion
        state = get_state()
        memory_manager = state.memory_manager
        entities = memory_manager.get_thought_entities()
        
        suggestions = set()
        
        # Add common query patterns
        common_patterns = [
            "completed plans", "active research", "draft plans", 
            "personal notes", "shared decisions", "recent thoughts"
        ]
        suggestions.update([p for p in common_patterns if p.startswith(incomplete.lower())])
        
        # Add thought titles and topics
        for entity in entities[:50]:  # Limit for performance
            title = entity.metadata.get('topic', entity.path.stem)
            if incomplete.lower() in title.lower():
                suggestions.add(title)
                
            # Add individual words from titles for partial matching
            words = title.lower().split()
            for word in words:
                if len(word) > 3 and word.startswith(incomplete.lower()):
                    suggestions.add(word)
        
        # Add type-based suggestions
        type_patterns = ["plans", "research", "tickets", "decisions", "prs"]
        suggestions.update([t for t in type_patterns if t.startswith(incomplete.lower())])
        
        return sorted(list(suggestions))[:10]  # Limit to 10 suggestions
    except Exception:
        # Fallback to basic suggestions if anything fails
        return ["plans", "research", "completed", "active", "shared", "personal"]


# ============================================================================
# Complex Commands (Phase 2)
# ============================================================================

@typer_app.command()
def find(
    query: Annotated[str, typer.Argument(
        help="Natural language query for finding thoughts",
        autocompletion=complete_thought_queries
    )],
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    scope: Annotated[SearchScope, typer.Option(
        "--scope", help="Limit search scope"
    )] = SearchScope.ALL,
    thought_type: Annotated[ThoughtType, typer.Option(
        "--type", help="Limit to thought type"
    )] = ThoughtType.ALL,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    force: Annotated[bool, typer.Option(
        "--force", help="Skip confirmation prompts for destructive actions"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find thoughts using intelligent natural language queries."""
    from rich.table import Table
    from pathlib import Path
    
    set_app_state(verbose=verbose)
    state = get_state()
    memory_manager = state.memory_manager
    
    # Initialize intelligent query engine
    query_engine = state.query_engine
    
    console.print(f"[bold blue]🔍 Finding: '{query}'[/bold blue]")
    if action:
        action_color = "yellow" if dry_run else "red" if action == ActionType.DELETE else "cyan"
        dry_run_text = " (dry run)" if dry_run else ""
        console.print(f"[bold {action_color}]Action: {action.value}{dry_run_text}[/bold {action_color}]")
    
    try:
        # Parse natural language query
        intent = query_engine.parse_query(query)
        
        # Show parsed intent for debugging
        if verbose:
            console.print(f"[dim]Parsed intent: type={intent.target_type}, status={intent.status_filter}, content='{intent.content_query}'[/dim]")
        
        # Execute query
        results = query_engine.execute_query(intent)
        
        # Apply CLI filters (override intent if specified)
        if scope != SearchScope.ALL:
            results = [r for r in results if r.scope == scope.value]
        if thought_type != ThoughtType.ALL:
            results = [r for r in results if r.type == thought_type.value]
            
        # Limit results
        results = results[:limit]
        
        if not results:
            console.print("[yellow]❌ No thoughts found matching your query[/yellow]")
            return
            
        # Display results table
        table = Table(title=f"Found {len(results)} thoughts")
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Title", style="green")
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Scope", style="blue", width=10)  
        table.add_column("Path", style="dim")
        
        for entity in results:
            # Extract title from metadata or content
            title = entity.metadata.get('topic', entity.path.stem)
            if len(title) > 40:
                title = title[:37] + "..."
                
            # Format path relative to workspace
            try:
                rel_path = entity.path.relative_to(Path.cwd())
            except ValueError:
                rel_path = entity.path
                
            table.add_row(
                entity.type.title(),
                title,
                entity.lifecycle_state.replace('_', ' ').title(),
                entity.scope.title(),
                str(rel_path)
            )
            
        console.print(table)
        
        # Execute action if specified
        if action and not dry_run:
            _execute_action(action.value, results, force, verbose)
        elif action and dry_run:
            _preview_action(action.value, results)
            
    except Exception as e:
        console.print(f"❌ [bold red]Error during search: {e}[/bold red]")
        if verbose:
            console.print_exception()


def _execute_action(action: str, results: list, force: bool, verbose: bool):
    """Execute action on found thoughts."""
    if not force and action in ['delete', 'archive']:
        import typer
        confirm = typer.confirm(f"Are you sure you want to {action} {len(results)} thoughts?")
        if not confirm:
            console.print("❌ [yellow]Action cancelled[/yellow]")
            return
    
    # Get action engine for execution
    action_engine = get_action_engine()
    
    for entity in results:
        try:
            if action == 'show':
                console.print(f"📄 [bold]{entity.path}[/bold]")
                content = entity.path.read_text(encoding='utf-8')
                console.print(content[:500] + "..." if len(content) > 500 else content)
                console.print()
            elif action == 'delete':
                action_engine.delete_thought(entity)
                console.print(f"🗑️  [red]Deleted: {entity.path.name}[/red]")
            elif action == 'archive':
                action_engine.archive_thought(entity)
                console.print(f"📦 [yellow]Archived: {entity.path.name}[/yellow]")
            elif action == 'promote':
                action_engine.promote_thought(entity)
                console.print(f"⭐ [green]Promoted: {entity.path.name}[/green]")
        except Exception as e:
            console.print(f"❌ [red]Error {action}ing {entity.path.name}: {e}[/red]")
            if verbose:
                console.print_exception()


def _preview_action(action: str, results: list):
    """Preview what action would do without executing."""
    from rich.table import Table
    
    table = Table(title=f"Would {action} {len(results)} thoughts (dry run)")
    table.add_column("Action", style="cyan", width=10)
    table.add_column("Type", style="blue", width=10)
    table.add_column("Path", style="dim")
    
    for entity in results:
        # Format relative path for display
        try:
            # If path is not relative to current directory, use absolute path or just filename
            rel_path = entity.path.relative_to(Path.cwd())
        except ValueError:
            # If path is not relative to current directory, use absolute path or just filename
            rel_path = entity.path.name
        table.add_row(action.title(), entity.type, str(rel_path))
        
    console.print(table)
    console.print(f"[dim]Run without --dry-run to execute[/dim]")


# ============================================================================
# Remaining Commands (Phase 3)
# ============================================================================

@typer_app.command()
def init(
    template: Annotated[TemplateType, typer.Option(
        "--template", help="Template to use"
    )] = TemplateType.FULL,
    config_file: Annotated[Optional[Path], typer.Option(
        "--config-file", help="Path to cookiecutter configuration YAML file",
        exists=True
    )] = None,
    shared_dir: Annotated[Optional[Path], typer.Option(
        "--shared-dir", help="Path to shared directory for thoughts"
    )] = None,
    force: Annotated[bool, typer.Option(
        "--force", help="Force initialization even if directory exists"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Initialize mem8 workspace using cookiecutter templates."""
    from cookiecutter.main import cookiecutter
    
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Initializing mem8 workspace with {template.value} template...[/bold blue]")
    
    try:
        workspace_dir = Path.cwd()
        
        # Determine template path and requirements
        try:
            from importlib import resources
            if template == TemplateType.CLAUDE_CONFIG:
                template_path = str(resources.files('mem8') / 'templates' / 'claude-dot-md-template')
                requires_shared = False
            elif template == TemplateType.THOUGHTS_REPO:
                template_path = str(resources.files('mem8') / 'templates' / 'shared-thoughts-template')
                requires_shared = True
            else:  # FULL
                # Use full template (both claude-dot-md and shared-thoughts)
                template_path = str(resources.files('mem8') / 'templates' / 'claude-dot-md-template')
                requires_shared = True
        except (ImportError, FileNotFoundError) as e:
            console.print(f"❌ [red]Template not found: {e}[/red]")
            if verbose:
                console.print_exception()
            return
        
        # Validate shared directory if required
        if requires_shared and not shared_dir:
            console.print("[yellow]⚠️  This template requires a shared directory.[/yellow]")
            console.print("Use --shared-dir to specify the path to your shared thoughts repository.")
            return
            
        # Prepare cookiecutter context
        extra_context = {}
        if config_file:
            import yaml
            with open(config_file, 'r') as f:
                extra_context = yaml.safe_load(f)
        
        if shared_dir:
            extra_context['shared_thoughts_dir'] = str(shared_dir)
        
        # Run cookiecutter
        output_dir = cookiecutter(
            template_path,
            output_dir=str(workspace_dir),
            extra_context=extra_context,
            overwrite_if_exists=force,
            no_input=bool(config_file)
        )
        
        console.print(f"✅ [green]Workspace initialized at: {output_dir}[/green]")
        console.print("💡 [dim]Run 'mem8 status' to verify setup.[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error during initialization: {e}[/red]")
        if verbose:
            console.print_exception()


@typer_app.command()
def sync(
    direction: Annotated[SyncDirection, typer.Option(
        "--direction", help="Sync direction"
    )] = SyncDirection.BOTH,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be synced without making changes"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Synchronize local and shared memory."""
    set_app_state(verbose=verbose)
    state = get_state()
    sync_manager = state.sync_manager
    
    action = "Dry run:" if dry_run else "Syncing"
    console.print(f"[bold blue]{action} memory ({direction.value})...[/bold blue]")
    
    try:
        result = sync_manager.sync_memory(direction=direction.value, dry_run=dry_run)
        
        if result['success']:
            console.print("✅ [green]Sync completed successfully[/green]")
            if 'stats' in result:
                stats = result['stats']
                console.print(f"📊 [dim]Files synced: {stats.get('files_synced', 0)}, "
                            f"Conflicts: {stats.get('conflicts', 0)}[/dim]")
        else:
            console.print("❌ [red]Sync failed[/red]")
            if 'error' in result:
                console.print(f"Error: {result['error']}")
                
    except Exception as e:
        console.print(f"❌ [red]Error during sync: {e}[/red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Command Groups (Team and Deploy)
# ============================================================================

# Create team subapp
team_app = typer.Typer(name="team", help="Team collaboration commands")
typer_app.add_typer(team_app, name="team")

@team_app.command()
def create(
    name: Annotated[str, typer.Option("--name", help="Team name")],
    description: Annotated[Optional[str], typer.Option("--description", help="Team description")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Create a new team."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Creating team: {name}[/bold blue]")
    if description:
        console.print(f"Description: {description}")
    
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")
    console.print("For now, teams are managed locally through shared directories.")


@team_app.command()
def list(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """List available teams."""
    set_app_state(verbose=verbose)
    
    console.print("[bold blue]Available teams:[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


@team_app.command()
def join(
    team_name: Annotated[str, typer.Argument(help="Team name to join")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Join an existing team."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Joining team: {team_name}[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


# Create deploy subapp  
deploy_app = typer.Typer(name="deploy", help="Deployment commands")
typer_app.add_typer(deploy_app, name="deploy")

@deploy_app.command()
def kubernetes(
    env: Annotated[DeployEnvironment, typer.Option(
        "--env", help="Deployment environment"
    )] = DeployEnvironment.LOCAL,
    domain: Annotated[Optional[str], typer.Option("--domain", help="Custom domain for deployment")] = None,
    replicas: Annotated[int, typer.Option("--replicas", help="Number of replicas")] = 2,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Deploy to Kubernetes cluster."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Deploying to Kubernetes ({env.value})...[/bold blue]")
    if domain:
        console.print(f"Domain: {domain}")
    console.print(f"Replicas: {replicas}")
    
    console.print("[yellow]⚠️  Kubernetes deployment requires backend API (Phase 2)[/yellow]")
    console.print("Available after backend API and frontend are implemented.")


@deploy_app.command()
def local(
    port: Annotated[int, typer.Option("--port", help="Port to run on")] = 8000,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Start local development server."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Starting local server on port {port}...[/bold blue]")
    console.print("[yellow]⚠️  Local server requires backend API (Phase 2)[/yellow]")


# ============================================================================
# Shell Completion (Using Typer's built-in system)
# ============================================================================

# Enable Typer's built-in completion
typer_app.add_completion = True