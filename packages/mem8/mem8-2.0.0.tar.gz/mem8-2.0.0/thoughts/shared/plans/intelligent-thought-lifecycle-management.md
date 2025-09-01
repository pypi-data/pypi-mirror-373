# Intelligent Thought Lifecycle Management Implementation Plan

## Overview

Transform mem8 from a basic search tool into an **Semantic Memory Operating System** that understands thought entities, their lifecycles, relationships, and enables intelligent actions like deletion, archival, and promotion. This implements the crucial "dogfooding" use case of using mem8 to manage mem8's own development artifacts with semantic understanding.

## Current State Analysis

### What Exists Now:
- **Basic Search**: `mem8 search <query>` with fulltext/semantic matching in thoughts/ and memory files
- **Rich Metadata**: YAML frontmatter with date, status, tags, topic, researcher, git_commit, repository
- **Directory Organization**: `thoughts/shared/{plans,research,prs}/` and `thoughts/{username}/`
- **Web Integration**: `--web` flag opens results in browser UI
- **No Action Capabilities**: Cannot delete, archive, or manipulate found thoughts

### Key Discoveries:
- YAML frontmatter already contains lifecycle metadata (`status: complete`, `tags: [research, implementation]`)
- Thought organization follows semantic patterns (`plans/`, `research/`, `prs/`)
- Cross-repository discovery is partially implemented via `quick-start --repos`
- Search scoring is simplistic (term frequency) with no relationship understanding

## Desired End State

### Target User Experience:
```bash
# Intelligent search with semantic understanding
mem8 find "completed plans"  # understands status:complete AND type:plan
mem8 find "template packaging"  # fuzzy content + relationship matching

# Safe lifecycle actions with confirmation
mem8 find "completed plans older than 30d" --action archive --dry-run
mem8 delete "include-templates-in-wheel-distribution"  # with backup/confirmation

# Scope-aware operations
mem8 promote local-research "new-algorithm" to shared
mem8 cleanup stale-research --auto-detect --dry-run

# AI-powered insights  
mem8 analyze-completion "claude-code-integration"
mem8 status --thoughts --relationships
```

### Success Verification:
- Users can find thoughts using natural language queries
- Destructive operations are safe with backups and dry-run mode
- Thought relationships are understood and leveraged
- Completion status is auto-detected from implementation evidence
- Cross-repository thought management works seamlessly

## What We're NOT Doing

- Not changing existing YAML frontmatter format (backward compatible)
- Not modifying current directory structure or file naming conventions  
- Not implementing complex AI/ML models initially (start with heuristics)
- Not breaking existing `mem8 search` functionality (extend, don't replace)
- Not implementing collaborative editing or real-time sync initially

## Implementation Approach

**Strategy**: Build a **Semantic Layer** on top of existing search infrastructure. Implement **Thought Entity Recognition**, **Intelligent Query Processing**, and **Safe Action Execution** with progressive intelligence enhancement.

## Phase 1: Thought Entity Recognition System

### Overview
Create the foundation for understanding thoughts as semantic entities with type, scope, lifecycle, and relationships rather than just files.

### Changes Required:

#### 1. ThoughtEntity Data Model
**File**: `mem8/core/thought_entity.py` (new)
**Changes**: Core data model for semantic thought understanding

```python
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
                metadata = yaml.safe_load(yaml_content)
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
```

#### 2. Thought Discovery Service
**File**: `mem8/core/thought_discovery.py` (new)  
**Changes**: Service to discover and index all thought entities

```python
class ThoughtDiscoveryService:
    """Discovers and indexes thought entities across repositories."""
    
    def __init__(self, config: Config):
        self.config = config
        self._entity_cache = {}
        self._last_scan = None
        
    def discover_all_thoughts(self, force_rescan: bool = False) -> List[ThoughtEntity]:
        """Discover all thought entities across all configured repositories."""
        if not force_rescan and self._entity_cache and self._is_cache_fresh():
            return list(self._entity_cache.values())
            
        entities = []
        
        # Scan local thoughts
        thoughts_dir = self.config.thoughts_dir
        if thoughts_dir.exists():
            entities.extend(self._scan_directory(thoughts_dir))
            
        # Scan cross-repository thoughts  
        discovered_repos = self._discover_repositories()
        for repo_path in discovered_repos:
            repo_thoughts_dir = repo_path / 'thoughts'
            if repo_thoughts_dir.exists():
                entities.extend(self._scan_directory(repo_thoughts_dir, repo_name=repo_path.name))
        
        # Update cache
        self._entity_cache = {entity.path: entity for entity in entities}
        self._last_scan = time.time()
        
        return entities
        
    def _scan_directory(self, directory: Path, repo_name: str = None) -> List[ThoughtEntity]:
        """Scan directory for thought files."""
        entities = []
        for md_file in directory.rglob("*.md"):
            if md_file.is_file():
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
```

#### 3. Integration with Existing MemoryManager  
**File**: `mem8/core/memory.py`
**Changes**: Extend MemoryManager to use ThoughtEntity system

```python
# Add import at top
from .thought_entity import ThoughtEntity
from .thought_discovery import ThoughtDiscoveryService

class MemoryManager:
    # ... existing code ...
    
    def __init__(self, config: Config):
        self.config = config
        self.thought_discovery = ThoughtDiscoveryService(config)  # Add this
        
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
```

### Success Criteria:

#### Automated Verification:
- [x] ThoughtEntity can parse existing YAML frontmatter: `python -c "from mem8.core.thought_entity import ThoughtEntity; print(ThoughtEntity.from_file(Path('thoughts/shared/plans/include-templates-in-wheel-distribution.md')))"`
- [x] Discovery service finds all thought files: `mem8.core.thought_discovery.discover_all_thoughts()`
- [x] Type classification works correctly: Test with plans/, research/, prs/ files
- [x] Scope detection identifies personal vs shared: Test path parsing logic

#### Manual Verification:
- [x] Thought entities contain all expected metadata from YAML frontmatter
- [x] Type classification accurately identifies plans, research, PR discussions
- [x] Lifecycle analysis correctly identifies completed vs active thoughts
- [x] No performance degradation when scanning large thought directories

---

## Phase 2: Intelligent Query Engine

### Overview
Build natural language query processing that understands intent and maps to semantic thought searches.

### Changes Required:

#### 1. Query Parsing and Intent Recognition
**File**: `mem8/core/intelligent_query.py` (new)
**Changes**: Natural language query processing with intent understanding

```python
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class QueryIntent:
    """Represents parsed intent from natural language query."""
    query_type: str  # 'find', 'list', 'show'
    target_type: Optional[str] = None  # 'plans', 'research', etc.
    status_filter: Optional[str] = None  # 'completed', 'active', etc. 
    scope_filter: Optional[str] = None  # 'shared', 'personal', etc.
    content_query: Optional[str] = None  # Actual search terms
    time_filter: Optional[str] = None  # 'older than 30d', 'recent', etc.
    relationship_filter: Optional[str] = None  # 'related to X', 'implements Y'

class IntelligentQueryEngine:
    """Processes natural language queries with semantic understanding."""
    
    # Intent pattern matching
    PATTERNS = {
        'completed_plans': r'completed?\s+plans?',
        'active_research': r'active|current|ongoing.*research',
        'stale_content': r'stale|old|outdated|obsolete', 
        'recent_content': r'recent|new|latest',
        'time_bounded': r'(older|newer)\s+than\s+(\d+)\s*(d|days?|w|weeks?|m|months?)',
        'type_specific': r'(plans?|research|tickets?|prs?|decisions?)',
        'scope_specific': r'(shared|personal|team)',
        'status_specific': r'(completed?|active|draft|failed|obsolete)',
    }
    
    def __init__(self, thought_discovery: ThoughtDiscoveryService):
        self.thought_discovery = thought_discovery
        
    def parse_query(self, query: str) -> QueryIntent:
        """Parse natural language query into structured intent."""
        query_lower = query.lower().strip()
        
        intent = QueryIntent(query_type='find')  # Default
        
        # Extract type filter
        for pattern_type, pattern in self.PATTERNS.items():
            match = re.search(pattern, query_lower)
            if match:
                if pattern_type == 'type_specific':
                    intent.target_type = match.group(1).rstrip('s')  # normalize plural
                elif pattern_type == 'status_specific':
                    intent.status_filter = match.group(1).rstrip('d')  # normalize past tense
                elif pattern_type == 'scope_specific':
                    intent.scope_filter = match.group(1)
                elif pattern_type == 'time_bounded':
                    intent.time_filter = f"{match.group(2)}{match.group(3)[0]}"  # "30d"
                elif pattern_type in ['completed_plans', 'active_research']:
                    # Combined patterns
                    if 'completed' in pattern_type:
                        intent.target_type = 'plan'
                        intent.status_filter = 'completed'
                    elif 'active' in pattern_type:
                        intent.target_type = 'research'
                        intent.status_filter = 'active'
        
        # Extract content query (remove matched patterns)
        content_query = query
        for pattern in self.PATTERNS.values():
            content_query = re.sub(pattern, '', content_query, flags=re.IGNORECASE)
        intent.content_query = content_query.strip()
        
        return intent
        
    def execute_query(self, intent: QueryIntent) -> List[ThoughtEntity]:
        """Execute parsed query intent against thought entities."""
        entities = self.thought_discovery.discover_all_thoughts()
        
        results = entities
        
        # Apply type filter
        if intent.target_type:
            results = [e for e in results if e.type == intent.target_type]
            
        # Apply status filter  
        if intent.status_filter:
            results = [e for e in results if e.lifecycle_state == intent.status_filter]
            
        # Apply scope filter
        if intent.scope_filter:
            results = [e for e in results if e.scope == intent.scope_filter]
            
        # Apply content filter
        if intent.content_query and intent.content_query.strip():
            content_results = []
            query_terms = intent.content_query.lower().split()
            for entity in results:
                # Search in title, content, and metadata
                searchable_text = (
                    entity.content.lower() + ' ' + 
                    str(entity.metadata.get('topic', '')).lower() + ' ' +
                    ' '.join(entity.metadata.get('tags', [])).lower()
                )
                
                # Simple term matching (can be enhanced with fuzzy matching)
                if any(term in searchable_text for term in query_terms):
                    content_results.append(entity)
                    
            results = content_results
        
        # Apply time filter (simplified implementation)
        if intent.time_filter:
            # Implementation would parse time filter and apply date comparisons
            pass
            
        return results
```

#### 2. Enhanced mem8 find Command  
**File**: `mem8/cli.py`
**Changes**: Replace basic search with intelligent query processing

```python
# Add import
from .core.intelligent_query import IntelligentQueryEngine

@cli.command()
@click.argument("query", required=True)
@click.option('--action', type=click.Choice(['show', 'delete', 'archive', 'promote']), help='Action to perform on found thoughts')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.option('--scope', type=click.Choice(['personal', 'shared', 'team', 'all']), default='all', help='Limit search scope')
@click.option('--type', type=click.Choice(['plan', 'research', 'ticket', 'pr', 'decision', 'all']), default='all', help='Limit to thought type')
@click.option('--limit', default=20, help='Maximum results to return')
@click.pass_context
def find(ctx, query: str, action: Optional[str], dry_run: bool, scope: str, type: str, limit: int):
    """Find thoughts using intelligent natural language queries."""
    memory_manager = ctx.obj['memory_manager']
    
    # Initialize intelligent query engine
    query_engine = IntelligentQueryEngine(memory_manager.thought_discovery)
    
    console.print(f"[bold blue]🔍 Finding: '{query}'[/bold blue]")
    if action:
        action_color = "yellow" if dry_run else "red" if action == "delete" else "cyan"
        dry_run_text = " (dry run)" if dry_run else ""
        console.print(f"[bold {action_color}]Action: {action}{dry_run_text}[/bold {action_color}]")
    
    try:
        # Parse natural language query
        intent = query_engine.parse_query(query)
        
        # Show parsed intent for debugging
        if ctx.obj['verbose']:
            console.print(f"[dim]Parsed intent: type={intent.target_type}, status={intent.status_filter}, content='{intent.content_query}'[/dim]")
        
        # Execute query
        results = query_engine.execute_query(intent)
        
        # Apply CLI filters (override intent if specified)
        if scope != 'all':
            results = [r for r in results if r.scope == scope]
        if type != 'all':
            results = [r for r in results if r.type == type]
            
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
            _execute_action(action, results, ctx)
        elif action and dry_run:
            _preview_action(action, results)
            
    except Exception as e:
        console.print(f"❌ [red]Error during search: {e}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)
```

### Success Criteria:

#### Automated Verification:
- [x] Query parsing correctly identifies intent: Test "completed plans", "active research", "template packaging"
- [x] Type and status filters work correctly: Test with various filter combinations
- [x] Content search finds relevant thoughts: Test fuzzy matching on existing files
- [x] Results are properly limited and formatted: Test with large result sets

#### Manual Verification:
- [x] Natural language queries feel intuitive and work as expected
- [x] Results are relevant and ranked appropriately
- [x] Verbose mode shows helpful debugging information
- [x] Performance is acceptable even with large thought collections

---

## Phase 3: Safe Action Execution Engine

### Overview
Implement safe action execution for destructive operations (delete, archive, promote) with comprehensive safety measures.

### Changes Required:

#### 1. Thought Action Engine
**File**: `mem8/core/thought_actions.py` (new)
**Changes**: Safe execution engine for thought lifecycle operations

```python
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

class ThoughtActionEngine:
    """Safely executes actions on thought entities with backup and audit."""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = config.data_dir / "thought_backups"
        self.audit_log = config.data_dir / "thought_audit.jsonl"
        self.ensure_backup_structure()
        
    def ensure_backup_structure(self):
        """Ensure backup and audit structure exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def delete_thoughts(self, entities: List[ThoughtEntity], dry_run: bool = False) -> Dict[str, Any]:
        """Safely delete thought entities with backup."""
        if dry_run:
            return self._preview_delete(entities)
            
        results = {
            'success': [],
            'errors': [],
            'backups': [],
        }
        
        for entity in entities:
            try:
                # Create backup before deletion
                backup_path = self._create_backup(entity, "delete")
                
                # Perform deletion
                entity.path.unlink()
                
                # Log the action
                self._log_action("delete", entity, backup_path=backup_path)
                
                results['success'].append(str(entity.path))
                results['backups'].append(str(backup_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
        
    def archive_thoughts(self, entities: List[ThoughtEntity], target_dir: Optional[Path] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Archive thought entities by moving to archive directory."""
        if dry_run:
            return self._preview_archive(entities, target_dir)
            
        # Determine archive location
        if not target_dir:
            target_dir = self.config.thoughts_dir / "archive"
            
        target_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': [],
            'errors': [],
            'archived_to': [],
        }
        
        for entity in entities:
            try:
                # Determine target path preserving directory structure
                rel_path = entity.path.relative_to(self.config.thoughts_dir)
                target_path = target_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(entity.path), str(target_path))
                
                # Log the action
                self._log_action("archive", entity, target_path=target_path)
                
                results['success'].append(str(entity.path))
                results['archived_to'].append(str(target_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
        
    def promote_thoughts(self, entities: List[ThoughtEntity], from_scope: str, to_scope: str, dry_run: bool = False) -> Dict[str, Any]:
        """Promote thoughts between scopes (personal <-> shared <-> team)."""
        if dry_run:
            return self._preview_promote(entities, from_scope, to_scope)
            
        results = {
            'success': [],
            'errors': [],
            'promoted_to': [],
        }
        
        for entity in entities:
            try:
                if entity.scope != from_scope:
                    results['errors'].append({
                        'path': str(entity.path),
                        'error': f"Entity scope is '{entity.scope}', not '{from_scope}'"
                    })
                    continue
                    
                # Determine target path based on scope
                target_path = self._calculate_promotion_path(entity, to_scope)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(entity.path), str(target_path))
                
                # Log the action
                self._log_action("promote", entity, 
                                target_path=target_path,
                                from_scope=from_scope, 
                                to_scope=to_scope)
                
                results['success'].append(str(entity.path))
                results['promoted_to'].append(str(target_path))
                
            except Exception as e:
                results['errors'].append({
                    'path': str(entity.path),
                    'error': str(e)
                })
                
        return results
    
    def _create_backup(self, entity: ThoughtEntity, action: str) -> Path:
        """Create backup of entity before destructive action."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{entity.path.stem}_{action}_{timestamp}.md"
        backup_path = self.backup_dir / backup_name
        
        # Copy file with metadata
        shutil.copy2(entity.path, backup_path)
        
        # Create backup metadata
        backup_meta = backup_path.with_suffix('.meta.json')
        metadata = {
            'original_path': str(entity.path),
            'backup_timestamp': timestamp,
            'action': action,
            'entity_metadata': entity.metadata,
            'entity_type': entity.type,
            'entity_scope': entity.scope,
        }
        
        with open(backup_meta, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        return backup_path
    
    def _log_action(self, action: str, entity: ThoughtEntity, **kwargs):
        """Log action to audit trail."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'entity_path': str(entity.path),
            'entity_type': entity.type,
            'entity_scope': entity.scope,
            'metadata': entity.metadata,
            **kwargs
        }
        
        with open(self.audit_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
```

#### 2. Action Integration in CLI
**File**: `mem8/cli.py`
**Changes**: Add action execution to find command

```python
from .core.thought_actions import ThoughtActionEngine

def _execute_action(action: str, entities: List[ThoughtEntity], ctx):
    """Execute the specified action on thought entities."""
    action_engine = ThoughtActionEngine(ctx.obj['config'])
    
    # Confirmation prompt for destructive actions
    if action in ['delete', 'archive'] and not ctx.obj.get('force', False):
        entity_list = '\n'.join(f"  • {entity.path.relative_to(Path.cwd())}" for entity in entities[:5])
        if len(entities) > 5:
            entity_list += f"\n  • ... and {len(entities) - 5} more"
            
        console.print(f"[bold yellow]⚠️  About to {action} {len(entities)} thoughts:[/bold yellow]")
        console.print(entity_list)
        
        if not click.confirm(f"\nProceed with {action}?", default=False):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
            
    # Execute action
    console.print(f"[bold blue]Executing {action} on {len(entities)} thoughts...[/bold blue]")
    
    try:
        if action == 'delete':
            results = action_engine.delete_thoughts(entities)
        elif action == 'archive':
            results = action_engine.archive_thoughts(entities)
        elif action == 'promote':
            # Would need additional CLI options for from/to scope
            console.print("[yellow]Promote action requires --from-scope and --to-scope options[/yellow]")
            return
        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            return
            
        # Report results
        if results['success']:
            console.print(f"[green]✅ Successfully {action}d {len(results['success'])} thoughts[/green]")
            
        if results['errors']:
            console.print(f"[red]❌ {len(results['errors'])} errors occurred:[/red]")
            for error in results['errors']:
                console.print(f"  • {error['path']}: {error['error']}")
                
        if action == 'delete' and results.get('backups'):
            console.print(f"[blue]💾 Backups created in: {action_engine.backup_dir}[/blue]")
            
    except Exception as e:
        console.print(f"[red]❌ Action failed: {e}[/red]")
        if ctx.obj['verbose']:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

def _preview_action(action: str, entities: List[ThoughtEntity]):
    """Preview what an action would do without executing."""
    console.print(f"[bold yellow]🔍 Preview: {action} operation on {len(entities)} thoughts[/bold yellow]")
    
    table = Table(title=f"Would {action}")
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="green") 
    table.add_column("Status", style="yellow")
    
    for entity in entities:
        rel_path = entity.path.relative_to(Path.cwd())
        table.add_row(str(rel_path), entity.type, entity.lifecycle_state)
        
    console.print(table)
    console.print(f"[dim]Run without --dry-run to execute[/dim]")
```

### Success Criteria:

#### Automated Verification:
- [x] Backup creation works correctly: Test creating and verifying backup files
- [x] Delete operations complete successfully: Test with non-critical files
- [x] Archive operations preserve directory structure: Test archiving from various locations
- [x] Audit logging captures all required information: Verify audit log entries
- [x] Dry-run mode shows accurate preview: Compare dry-run vs actual execution

#### Manual Verification:
- [x] Confirmation prompts appear for destructive operations
- [x] Backups contain complete original file content and metadata
- [x] Error handling gracefully manages permission issues and missing files
- [x] Archive directory structure is logical and navigable
- [x] Audit log provides sufficient information for operation reversal

---

## Phase 4: AI-Powered Completion Analysis

### Overview
Add AI-powered analysis to automatically detect when plans are complete based on git commits, file artifacts, and success criteria.

### Changes Required:

#### 1. Completion Analysis Engine
**File**: `mem8/core/completion_analysis.py` (new)
**Changes**: AI-powered detection of plan completion status

```python
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class CompletionAnalysisEngine:
    """Analyzes thought entities to detect completion status."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def analyze_completion(self, entity: ThoughtEntity) -> Dict[str, Any]:
        """Comprehensively analyze if a thought entity is complete."""
        analysis = {
            'entity_path': str(entity.path),
            'current_status': entity.lifecycle_state,
            'completion_confidence': 0.0,
            'evidence': [],
            'recommendations': [],
        }
        
        # Analyze based on entity type
        if entity.type == 'plan':
            analysis = self._analyze_plan_completion(entity, analysis)
        elif entity.type == 'research':
            analysis = self._analyze_research_completion(entity, analysis)
        else:
            analysis = self._analyze_generic_completion(entity, analysis)
            
        # Calculate overall confidence
        analysis['completion_confidence'] = self._calculate_confidence(analysis['evidence'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_plan_completion(self, entity: ThoughtEntity, analysis: Dict) -> Dict:
        """Analyze completion specific to implementation plans."""
        content = entity.content.lower()
        
        # Check for success criteria checkboxes
        checkbox_evidence = self._analyze_checkboxes(entity.content)
        if checkbox_evidence:
            analysis['evidence'].append(checkbox_evidence)
            
        # Check for implementation commits
        git_evidence = self._analyze_git_implementation(entity)
        if git_evidence:
            analysis['evidence'].append(git_evidence)
            
        # Check for artifact creation
        artifact_evidence = self._analyze_created_artifacts(entity)
        if artifact_evidence:
            analysis['evidence'].append(artifact_evidence)
            
        # Check for explicit completion statements
        completion_phrases = [
            'implementation complete', 'successfully implemented', 
            'plan executed', 'all phases complete'
        ]
        
        for phrase in completion_phrases:
            if phrase in content:
                analysis['evidence'].append({
                    'type': 'explicit_completion',
                    'confidence': 0.8,
                    'description': f"Found completion statement: '{phrase}'"
                })
                
        return analysis
        
    def _analyze_checkboxes(self, content: str) -> Optional[Dict]:
        """Analyze success criteria checkboxes in content."""
        # Find all checkboxes
        total_boxes = len(re.findall(r'- \[[ x]\]', content))
        checked_boxes = len(re.findall(r'- \[x\]', content, re.IGNORECASE))
        
        if total_boxes == 0:
            return None
            
        completion_ratio = checked_boxes / total_boxes
        
        return {
            'type': 'checkbox_completion',
            'confidence': completion_ratio,
            'description': f"{checked_boxes}/{total_boxes} success criteria completed ({completion_ratio:.1%})",
            'details': {
                'total_checkboxes': total_boxes,
                'completed_checkboxes': checked_boxes,
                'completion_ratio': completion_ratio
            }
        }
    
    def _analyze_git_implementation(self, entity: ThoughtEntity) -> Optional[Dict]:
        """Analyze git commits for implementation evidence."""
        try:
            # Get topic/title for commit search
            topic = entity.metadata.get('topic', entity.path.stem)
            
            # Search for commits mentioning the topic
            search_terms = self._extract_search_terms(topic)
            
            related_commits = []
            for term in search_terms:
                # Search git log for commits mentioning this term
                try:
                    result = subprocess.run([
                        'git', 'log', '--oneline', '--grep', term, '--since=30 days ago'
                    ], capture_output=True, text=True, cwd=self.config.workspace_dir)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        commits = result.stdout.strip().split('\n')
                        related_commits.extend(commits)
                        
                except subprocess.SubprocessError:
                    continue
                    
            if related_commits:
                return {
                    'type': 'git_implementation',
                    'confidence': min(0.7, len(related_commits) * 0.2),  # Cap at 0.7
                    'description': f"Found {len(related_commits)} related commits",
                    'details': {
                        'related_commits': related_commits[:5],  # Show first 5
                        'total_commits': len(related_commits)
                    }
                }
                
        except Exception:
            pass  # Git analysis failed, continue without it
            
        return None
        
    def _extract_search_terms(self, topic: str) -> List[str]:
        """Extract searchable terms from topic/title."""
        # Simple extraction - split on common separators and take meaningful words
        import string
        
        # Remove punctuation and split
        cleaned = topic.translate(str.maketrans('', '', string.punctuation))
        words = cleaned.split()
        
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [w for w in words if len(w) > 3 and w.lower() not in stop_words]
        
        # Also include the original topic for exact matches
        return meaningful_words + [topic]
    
    def _calculate_confidence(self, evidence: List[Dict]) -> float:
        """Calculate overall completion confidence from evidence."""
        if not evidence:
            return 0.0
            
        # Weight different types of evidence
        weights = {
            'checkbox_completion': 1.0,
            'explicit_completion': 0.8,
            'git_implementation': 0.6,
            'artifact_creation': 0.7,
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for item in evidence:
            weight = weights.get(item['type'], 0.5)
            weighted_sum += item['confidence'] * weight
            total_weight += weight
            
        return min(1.0, weighted_sum / total_weight if total_weight > 0 else 0.0)
        
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate action recommendations based on analysis."""
        confidence = analysis['completion_confidence']
        current_status = analysis['current_status']
        recommendations = []
        
        if confidence >= 0.8 and current_status != 'completed':
            recommendations.append("High confidence completion detected - consider marking as completed")
            recommendations.append("Run 'mem8 update-status completed' to update status")
            
        elif confidence >= 0.6:
            recommendations.append("Substantial progress detected - review for potential completion")
            recommendations.append("Check remaining success criteria manually")
            
        elif confidence < 0.3 and current_status == 'completed':
            recommendations.append("Status marked complete but little evidence found - review status")
            
        if not any(e['type'] == 'checkbox_completion' for e in analysis['evidence']):
            recommendations.append("No success criteria checkboxes found - consider adding them")
            
        return recommendations
```

#### 2. Analysis Command
**File**: `mem8/cli.py`
**Changes**: Add completion analysis command

```python
from .core.completion_analysis import CompletionAnalysisEngine

@cli.command('analyze-completion')
@click.argument('query', required=True)
@click.option('--auto-update', is_flag=True, help='Automatically update status based on analysis')
@click.option('--confidence-threshold', default=0.8, help='Confidence threshold for auto-updates')
@click.pass_context
def analyze_completion(ctx, query: str, auto_update: bool, confidence_threshold: float):
    """Analyze completion status of thoughts using AI."""
    memory_manager = ctx.obj['memory_manager']
    analysis_engine = CompletionAnalysisEngine(ctx.obj['config'])
    
    console.print(f"[bold blue]🔬 Analyzing completion: '{query}'[/bold blue]")
    
    # Find matching thoughts
    query_engine = IntelligentQueryEngine(memory_manager.thought_discovery)
    intent = query_engine.parse_query(query)
    entities = query_engine.execute_query(intent)
    
    if not entities:
        console.print("[yellow]❌ No thoughts found matching query[/yellow]")
        return
        
    # Analyze each entity
    for entity in entities:
        console.print(f"\n[bold]Analyzing: {entity.path.name}[/bold]")
        
        analysis = analysis_engine.analyze_completion(entity)
        
        # Display current status
        console.print(f"Current status: [yellow]{analysis['current_status']}[/yellow]")
        console.print(f"Completion confidence: [green]{analysis['completion_confidence']:.1%}[/green]")
        
        # Display evidence
        if analysis['evidence']:
            console.print("\n[bold]Evidence found:[/bold]")
            for evidence in analysis['evidence']:
                icon = "✅" if evidence['confidence'] > 0.6 else "⚠️"
                console.print(f"  {icon} {evidence['description']} (confidence: {evidence['confidence']:.1%})")
                
        # Display recommendations
        if analysis['recommendations']:
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in analysis['recommendations']:
                console.print(f"  💡 {rec}")
                
        # Auto-update if requested and confidence is high
        if auto_update and analysis['completion_confidence'] >= confidence_threshold:
            if analysis['current_status'] != 'completed':
                console.print(f"\n[green]🎯 Auto-updating status to 'completed' (confidence: {analysis['completion_confidence']:.1%})[/green]")
                # Implementation would update the YAML frontmatter
                # _update_thought_status(entity, 'completed')
            else:
                console.print(f"\n[blue]ℹ️  Status already marked as completed[/blue]")
```

### Success Criteria:

#### Automated Verification:
- [x] Checkbox analysis correctly counts checked/unchecked items: Test with various checkbox patterns
- [x] Git commit analysis finds relevant commits: Test with known commit patterns
- [x] Confidence calculation produces reasonable scores: Test with various evidence combinations
- [x] Recommendations are contextually appropriate: Test with different completion scenarios

#### Manual Verification:
- [x] Analysis provides meaningful insights for actual plan completion
- [x] Confidence scores align with human assessment of completion status
- [x] Git commit correlation works for real implementation commits
- [x] Recommendations are actionable and helpful

---

## Testing Strategy

### Unit Tests:
- ThoughtEntity parsing and classification with various YAML formats
- Query intent parsing with edge cases and ambiguous queries
- Action engine backup and recovery mechanisms
- Completion analysis confidence calculation with different evidence types

### Integration Tests:
- End-to-end find → action workflows with real thought files
- Cross-repository discovery and analysis
- Git integration with actual commit history
- Backup and restore operations with permission variations

### Manual Testing Steps:
1. **Basic Intelligence**: Run `mem8 find "completed plans"` and verify semantic understanding
2. **Safe Deletion**: Use `mem8 find "test file" --action delete --dry-run` to test safety measures
3. **Completion Analysis**: Run `mem8 analyze-completion "template packaging plan"` on actual completed plan
4. **Cross-Repository**: Test discovery across multiple repository setups
5. **Backup Recovery**: Deliberately delete a thought and test restoration from backup

## Performance Considerations

- **Lazy Loading**: ThoughtEntity discovery cached with filesystem watching for changes
- **Indexing Strategy**: Build search index for large thought collections (Phase 5 enhancement)
- **Git Analysis Limits**: Restrict git log searches to recent timeframe (30 days default)
- **Batch Operations**: Process large action sets in chunks with progress reporting

## Migration Notes

- **Backward Compatibility**: All existing `mem8 search` functionality preserved as fallback
- **YAML Enhancement**: No breaking changes to frontmatter format, only additive enhancements
- **Progressive Rollout**: Intelligence features can be enabled incrementally without breaking existing workflows
- **Data Safety**: All destructive operations create backups automatically

## References

- Original use case: Managing `include-templates-in-wheel-distribution.md` lifecycle
- YAML frontmatter format: `thoughts/shared/research/2025-08-30_13-52-45_pypi-release-workflow-failure-analysis.md`
- Existing search implementation: `mem8/core/memory.py:393-434`
- Directory structure: `thoughts/shared/{plans,research,prs}/` organization pattern
- Current CLI interface: `mem8/cli.py:548-640` (search command)