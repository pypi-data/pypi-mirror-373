#!/usr/bin/env python3
"""
mem8 CLI: Memory management for the orchestr8 ecosystem - team collaboration with shared thoughts.
"""

import os
import shutil
import sys
import webbrowser
import urllib.parse
from pathlib import Path
from typing import Optional

# Configure UTF-8 encoding for Windows compatibility
def setup_utf8_encoding():
    """Setup UTF-8 encoding for Windows compatibility."""
    # Set environment variables for UTF-8 mode
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Configure stdout/stderr streams
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            # Fallback if reconfigure fails
            pass
    
    # Import colorama after setting up encoding
    try:
        import colorama
        colorama.init(autoreset=True)
    except ImportError:
        pass

# Setup encoding before other imports
setup_utf8_encoding()

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .core.config import Config
from .core.memory import MemoryManager
from .core.sync import SyncManager
from .core.utils import get_shared_directory, setup_logging
from .core.smart_setup import (
    detect_project_context, 
    generate_smart_config, 
    setup_minimal_structure,
    launch_web_ui,
    show_setup_instructions
)
from .claude_integration import setup_claude_code_integration

# Create Rich console with UTF-8 support
console = Console(
    force_terminal=True,
    legacy_windows=None  # Auto-detect Windows compatibility
)


@click.group()
@click.version_option(version=__version__, prog_name="mem8")
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output"
)
@click.option(
    "--config-dir", 
    type=click.Path(), 
    help="Custom configuration directory"
)
@click.pass_context
def cli(ctx, verbose: bool, config_dir: Optional[str]):
    """mem8: Memory management CLI for the orchestr8 ecosystem."""
    setup_logging(verbose)
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = Config(config_dir)
    ctx.obj['memory_manager'] = MemoryManager(ctx.obj['config'])
    ctx.obj['sync_manager'] = SyncManager(ctx.obj['config'])


@cli.command()
@click.option(
    "--template",
    type=click.Choice(['claude-config', 'thoughts-repo', 'full']),
    default='full',
    help="Template to use: claude-config (Claude Code only), thoughts-repo (thoughts only), or full (both)"
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to cookiecutter configuration YAML file"
)
@click.option(
    "--shared-dir", 
    type=click.Path(), 
    help="Path to shared directory for thoughts (when using thoughts-repo or full)"
)
@click.option(
    "--force", 
    is_flag=True, 
    help="Force initialization even if directory exists"
)
@click.pass_context
def init(ctx, template: str, config_file: Optional[str], shared_dir: Optional[str], force: bool):
    """Initialize mem8 workspace using cookiecutter templates."""
    from cookiecutter.main import cookiecutter
    
    console.print(f"[bold blue]Initializing mem8 workspace with {template} template...[/bold blue]")
    
    try:
        workspace_dir = Path.cwd()
        project_root = Path(__file__).parent.parent
        
        # Determine template path and requirements
        if template == 'claude-config':
            template_path = project_root / "claude-dot-md-template"
            needs_shared = False
        elif template == 'thoughts-repo':
            template_path = project_root / "shared-thoughts-template" 
            needs_shared = True
        else:  # full
            # Run both templates
            claude_template_path = project_root / "claude-dot-md-template"
            thoughts_template_path = project_root / "shared-thoughts-template"
            needs_shared = True
        
        # Check if workspace already exists and handle carefully
        existing_files = []
        critical_dirs = []
        
        if template in ['claude-config', 'full']:
            if (workspace_dir / ".claude").exists():
                existing_files.append(".claude directory")
                critical_dirs.append(workspace_dir / ".claude")
            if (workspace_dir / "CLAUDE.md").exists():
                existing_files.append("CLAUDE.md file")
        
        if template in ['thoughts-repo', 'full']:
            if (workspace_dir / "thoughts").exists():
                existing_files.append("thoughts directory")
                critical_dirs.append(workspace_dir / "thoughts")
                # Check specifically for shared directory
                if (workspace_dir / "thoughts" / "shared").exists():
                    existing_files.append("thoughts/shared directory (contains your data!)")
        
        if existing_files and not force:
            console.print(f"⚠️  [yellow]Existing workspace components found:[/yellow]")
            for file in existing_files:
                console.print(f"  • {file}")
            
            # Special warning for shared directory
            if any("shared" in f for f in existing_files):
                console.print("\n🚨 [bold red]WARNING: thoughts/shared contains your memory data![/bold red]")
                console.print("[red]This directory will NOT be overwritten to protect your data.[/red]")
            
            console.print(f"\n[bold]Options:[/bold]")
            console.print(f"  • Use [cyan]--force[/cyan] to overwrite (⚠️  will preserve thoughts/shared)")
            console.print(f"  • Move to a clean directory")
            console.print(f"  • Remove conflicting files manually")
            sys.exit(1)
        
        if existing_files and force:
            console.print(f"⚠️  [yellow]Overwriting existing files with --force[/yellow]")
            # Always preserve thoughts/shared directory
            shared_backup = None
            if (workspace_dir / "thoughts" / "shared").exists():
                console.print("[bold green]🛡️  Preserving existing thoughts/shared directory[/bold green]")
                import tempfile
                shared_backup = Path(tempfile.mkdtemp()) / "shared_backup"
                shutil.copytree(workspace_dir / "thoughts" / "shared", shared_backup)
                console.print(f"Backed up to: {shared_backup}")
        
        # Determine shared directory if needed
        if needs_shared:
            if shared_dir:
                shared_path = Path(shared_dir).resolve()
            else:
                shared_path = get_shared_directory()
            console.print(f"Using shared directory: {shared_path}")
        
        # Run cookiecutter for the appropriate templates
        if template == 'full':
            # First create Claude Code config
            console.print("Creating Claude Code configuration...")
            claude_result = cookiecutter(
                str(claude_template_path),
                config_file=config_file,
                output_dir=str(workspace_dir),
                overwrite_if_exists=force
            )
            
            # Then create thoughts repository
            console.print("Creating thoughts repository...")
            thoughts_result = cookiecutter(
                str(thoughts_template_path),
                config_file=config_file, 
                output_dir=str(workspace_dir),
                overwrite_if_exists=force
            )
            
            console.print("✅ [green]Full workspace initialized successfully![/green]")
            console.print(f"Claude config: {claude_result}")
            console.print(f"Thoughts repo: {thoughts_result}")
            
            # Restore shared backup if we had one
            if 'shared_backup' in locals() and shared_backup and shared_backup.exists():
                console.print("🔄 [bold blue]Restoring your preserved thoughts/shared directory...[/bold blue]")
                if (workspace_dir / "thoughts" / "shared").exists():
                    shutil.rmtree(workspace_dir / "thoughts" / "shared")
                shutil.copytree(shared_backup, workspace_dir / "thoughts" / "shared")
                shutil.rmtree(shared_backup.parent)  # Clean up temp directory
                console.print("✅ [green]Your thoughts/shared data has been restored![/green]")
            
        else:
            # Single template
            result = cookiecutter(
                str(template_path),
                config_file=config_file,
                output_dir=str(workspace_dir), 
                overwrite_if_exists=force
            )
            
            console.print(f"✅ [green]{template} template initialized successfully![/green]")
            console.print(f"Output: {result}")
            
            # Restore shared backup if we had one
            if 'shared_backup' in locals() and shared_backup and shared_backup.exists():
                console.print("🔄 [bold blue]Restoring your preserved thoughts/shared directory...[/bold blue]")
                if (workspace_dir / "thoughts" / "shared").exists():
                    shutil.rmtree(workspace_dir / "thoughts" / "shared")
                shutil.copytree(shared_backup, workspace_dir / "thoughts" / "shared")
                shutil.rmtree(shared_backup.parent)  # Clean up temp directory
                console.print("✅ [green]Your thoughts/shared data has been restored![/green]")
        
        # Show next steps
        console.print("\\n[bold]Next steps:[/bold]")
        if template in ['thoughts-repo', 'full']:
            console.print("  • Run [cyan]mem8 sync[/cyan] to sync with shared memory")
        if template in ['claude-config', 'full']:
            console.print("  • Edit [cyan].claude/CLAUDE.md[/cyan] to customize your setup")
        console.print("  • Run [cyan]mem8 status[/cyan] to check workspace status")
        console.print("  • Run [cyan]mem8 search <query>[/cyan] to search your memory")
            
    except Exception as e:
        console.print(f"❌ [red]Error during initialization: {e}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


@cli.command("quick-start")
@click.option('--repos', help='Comma-separated list of repository paths to discover')
@click.option('--web', is_flag=True, help='Launch web UI after setup')
@click.pass_context
def quick_start(ctx, repos: Optional[str], web: bool):
    """Set up mem8 with intelligent defaults in 30 seconds."""
    console.print("🚀 [bold blue]Setting up mem8 with smart defaults...[/bold blue]")
    
    try:
        # 1. Auto-detect project context
        console.print("🔍 [dim]Detecting project context...[/dim]")
        project_info = detect_project_context()
        
        # Show discovered information
        if project_info['git_repos']:
            console.print(f"✅ Found {len(project_info['git_repos'])} git repositories")
            for repo in project_info['git_repos'][:3]:  # Show first 3
                indicator = " (has thoughts)" if repo.get('has_thoughts') else ""
                console.print(f"  • {repo['name']}{indicator}")
            if len(project_info['git_repos']) > 3:
                console.print(f"  • ... and {len(project_info['git_repos']) - 3} more")
        
        if project_info['is_claude_code_project']:
            console.print("✅ Claude Code project detected")
        
        # 2. Generate minimal configuration
        console.print("⚙️  [dim]Generating configuration...[/dim]")
        config = generate_smart_config(project_info, repos)
        
        console.print(f"👤 Username: {config['username']}")
        console.print(f"📁 Shared location: {config['shared_location']}")
        
        # 3. Create necessary directories
        console.print("📂 [dim]Creating directory structure...[/dim]")
        setup_results = setup_minimal_structure(config)
        
        # Show results
        if setup_results['created']:
            console.print("✅ [green]Created directories:[/green]")
            for created in setup_results['created']:
                console.print(f"  • {created}")
        
        if setup_results['linked']:
            console.print("🔗 [blue]Created links:[/blue]")
            for linked in setup_results['linked']:
                console.print(f"  • {linked}")
        
        if setup_results['errors']:
            console.print("⚠️  [yellow]Warnings:[/yellow]")
            for error in setup_results['errors']:
                console.print(f"  • {error}")
        
        # 4. Set up Claude Code integration if applicable
        if project_info['is_claude_code_project']:
            console.print("🔧 [dim]Setting up Claude Code integration...[/dim]")
            claude_results = setup_claude_code_integration(config)
            
            if claude_results['updated']:
                console.print("✅ [green]Updated Claude integration:[/green]")
                for updated in claude_results['updated']:
                    console.print(f"  • {updated}")
            
            if claude_results['created']:
                console.print("✅ [green]Created Claude integration:[/green]")
                for created in claude_results['created']:
                    console.print(f"  • {created}")
        
        # 5. Launch web UI if requested
        if web:
            console.print("🌐 [dim]Launching web UI...[/dim]")
            if launch_web_ui():
                console.print("✅ [green]mem8 UI opened in your browser![/green]")
            else:
                console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
                instructions = show_setup_instructions()
                console.print(instructions)
        
        # Show next steps
        console.print("\n🎉 [bold green]Quick setup complete![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  • Run [cyan]mem8 status[/cyan] to check workspace health")
        console.print("  • Run [cyan]mem8 search <query>[/cyan] to search your thoughts")
        console.print("  • Use [cyan]mem8 quick-start --web[/cyan] to launch the web UI")
        if not project_info['is_claude_code_project']:
            console.print("  • Run [cyan]mem8 init --template claude-config[/cyan] to add Claude Code integration")
        
        console.print(f"\n💡 [dim]Tip: Your thoughts are in [cyan]thoughts/{config['username']}/[/cyan] and shared thoughts in [cyan]thoughts/shared/[/cyan][/dim]")
            
    except Exception as e:
        console.print(f"❌ [red]Error during quick setup: {e}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


@cli.command()
def dashboard():
    """Launch mem8 web dashboard."""
    console.print("🌐 [bold blue]Launching mem8 dashboard...[/bold blue]")
    
    if launch_web_ui():
        console.print("✅ [green]Dashboard opened in your browser![/green]")
        console.print("💡 [dim]Use 'mem8 status' to check backend health.[/dim]")
    else:
        console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
        instructions = show_setup_instructions()
        console.print(instructions)


@cli.command()
@click.option('--team', help='Team name for deployment')
@click.option('--backend', is_flag=True, help='Deploy backend services')
@click.option('--frontend', is_flag=True, help='Deploy frontend')
@click.option('--all', is_flag=True, help='Deploy full stack')
@click.pass_context
def bootstrap(ctx, team: Optional[str], backend: bool, frontend: bool, all: bool):
    """Bootstrap mem8 for team deployment."""
    console.print("🚀 [bold blue]Bootstrapping mem8 for team deployment...[/bold blue]")
    
    if all:
        backend = frontend = True
    
    try:
        # 1. Ensure workspace is set up
        console.print("📂 [dim]Setting up workspace...[/dim]")
        project_info = detect_project_context()
        config = generate_smart_config(project_info, None)
        setup_results = setup_minimal_structure(config)
        
        # 2. Set up Claude Code integration
        if project_info['is_claude_code_project']:
            console.print("🔧 [dim]Configuring Claude Code integration...[/dim]")
            claude_results = setup_claude_code_integration(config)
            if claude_results['updated'] or claude_results['created']:
                console.print("✅ Claude Code integration configured")
        
        # 3. Backend deployment preparation
        if backend:
            console.print("🛠️  [dim]Preparing backend deployment...[/dim]")
            console.print("ℹ️  [yellow]Backend deployment requires:[/yellow]")
            console.print("  • Docker and docker-compose installed")
            console.print("  • GitHub OAuth app configured")
            console.print("  • Environment variables set (.env file)")
            console.print("  • Run: [cyan]docker-compose up -d[/cyan] to start services")
        
        # 4. Frontend deployment preparation  
        if frontend:
            console.print("🎨 [dim]Preparing frontend deployment...[/dim]")
            console.print("ℹ️  [yellow]Frontend deployment requires:[/yellow]")
            console.print("  • Node.js 18+ installed")
            console.print("  • Environment variables set (.env.local)")
            console.print("  • Run: [cyan]cd frontend && npm install && npm run build[/cyan]")
        
        # 5. Team setup
        if team:
            console.print(f"👥 [dim]Setting up team: {team}...[/dim]")
            console.print("ℹ️  [yellow]Team setup includes:[/yellow]")
            console.print(f"  • Shared directory configured for team '{team}'")
            console.print("  • GitHub OAuth configured for team members")
            console.print("  • Database initialized with team structure")
        
        console.print("\n🎉 [bold green]Bootstrap complete![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  • Configure environment variables")
        console.print("  • Start services with [cyan]docker-compose up -d[/cyan]")
        console.print("  • Invite team members to GitHub OAuth app")
        console.print("  • Share the web interface URL with team")
        
    except Exception as e:
        console.print(f"❌ [red]Bootstrap failed: {e}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


@cli.command()
@click.option(
    "--direction", 
    type=click.Choice(['pull', 'push', 'both']), 
    default='both',
    help="Sync direction"
)
@click.option(
    "--dry-run", 
    is_flag=True, 
    help="Show what would be synced without making changes"
)
@click.pass_context
def sync(ctx, direction: str, dry_run: bool):
    """Synchronize local and shared memory."""
    sync_manager = ctx.obj['sync_manager']
    
    action = "Dry run:" if dry_run else "Syncing"
    console.print(f"[bold blue]{action} memory ({direction})...[/bold blue]")
    
    try:
        result = sync_manager.sync_memory(direction=direction, dry_run=dry_run)
        
        if result['success']:
            # Show sync summary
            table = Table(title="Sync Summary")
            table.add_column("Operation", style="cyan")
            table.add_column("Count", justify="right", style="green")
            
            for operation, count in result['summary'].items():
                if count > 0:
                    table.add_row(operation.title(), str(count))
            
            if table.rows:
                console.print(table)
            else:
                console.print("✅ [green]No changes needed - everything is up to date![/green]")
                
        else:
            console.print(f"❌ [red]Sync failed: {result['error']}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error during sync: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--detailed", 
    is_flag=True, 
    help="Show detailed status information"
)
@click.pass_context
def status(ctx, detailed: bool):
    """Show mem8 workspace status."""
    memory_manager = ctx.obj['memory_manager']
    
    console.print("[bold blue]mem8 Workspace Status[/bold blue]")
    
    try:
        status_info = memory_manager.get_status(detailed=detailed)
        
        # Basic status table
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
        
        # Sync status
        if status_info['sync_status']:
            sync_status = status_info['sync_status']
            console.print(f"\\nLast sync: {sync_status['last_sync'] or 'Never'}")
            console.print(f"Pending changes: {sync_status['pending_changes']}")
            
        # Detailed info
        if detailed and status_info.get('details'):
            console.print("\\n[bold]Detailed Information:[/bold]")
            for detail in status_info['details']:
                console.print(f"  • {detail}")
                
    except Exception as e:
        console.print(f"❌ [red]Error getting status: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("query", required=True)
@click.option(
    "--limit", 
    default=10, 
    help="Maximum number of results to return"
)
@click.option(
    "--type", 
    "content_type",
    type=click.Choice(['thoughts', 'memories', 'all']), 
    default='all',
    help="Type of content to search"
)
@click.option(
    "--method",
    type=click.Choice(['fulltext', 'semantic']),
    default='fulltext',
    help="Search method: fulltext or semantic"
)
@click.option(
    "--path",
    help="Restrict search to specific path"
)
@click.option(
    "--web", 
    is_flag=True, 
    help="Open results in web UI"
)
@click.pass_context  
def search(ctx, query: str, limit: int, content_type: str, method: str, path: str, web: bool):
    """Search through AI memory and thoughts."""
    # Handle web UI search
    if web and query:
        console.print(f"🌐 [bold blue]Opening search for '{query}' in web UI...[/bold blue]")
        # Open web UI with pre-populated search
        search_url = f'http://localhost:20040?search={urllib.parse.quote(query)}'
        if launch_web_ui():
            webbrowser.open(search_url)
            console.print("✅ [green]Search opened in web browser![/green]")
        else:
            console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
            instructions = show_setup_instructions()
            console.print(instructions)
        return
    
    # Traditional CLI search
    memory_manager = ctx.obj['memory_manager']
    
    search_method = f"[cyan]{method}[/cyan]" 
    console.print(f"[bold blue]Searching for: '{query}' ({search_method})[/bold blue]")
    
    if method == 'semantic':
        console.print("[yellow]⚠️  Semantic search requires sentence-transformers library[/yellow]")
    
    try:
        results = memory_manager.search_content(
            query=query,
            limit=limit,
            content_type=content_type,
            search_method=method,
            path_filter=path
        )
        
        if results['matches']:
            table = Table(title=f"Search Results ({len(results['matches'])} found)")
            table.add_column("Type", style="cyan", width=10)
            table.add_column("Title", style="green")
            table.add_column("Path", style="dim")
            table.add_column("Score", justify="right", style="yellow", width=8)
            
            for match in results['matches']:
                # Try to get relative path, fallback to full path
                try:
                    display_path = str(Path(match['path']).relative_to(Path.cwd()))
                except ValueError:
                    display_path = str(match['path'])
                
                table.add_row(
                    match['type'].title(),
                    match['title'][:50] + "..." if len(match['title']) > 50 else match['title'],
                    display_path,
                    f"{match['score']:.2f}"
                )
            
            console.print(table)
        else:
            console.print("❌ [yellow]No matches found[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [red]Error during search: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--auto-fix", 
    is_flag=True, 
    help="Attempt to automatically fix issues"
)
@click.pass_context
def doctor(ctx, auto_fix: bool):
    """Diagnose and fix mem8 workspace issues."""
    memory_manager = ctx.obj['memory_manager']
    
    console.print("[bold blue]Running mem8 diagnostics...[/bold blue]")
    
    try:
        diagnosis = memory_manager.diagnose_workspace(auto_fix=auto_fix)
        
        # Show issues
        if diagnosis['issues']:
            console.print("\\n⚠️  [bold yellow]Issues found:[/bold yellow]")
            for issue in diagnosis['issues']:
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_icon} {issue['description']}")
                if auto_fix and issue.get('fixed'):
                    console.print(f"    ✅ [green]Fixed automatically[/green]")
        
        # Show fixes applied
        if auto_fix and diagnosis['fixes_applied']:
            console.print("\\n✅ [bold green]Fixes applied:[/bold green]")
            for fix in diagnosis['fixes_applied']:
                console.print(f"  • {fix}")
        
        # Overall health
        health_score = diagnosis['health_score']
        if health_score >= 90:
            console.print(f"\\n✅ [bold green]Workspace health: Excellent ({health_score}%)[/bold green]")
        elif health_score >= 70:
            console.print(f"\\n⚠️  [bold yellow]Workspace health: Good ({health_score}%)[/bold yellow]")
        else:
            console.print(f"\\n❌ [bold red]Workspace health: Needs attention ({health_score}%)[/bold red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error during diagnosis: {e}[/red]")
        sys.exit(1)


@cli.group()
def team():
    """Team collaboration commands."""
    pass


@team.command()
@click.option("--name", required=True, help="Team name")
@click.option("--description", help="Team description")
@click.pass_context
def create(ctx, name: str, description: str):
    """Create a new team."""
    console.print(f"[bold blue]Creating team: {name}[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")
    console.print("For now, teams are managed locally through shared directories.")


@team.command()
@click.pass_context
def list(ctx):
    """List available teams."""
    console.print("[bold blue]Available teams:[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


@team.command()
@click.argument("team_name")
@click.pass_context
def join(ctx, team_name: str):
    """Join an existing team."""
    console.print(f"[bold blue]Joining team: {team_name}[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


@cli.group()
def deploy():
    """Deployment commands."""
    pass


@deploy.command()
@click.option(
    "--env", 
    type=click.Choice(['local', 'staging', 'production']),
    default='local',
    help="Deployment environment"
)
@click.option("--domain", help="Custom domain for deployment")
@click.option("--replicas", default=2, help="Number of replicas")
@click.pass_context
def kubernetes(ctx, env: str, domain: str, replicas: int):
    """Deploy mem8 to Kubernetes via orchestr8."""
    console.print(f"[bold blue]Deploying to {env} environment...[/bold blue]")
    console.print("[yellow]⚠️  Kubernetes deployment requires Phase 4 implementation[/yellow]")
    console.print("Available after backend API and frontend are implemented.")


@deploy.command()
@click.option("--port", default=8000, help="Port to run on")
@click.pass_context
def local(ctx, port: int):
    """Start local development server."""
    console.print(f"[bold blue]Starting local server on port {port}...[/bold blue]")
    console.print("[yellow]⚠️  Local server requires backend API (Phase 2)[/yellow]")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()