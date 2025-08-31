# Claude Code Integration and Easy Onboarding Implementation Plan

## Overview

Transform AI-Mem from a complex multi-template CLI tool into a streamlined, Claude Code-integrated memory management platform that makes it trivially easy for developers to get started with AI memory management and visualization across multiple repositories.

## Current State Analysis

### What Exists Now:
- **Complex CLI Setup**: 3 template choices (claude-config, thoughts-repo, full) with extensive cookiecutter configuration
- **Multi-Repository Support**: Git worktree integration via templates but requires manual setup
- **Terminal UI**: Beautiful web interface at localhost:20040 with real-time collaboration
- **Claude Code Templates**: Existing agent definitions and command workflows in claude-dot-md-template

### Key Constraints Discovered:
- **High Barrier to Entry**: New users must understand cookiecutter, templates, and shared directory concepts
- **Configuration Complexity**: 10+ auto-detection paths, network drive assumptions, platform differences
- **Manual Multi-Repo Setup**: No automatic discovery of orchestr8/agenticinsights repositories
- **Disconnected Experience**: CLI, web UI, and Claude Code workflows are separate tools

## Desired End State

### Target User Experience:
```bash
# From any Claude Code project directory
claude
> /setup-memory
# AI-Mem automatically discovers local repos, sets up integration, launches UI

# Or standalone
cd ~/projects/my-project
ai-mem quick-start
# Guided 30-second setup with immediate thoughts visualization
```

### Success Verification:
- New users can get thoughts visualization working in under 60 seconds
- Claude Code users can access AI-Mem through natural slash commands
- Thoughts from multiple repositories (ai-mem, orchestr8, agenticinsights) appear in unified UI
- Zero manual configuration needed for common developer setups

## What We're NOT Doing

- Removing cookiecutter templates (maintain backward compatibility)
- Changing existing database schema or API endpoints
- Modifying core synchronization logic
- Breaking existing team collaboration workflows
- Supporting non-git repositories initially

## Implementation Approach

**Strategy**: Progressive enhancement with backward compatibility. Add streamlined onboarding flows while preserving existing functionality. Integrate with Claude Code's memory hierarchy to provide seamless developer experience.

## Phase 1: Streamlined Quick-Start Flow

### Overview
Replace complex template selection with intelligent defaults and guided setup for new users.

### Changes Required:

#### 1. New CLI Command: `ai-mem quick-start`
**File**: `ai_mem/cli.py`
**Changes**: Add quick-start command that bypasses cookiecutter complexity

```python
@cli.command()
@click.option('--repos', help='Comma-separated list of repository paths to discover')
@click.option('--web', is_flag=True, help='Launch web UI after setup')
def quick_start(repos, web):
    """Set up AI-Mem with intelligent defaults in 30 seconds."""
    console.print("🚀 Setting up AI-Mem with smart defaults...")
    
    # 1. Auto-detect project context
    project_info = detect_project_context()
    
    # 2. Generate minimal configuration
    config = generate_smart_config(project_info, repos)
    
    # 3. Create necessary directories
    setup_minimal_structure(config)
    
    # 4. Launch web UI if requested
    if web:
        launch_web_ui()
```

#### 2. Project Context Detection
**File**: `ai_mem/core/smart_setup.py` (new)
**Changes**: Intelligent project analysis and configuration generation

```python
def detect_project_context():
    """Detect project type, git repos, and optimal configuration."""
    context = {
        'is_claude_code_project': Path('.claude').exists(),
        'git_repos': discover_local_repositories(),
        'project_type': infer_project_type(),
        'username': get_git_username(),
        'shared_location': find_optimal_shared_location()
    }
    return context

def discover_local_repositories():
    """Find all git repositories in parent and sibling directories."""
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    repos = []
    # Search current directory
    repos.extend(find_git_repos(current_dir))
    # Search sibling directories (orchestr8, agenticinsights, etc.)
    repos.extend(find_git_repos(parent_dir, max_depth=2))
    
    return repos
```

#### 3. Minimal Directory Structure Setup
**File**: `ai_mem/core/smart_setup.py`
**Changes**: Create essential directories without cookiecutter overhead

```python
def setup_minimal_structure(config):
    """Create minimal AI-Mem structure with smart defaults."""
    # Create thoughts directory
    thoughts_dir = Path('thoughts')
    thoughts_dir.mkdir(exist_ok=True)
    
    # Create shared symlink or junction
    shared_dir = thoughts_dir / 'shared'
    if not shared_dir.exists():
        create_shared_link(shared_dir, config['shared_location'])
    
    # Create user directory
    user_dir = thoughts_dir / config['username']
    user_dir.mkdir(exist_ok=True)
    
    # Create basic structure
    for subdir in ['research', 'plans', 'tickets', 'notes']:
        (user_dir / subdir).mkdir(exist_ok=True)
```

#### 4. Web UI Auto-Launch
**File**: `ai_mem/cli.py`
**Changes**: Add web UI launch capability

```python
def launch_web_ui():
    """Launch web UI if backend is running, otherwise provide instructions."""
    try:
        response = requests.get('http://localhost:8000/api/v1/health', timeout=2)
        if response.status_code == 200:
            webbrowser.open('http://localhost:20040')
            console.print("🌐 AI-Mem UI opened in your browser!")
        else:
            show_setup_instructions()
    except requests.RequestException:
        show_setup_instructions()
```

### Success Criteria:

#### Automated Verification:
- [x] `ai-mem quick-start` completes successfully: `ai-mem quick-start && ls thoughts`
- [x] Generated structure is valid: `ai-mem status` reports healthy workspace
- [x] Multi-repo discovery works: `ai-mem quick-start --repos ../orchestr8,../agenticinsights`
- [x] Web launch succeeds when backend running: Backend health check returns 200

#### Manual Verification:
- [x] New user can complete setup in under 60 seconds
- [x] Generated thoughts directory structure is intuitive
- [x] Web UI launches correctly and shows discovered repositories
- [x] No cookiecutter knowledge required

---

## Phase 2: Claude Code Integration

### Overview
Create native Claude Code slash commands and memory integration for AI-Mem functionality.

### Changes Required:

#### 1. Claude Code Commands Template
**File**: `claude-dot-md-template/{{cookiecutter.project_slug}}/commands/setup-memory.md`
**Changes**: Add AI-Mem setup command for Claude Code users

```markdown
---
allowed-tools: Bash(ai-mem:*), Bash(git:*), Bash(mkdir:*) 
argument-hint: [--repos repo1,repo2] [--web]
description: Set up AI memory management with multi-repo discovery
---

# AI Memory Setup

Set up AI-Mem memory management for this project and discover related repositories.

## Setup Process

1. Check if AI-Mem is installed:
!`which ai-mem || echo "AI-Mem not found - install with: uv tool install ai-mem"`

2. Run quick setup:
!`ai-mem quick-start $ARGUMENTS`

3. Verify setup:
!`ai-mem status`

## Next Steps

- Use `ai-mem search "query"` to find thoughts across repositories
- Launch web UI with `ai-mem quick-start --web` for visual exploration
- Sync thoughts across team with `ai-mem sync`
```

#### 2. Memory Browser Command  
**File**: `claude-dot-md-template/{{cookiecutter.project_slug}}/commands/browse-memories.md`
**Changes**: Interactive memory exploration

```markdown
---
allowed-tools: Bash(ai-mem:*)
description: Browse and search AI memories across repositories
---

# Browse AI Memories

Explore thoughts and memories across your repositories.

## Recent Memories
!`ai-mem search --recent --limit 10`

## Repository Status
!`ai-mem status --repos`

## Interactive Search
Use `ai-mem search "your query"` to find specific thoughts across all configured repositories.

Launch the web UI for visual exploration: `ai-mem quick-start --web`
```

#### 3. AI-Mem Project Memory Integration
**File**: `ai_mem/claude_integration.py` (new)  
**Changes**: Generate CLAUDE.md additions for AI-Mem projects

```python
def generate_claude_memory_integration(config):
    """Generate CLAUDE.md content for AI-Mem integration."""
    repos_config = "\n".join([
        f"- {repo['name']}: {repo['thoughts_path']}" 
        for repo in config.get('repositories', [])
    ])
    
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

## Shared Thoughts Location
Shared thoughts: `{config.get('shared_location', 'thoughts/shared/')}`

## Workflow Integration  
- Research documents: `thoughts/shared/research/`
- Implementation plans: `thoughts/shared/plans/` 
- PR discussions: `thoughts/shared/prs/`
"""
    return claude_md_content
```

#### 4. CLAUDE.md Auto-Update
**File**: `ai_mem/cli.py`  
**Changes**: Automatically update CLAUDE.md when quick-start runs in Claude Code project

```python
def update_claude_md_integration(config):
    """Add AI-Mem integration section to existing CLAUDE.md."""
    claude_md = Path('.claude/CLAUDE.md')
    if claude_md.exists():
        content = claude_md.read_text()
        if 'AI Memory Integration' not in content:
            integration = generate_claude_memory_integration(config)
            content += f"\n\n{integration}"
            claude_md.write_text(content)
            console.print("✅ Updated .claude/CLAUDE.md with AI-Mem integration")
```

### Success Criteria:

#### Automated Verification:
- [x] Claude Code commands install correctly: `.claude/commands/setup-memory.md` exists
- [x] Commands execute without errors: `claude` session can run `/setup-memory`
- [x] CLAUDE.md integration works: File contains "AI Memory Integration" section
- [x] Memory browsing functional: `/browse-memories` returns recent thoughts

#### Manual Verification:
- [x] Claude Code users can discover and use AI-Mem through natural slash commands
- [x] Memory integration feels native within Claude Code workflow
- [x] Commands provide helpful output and next steps
- [x] Integration doesn't interfere with existing Claude Code functionality

---

## Phase 3: Multi-Repository Discovery and Visualization

### Overview  
Enhance frontend to automatically discover and visualize thoughts from multiple repositories (orchestr8, agenticinsights, ai-mem).

### Changes Required:

#### 1. Repository Discovery Service
**File**: `backend/src/aimem_api/services/repository_discovery.py` (new)
**Changes**: Automatic repository discovery and thoughts aggregation

```python
class RepositoryDiscoveryService:
    def discover_repositories(self, base_paths: List[Path]) -> List[RepoConfig]:
        """Discover git repositories and their thoughts directories."""
        repos = []
        for base_path in base_paths:
            for repo_path in base_path.rglob('.git'):
                if repo_path.is_dir():
                    repo_info = self.analyze_repository(repo_path.parent)
                    if repo_info:
                        repos.append(repo_info)
        return repos
    
    def analyze_repository(self, repo_path: Path) -> Optional[RepoConfig]:
        """Analyze repository for thoughts configuration."""
        # Check for thoughts directories
        thoughts_paths = [
            repo_path / 'thoughts',
            repo_path / 'docs' / 'thoughts', 
            repo_path / 'thoughts' / 'shared'
        ]
        
        for thoughts_path in thoughts_paths:
            if thoughts_path.exists():
                return RepoConfig(
                    name=repo_path.name,
                    path=repo_path,
                    thoughts_path=thoughts_path,
                    git_remote=self.get_git_remote(repo_path)
                )
        return None
```

#### 2. Multi-Repo API Endpoints
**File**: `backend/src/aimem_api/routers/repositories.py` (new)
**Changes**: API endpoints for repository management

```python
@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all discovered repositories with thoughts."""
    discovery_service = RepositoryDiscoveryService()
    
    # Get configured base paths from user settings
    base_paths = await get_user_repository_paths(current_user.id, db)
    
    # Discover repositories
    repos = discovery_service.discover_repositories(base_paths)
    
    return [RepositoryResponse.from_config(repo) for repo in repos]

@router.post("/repositories/sync")
async def sync_repositories(
    sync_request: RepositorySyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync thoughts from multiple repositories."""
    # Implementation for cross-repo sync
    pass
```

#### 3. Frontend Repository Selector
**File**: `frontend/components/RepositorySelector.tsx` (new)
**Changes**: UI component for repository selection and filtering

```typescript
export function RepositorySelector({ onRepositoryChange, selectedRepos }: RepositorySelectorProps) {
  const { data: repositories } = useRepositories();
  
  return (
    <div className="repository-selector">
      <h3 className="text-sm font-medium mb-2">Repositories</h3>
      <div className="space-y-1">
        {repositories?.map(repo => (
          <div key={repo.id} className="flex items-center space-x-2">
            <Checkbox 
              checked={selectedRepos.includes(repo.id)}
              onCheckedChange={(checked) => onRepositoryChange(repo.id, checked)}
            />
            <span className="text-xs font-mono">{repo.name}</span>
            <Badge variant="outline" className="text-xs">
              {repo.thoughtCount} thoughts
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 4. Enhanced Dashboard with Multi-Repo Support
**File**: `frontend/app/page.tsx`
**Changes**: Integrate repository selector and multi-repo thought display

```typescript
// Add repository state management
const [selectedRepositories, setSelectedRepositories] = useState<string[]>([]);
const { data: repositories } = useRepositories();

// Update thoughts query to include repository filter
const { data: thoughts } = useThoughts({
  team_id: selectedTeamId,
  repository_ids: selectedRepositories,
  search_query: searchQuery,
  search_type: searchType
});

// Add repository selector to sidebar
<RepositorySelector 
  selectedRepos={selectedRepositories}
  onRepositoryChange={(repoId, checked) => {
    setSelectedRepositories(prev => 
      checked 
        ? [...prev, repoId]
        : prev.filter(id => id !== repoId)
    );
  }}
/>
```

#### 5. Repository-Aware Thought Cards
**File**: `frontend/components/ThoughtCard.tsx` (new)
**Changes**: Enhanced thought display with repository context

```typescript
export function ThoughtCard({ thought }: { thought: ThoughtWithRepository }) {
  return (
    <div className="memory-cell p-4 rounded-lg hover:scale-[1.02] transition-all cursor-pointer">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-base">{thought.title}</h3>
        <div className="flex gap-1">
          <Badge variant="terminal">{thought.team}</Badge>
          <Badge variant="outline" className="text-xs">
            {thought.repository.name}
          </Badge>
        </div>
      </div>
      <p className="text-sm text-muted-foreground mb-3">{thought.excerpt}</p>
      <div className="flex items-center justify-between text-xs">
        <span className="font-mono">{thought.path}</span>
        <span>{thought.lastModified}</span>
      </div>
      {thought.tags && (
        <div className="flex flex-wrap gap-1 mt-2">
          {thought.tags.map(tag => <Badge key={tag} variant="outline">{tag}</Badge>)}
        </div>
      )}
    </div>
  );
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Repository discovery API works: `curl localhost:8000/api/v1/repositories` returns discovered repos
- [ ] Multi-repo thoughts query functions: API returns thoughts filtered by repository
- [ ] Frontend components render without errors: `npm run build` succeeds
- [ ] Repository sync triggers correctly: Sync endpoint processes multiple repositories

#### Manual Verification:
- [ ] UI shows thoughts from ai-mem, orchestr8, and agenticinsights repositories
- [ ] Repository filtering works smoothly in the interface
- [ ] Thought cards clearly indicate source repository
- [ ] Cross-repository search returns relevant results from all sources
- [ ] Repository discovery finds new repos when added to base paths

---

## Phase 4: Enhanced Developer Experience

### Overview
Polish the integration with advanced features for power users and better mobile experience.

### Changes Required:

#### 1. CLI Integration with Web UI
**File**: `ai_mem/cli.py`
**Changes**: Enhanced CLI commands with web UI integration

```python
@cli.command()
@click.option('--query', help='Search query')
@click.option('--web', is_flag=True, help='Open results in web UI')
def search(query, web):
    """Search across all configured repositories."""
    if web and query:
        # Open web UI with pre-populated search
        webbrowser.open(f'http://localhost:20040?search={urllib.parse.quote(query)}')
    else:
        # Traditional CLI search
        results = perform_search(query)
        display_search_results(results)

@cli.command()
def dashboard():
    """Launch AI-Mem web dashboard."""
    launch_web_ui()
    console.print("Dashboard launched! Use 'ai-mem status' to check backend health.")
```

#### 2. URL-based State Management
**File**: `frontend/hooks/useUrlState.ts` (new)
**Changes**: Support deep linking and shareable search URLs

```typescript
export function useUrlState() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  return {
    searchQuery: searchParams.get('search') || '',
    selectedTeam: searchParams.get('team'),
    selectedRepos: searchParams.get('repos')?.split(',') || [],
    
    updateSearch: (query: string) => {
      const params = new URLSearchParams(searchParams);
      if (query) {
        params.set('search', query);
      } else {
        params.delete('search');
      }
      setSearchParams(params);
    },
    
    updateFilters: (team?: string, repos?: string[]) => {
      const params = new URLSearchParams(searchParams);
      if (team) params.set('team', team);
      if (repos?.length) params.set('repos', repos.join(','));
      setSearchParams(params);
    }
  };
}
```

#### 3. Keyboard Shortcuts
**File**: `frontend/hooks/useKeyboardShortcuts.ts` (new)
**Changes**: Power user keyboard navigation

```typescript
export function useKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K for search focus
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector('[data-search-input]')?.focus();
      }
      
      // Cmd/Ctrl + D for dashboard
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        // Navigate to dashboard view
      }
      
      // Escape to clear search
      if (e.key === 'Escape') {
        const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
        if (searchInput && document.activeElement === searchInput) {
          searchInput.blur();
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
}
```

#### 4. Mobile-Responsive Design
**File**: `frontend/app/page.tsx`
**Changes**: Responsive layout with mobile-first design

```typescript
// Replace fixed sidebar with responsive drawer
const [sidebarOpen, setSidebarOpen] = useState(false);

return (
  <div className="flex h-screen bg-background">
    {/* Mobile sidebar overlay */}
    {sidebarOpen && (
      <div className="fixed inset-0 z-50 lg:hidden">
        <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
        <div className="absolute left-0 top-0 h-full w-80 bg-background border-r">
          <Sidebar onClose={() => setSidebarOpen(false)} />
        </div>
      </div>
    )}
    
    {/* Desktop sidebar */}
    <div className="hidden lg:flex lg:w-80 lg:flex-col">
      <Sidebar />
    </div>
    
    {/* Main content */}
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Mobile header */}
      <div className="lg:hidden flex items-center justify-between p-4 border-b">
        <button onClick={() => setSidebarOpen(true)}>
          <MenuIcon size={20} />
        </button>
        <h1 className="font-mono text-lg">AI-Mem</h1>
        <div /> {/* Spacer */}
      </div>
      
      {/* Content area with responsive grid */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {thoughts?.map(thought => <ThoughtCard key={thought.id} thought={thought} />)}
        </div>
      </div>
    </div>
  </div>
);
```

### Success Criteria:

#### Automated Verification:
- [ ] CLI web integration works: `ai-mem search "test" --web` opens browser
- [ ] URL state management functional: URLs contain search/filter parameters
- [ ] Keyboard shortcuts register: Browser dev tools show no event listener errors
- [ ] Mobile layout renders correctly: `npm run build` generates responsive CSS

#### Manual Verification:
- [ ] Keyboard shortcuts work smoothly (Cmd+K for search, Escape to clear)
- [ ] Mobile interface is usable on phone/tablet devices
- [ ] URL sharing works (copy/paste URL preserves search state)
- [ ] CLI dashboard command launches web UI successfully
- [ ] Deep links from CLI search open web UI with correct filters

---

## Testing Strategy

### Unit Tests:
- Repository discovery logic with various directory structures
- Configuration generation for different project types
- Claude Code memory integration content generation
- API endpoints for multi-repository operations

### Integration Tests:
- Complete quick-start flow from fresh directory
- Multi-repository sync operations
- Claude Code command execution in actual project
- Web UI state management with URL parameters

### Manual Testing Steps:
1. **New User Flow**: Start in empty directory, run `ai-mem quick-start`, verify setup
2. **Claude Code Integration**: Use `/setup-memory` in Claude session, check CLAUDE.md updates
3. **Multi-Repo Discovery**: Place in ~/projects with orchestr8/agenticinsights, verify discovery
4. **Mobile Experience**: Test responsive design on actual mobile devices
5. **Cross-Repository Search**: Search for terms that exist across multiple repos

## Performance Considerations

- **Repository Discovery**: Limit scanning depth to avoid performance issues on large filesystems
- **Thought Indexing**: Implement incremental indexing for large repositories
- **Frontend Pagination**: Add virtual scrolling for repositories with thousands of thoughts
- **Cache Strategy**: Cache repository discovery results with filesystem watching for changes

## Migration Notes

- **Backward Compatibility**: Existing cookiecutter-based setups continue to work unchanged
- **Configuration Migration**: Automatic detection and upgrade of legacy configurations
- **Data Preservation**: All existing thoughts and shared directories remain untouched
- **Gradual Adoption**: Teams can adopt new quick-start flow while maintaining existing workflows

## References

- Research document: `thoughts/shared/research/2025-08-30_12-05-35_thoughts-system-multi-repo-integration.md`
- Claude Code memory documentation: claude-code-docs/docs/memory.md
- Claude Code slash commands: claude-code-docs/docs/slash-commands.md
- Current CLI implementation: `ai_mem/cli.py:101-246`
- Frontend visualization: `frontend/app/page.tsx:13-492`
- Template system: `shared-thoughts-template/cookiecutter.json`