---
date: 2025-09-01T09:37:55-05:00
researcher: claude-code
git_commit: d4a784dc22487064b272f66b310f11477b1d8d2f
branch: codex/mark-semantic-search-as-experimental
repository: mem8
topic: "Humanlayer CLI Command Migration to mem8"
tags: [research, codebase, cli, migration, humanlayer, mem8]
status: complete
last_updated: 2025-09-01
last_updated_by: claude-code
---

# Research: Humanlayer CLI Command Migration to mem8

**Date**: 2025-09-01T09:37:55-05:00
**Researcher**: claude-code
**Git Commit**: d4a784dc22487064b272f66b310f11477b1d8d2f
**Branch**: codex/mark-semantic-search-as-experimental
**Repository**: mem8

## Research Question
Find any mentions of "humanlayer" as a CLI command that should now be "mem8"

## Summary
Found 26+ files containing "humanlayer" references that need migration to "mem8". These are primarily in command documentation files (`.claude/commands/`) and cookiecutter templates (`claude-dot-md-template/`). All references appear to be legacy artifacts from when this project or its templates were based on a "humanlayer" CLI tool. **No migration documentation exists**, suggesting this name change was recent or not yet documented.

## Detailed Findings

### CLI Command Invocations (HIGH PRIORITY)
- **Files affected**: 8 command files in `.claude/commands/`
- **Commands found**:
  - `humanlayer thoughts sync` → should be `mem8 thoughts sync`
  - `humanlayer launch --model opus` → should be `mem8 launch --model opus`
  - `npx humanlayer launch` → should be `npx mem8 launch`
  - `npx humanlayer thoughts init` → should be `npx mem8 thoughts init`

### File System Paths (HIGH PRIORITY)
- **Config directories**: `~/.humanlayer/logs/`, `~/.humanlayer/daemon.db`, `~/.humanlayer/daemon.sock`
- **Should be**: `~/.mem8/logs/`, `~/.mem8/daemon.db`, `~/.mem8/daemon.sock`
- **Worktree paths**: `~/wt/humanlayer/ENG-XXXX` → `~/wt/mem8/ENG-XXXX`

### Template System (MEDIUM PRIORITY)
- **Files affected**: Duplicate references in `mem8/templates/claude-dot-md-template/`
- **Impact**: New projects created from templates would inherit incorrect "humanlayer" references
- **Action needed**: Update cookiecutter templates to use "mem8" defaults

### GitHub Repository References (CONTEXT DEPENDENT)
- **Found**: `https://github.com/humanlayer/thoughts/` references
- **Found**: `git remote add USERNAME git@github.com:USERNAME/humanlayer`
- **Decision**: Update if these should point to your project's repositories

## Code References

### Command Files Requiring Updates
- `.claude/commands/research_codebase.md:141` - `humanlayer thoughts sync`
- `.claude/commands/ralph_research.md:39` - `humanlayer thoughts sync`  
- `.claude/commands/ralph_plan.md:27` - `humanlayer thoughts sync`
- `.claude/commands/ralph_impl.md:26` - `npx humanlayer launch --model opus`
- `.claude/commands/create_worktree.md:23,32,37` - `humanlayer launch` commands
- `.claude/commands/local_review.md:20,22,27,43` - Git remotes and CLI init commands
- `.claude/commands/describe_pr.md:9,56` - `humanlayer thoughts` references
- `.claude/commands/create_plan.md:54,268,288,311,398` - Various `humanlayer` references

### Template Files Requiring Updates
- `claude-dot-md-template/{{cookiecutter.project_slug}}/commands/*.md` - All command templates
- `mem8/templates/claude-dot-md-template/` - Packaged template copies

### Debug Configuration
- `.claude/commands/debug.md:36-180` - File system paths and environment variables

## Architecture Insights

### Template System Structure
The codebase uses a **dual-template system**:
1. **Development templates**: `claude-dot-md-template/` (for editing)
2. **Packaged templates**: `mem8/templates/claude-dot-md-template/` (for distribution)

Both locations contain identical "humanlayer" references, indicating the templates were originally copied from a humanlayer-based project.

### Command Documentation Patterns
All command files follow consistent patterns:
- **CLI invocations**: Direct command line usage
- **File system references**: Configuration and data directories  
- **Workflow integration**: Git worktrees and development processes

### Missing Migration Infrastructure
- **No migration documentation**: No thoughts documents about the name change
- **No deprecation warnings**: Templates still reference old CLI name
- **No transition plan**: No documented strategy for updating existing projects

## Historical Context (from thoughts/)
**No migration documentation found** in the thoughts directory. The absence of migration notes suggests:
- The name change was recent and not yet documented
- This was an internal decision not captured in the thoughts system  
- Templates were copied from another project without updating references

## Related Research
- `thoughts/shared/plans/restore-typer-cli-functionality.md` - CLI framework migration (Click → Typer)
- `thoughts/shared/research/2025-09-01_wheel-packaging-templates.md` - Template packaging research

## Open Questions

### Immediate Action Items
1. **Should all "humanlayer" references be changed to "mem8"?** - Research indicates YES for CLI commands and file paths
2. **What about GitHub repository URLs?** - Context dependent on whether they should point to your repositories
3. **Are there live deployments using the old paths?** - Check if `~/.humanlayer/` directories exist in production

### Missing Documentation
1. **Migration timeline**: When did the name change occur?
2. **Migration rationale**: Why was the name changed from "humanlayer" to "mem8"?
3. **Compatibility strategy**: Should old commands be deprecated gradually or changed immediately?

### Template Management
1. **Template update process**: How should both development and packaged templates be kept in sync?
2. **Existing projects**: How should existing projects created from old templates be updated?
3. **Rollout strategy**: Should this be a breaking change or backward compatible transition?

## Recommendations

### High Priority (CLI Functionality)
1. Update all CLI command references: `humanlayer` → `mem8`
2. Update all file system paths: `~/.humanlayer/` → `~/.mem8/`
3. Update worktree directory patterns: `~/wt/humanlayer/` → `~/wt/mem8/`

### Medium Priority (Template System)
1. Update cookiecutter templates in both locations
2. Ensure template synchronization process includes mem8 references
3. Test template instantiation with updated references

### Documentation Priority
1. Create migration documentation in `thoughts/shared/plans/`
2. Document the name change rationale and timeline
3. Add migration guide for existing projects using old templates

### Validation Priority  
1. Test that `mem8` CLI commands work as expected
2. Verify file system paths are correctly created
3. Ensure GitHub repository URLs point to intended repositories