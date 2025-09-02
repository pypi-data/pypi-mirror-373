---
date: 2025-09-01T14:00:00-05:00
author: claude-code
git_commit: d4a784dc22487064b272f66b310f11477b1d8d2f
branch: codex/mark-semantic-search-as-experimental
repository: mem8
topic: "Humanlayer to mem8 Command Mapping Reference"
tags: [migration, cli, commands, reference, mapping]
status: complete
last_updated: 2025-09-01
last_updated_by: claude-code
---

# Humanlayer → mem8 Command Mapping Reference

**Purpose**: Definitive mapping guide for migrating legacy "humanlayer" CLI commands to "mem8" equivalents during the migration process.

## CLI Command Mappings

### Primary Commands

| Legacy Command | mem8 Equivalent | Status | Notes |
|---|---|---|---|
| `humanlayer thoughts sync` | `mem8 sync` | ⚠️ **Experimental** | Sync functionality exists but needs overhaul for local/team sharing |
| `humanlayer launch --model opus` | `mem8 dashboard` | ✅ **Ready** | Dashboard launches web interface |
| `humanlayer launch` | `mem8 dashboard` | ✅ **Ready** | Default launch behavior |
| `npx humanlayer thoughts init` | `mem8 init` | ✅ **Ready** | Workspace initialization |
| `npx humanlayer launch` | `mem8 dashboard` | ✅ **Ready** | NPX equivalent |

### Additional Available Commands

**New mem8 commands not present in legacy humanlayer:**

| Command | Purpose | Status |
|---|---|---|
| `mem8 status` | Show workspace status | ✅ Ready |
| `mem8 doctor` | Diagnose and fix issues | ✅ Ready |
| `mem8 search` | Search memory and thoughts | ✅ Ready (semantic search experimental) |
| `mem8 find {all\|plans\|research\|shared\|completed}` | Find thoughts by category | ✅ Ready |
| `mem8 team {create\|list\|join}` | Team collaboration | ⚠️ Experimental |
| `mem8 deploy {kubernetes\|local}` | Deployment commands | ⚠️ Experimental |

## File System Path Mappings

### Configuration Directories

| Legacy Path | mem8 Equivalent | Purpose |
|---|---|---|
| `~/.humanlayer/` | `~/.mem8/` | Main config directory |
| `~/.humanlayer/logs/` | `~/.mem8/` (via platformdirs) | Log storage |
| `~/.humanlayer/daemon.db` | **N/A** | mem8 has no daemon component |
| `~/.humanlayer/daemon.sock` | **N/A** | mem8 has no daemon component |

### Worktree and Development Paths

| Legacy Path | mem8 Equivalent | Purpose |
|---|---|---|
| `~/wt/humanlayer/ENG-XXXX` | `~/wt/mem8/ENG-XXXX` | Git worktree naming |
| `humanlayer-wui/` | `mem8-wui/` | Web UI directory references |

## Command Option Mappings

### Sync Command Options

**Legacy**: `humanlayer thoughts sync [options]`
**New**: `mem8 sync [options]`

| Option | Available in mem8 | Notes |
|---|---|---|
| `--direction {pull\|push\|both}` | ✅ Yes | Sync direction control |
| `--dry-run` | ✅ Yes | Preview changes |
| `--verbose, -v` | ✅ Yes | Detailed output |

### Dashboard/Launch Command Options

**Legacy**: `humanlayer launch --model opus`
**New**: `mem8 dashboard`

| Legacy Option | mem8 Equivalent | Notes |
|---|---|---|
| `--model opus` | **N/A** | Model selection not supported in dashboard |

### Init Command Options

**Legacy**: `npx humanlayer thoughts init --directory humanlayer`
**New**: `mem8 init`

| Legacy Option | mem8 Equivalent | Notes |
|---|---|---|
| `--directory humanlayer` | Auto-detected | mem8 auto-detects project structure |

## Repository and URL Mappings

### GitHub Repository References

| Type | Legacy Reference | Action Required |
|---|---|---|
| Generic repo URLs | `github.com/humanlayer/thoughts` | **Context-dependent** - update only if pointing to your repos |
| Git remotes | `git@github.com:USERNAME/humanlayer` | **Context-dependent** - update if repo was renamed |
| Documentation URLs | `https://github.com/humanlayer/...` | **Review case-by-case** |

## Migration Regex Patterns

### For Automated Search-and-Replace

```bash
# CLI Commands
s/humanlayer thoughts sync/mem8 sync/g
s/humanlayer launch --model opus/mem8 dashboard/g
s/humanlayer launch/mem8 dashboard/g
s/npx humanlayer thoughts init/mem8 init/g
s/npx humanlayer launch/mem8 dashboard/g

# File System Paths
s/~\/.humanlayer\//~\/.mem8\//g
s/\$HOME\/.humanlayer\//\$HOME\/.mem8\//g
s/\${HOME}\/.humanlayer\//\${HOME}\/.mem8\//g

# Worktree Paths
s/~\/wt\/humanlayer\//~\/wt\/mem8\//g
s/\$HOME\/wt\/humanlayer\//\$HOME\/wt\/mem8\//g

# Directory References  
s/humanlayer-wui\//mem8-wui\//g

# Environment Variables (if any)
s/HUMANLAYER_/MEM8_/g
s/humanlayer_/mem8_/g
```

## Validation Commands

### Command Availability Check
```bash
mem8 --help                    # Verify main CLI works
mem8 sync --help              # Check sync options (experimental)
mem8 dashboard --help         # Check dashboard options  
mem8 init --help              # Check init options
mem8 status --help            # Check status command
mem8 search --help            # Check search functionality
```

### Functionality Verification
```bash
mem8 status                   # Should show workspace status
mem8 sync --dry-run           # Should preview sync (if configured)
mem8 dashboard --help         # Should show dashboard options
mem8 find --help             # Should show find subcommands
```

## Migration Warnings and Considerations

### ⚠️ **Sync Command Status**
- `mem8 sync` exists but is **experimental**
- Requires further development for:
  - Local repository sharing
  - Team collaboration workflows
  - Multi-repository synchronization
- Safe to migrate documentation, but users should expect changes

### ✅ **Ready Commands**
- `mem8 dashboard` - Fully functional web interface
- `mem8 init` - Complete workspace initialization
- `mem8 status` - Workspace status checking
- `mem8 search` - Memory and thoughts searching

### 📋 **Missing Features**
- No model selection in dashboard (unlike `--model opus`)
- No daemon component (simpler architecture)
- Some advanced sync features may need development

## Use in Migration Process

1. **Pre-migration**: Validate all target commands work
2. **During migration**: Use regex patterns for consistent replacement
3. **Post-migration**: Run validation commands to verify changes
4. **Documentation**: Reference this mapping for user migration guides

## Status: Phase 1 Complete
- ✅ Command mappings documented and verified
- ✅ File system paths mapped
- ✅ Migration patterns defined
- ✅ Validation procedures established
- ⚠️ Experimental commands clearly marked