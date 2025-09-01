---
date: 2025-08-31T01:10:23-05:00
researcher: vaski
git_commit: b0e0beb9ea705686073544b293bc6bc41f976389
branch: main
repository: mem8
topic: "mem8 init command template path resolution issue when installed via uvx"
tags: [research, codebase, mem8, cli, packaging, cookiecutter, templates]
status: complete
last_updated: 2025-08-31
last_updated_by: vaski
---

# Research: mem8 init command template path resolution issue when installed via uvx

**Date**: 2025-08-31T01:10:23-05:00
**Researcher**: vaski
**Git Commit**: b0e0beb9ea705686073544b293bc6bc41f976389
**Branch**: main
**Repository**: mem8

## Research Question
Why does `uvx mem8 init` fail with an error trying to use a local uv cache path (`C:\Users\vaski\AppData\Local\uv\cache\archive-v0\...`) instead of a GitHub URL or proper template path for the cookiecutter template?

## Summary
The root cause is that the cookiecutter templates (`claude-dot-md-template` and `shared-thoughts-template`) are NOT included in the wheel distribution. The `pyproject.toml` only packages the `ai_mem/` Python package directory, excluding the template directories that exist at the project root. When installed via `uvx`, the code tries to find templates relative to the installed package location in the uv cache, but they don't exist there.

## Detailed Findings

### Package Distribution Issue
The templates are present in the source repository but missing from the wheel distribution:
- `pyproject.toml:63-64` only includes `packages = ["ai_mem"]`
- No configuration to include template directories in the wheel
- No `MANIFEST.in` file to specify additional files
- Templates exist at repository root level, not inside `ai_mem/` package

### Template Path Resolution Logic
- `ai_mem/cli.py:119` - Uses `Path(__file__).parent.parent` to find project root
- `ai_mem/cli.py:123-131` - Hardcodes template paths relative to this root:
  ```python
  project_root = Path(__file__).parent.parent
  template_path = project_root / "claude-dot-md-template"  # or "shared-thoughts-template"
  ```
- When installed via uvx, `__file__` points to the uv cache location
- Templates are expected at sibling directories to `ai_mem/`, but they're not packaged

### Cookiecutter Invocation
- `ai_mem/cli.py:192-227` - Calls `cookiecutter()` with local filesystem paths
- No fallback mechanism for missing templates
- No remote GitHub URL option
- The error message shows cookiecutter trying to use the exact path passed to it

### Silent Failures in Other Components
- `ai_mem/core/memory.py:271-289` - Also tries to copy from templates
- Uses `.exists()` checks that silently skip if templates are missing
- Results in incomplete workspace setup without user warnings

## Code References
- `ai_mem/cli.py:111-256` - Main `init` command implementation
- `ai_mem/cli.py:119` - Project root calculation that causes the issue
- `ai_mem/cli.py:123-131` - Template path determination
- `ai_mem/cli.py:192-227` - Cookiecutter invocation with local paths
- `ai_mem/core/memory.py:266-289` - Additional template usage that fails silently
- `pyproject.toml:63-64` - Packaging configuration that excludes templates

## Architecture Insights
1. **Development vs Production Divergence**: The code works when run from source (templates exist) but fails when installed as a package (templates missing)
2. **No Package Resource Management**: Uses direct filesystem paths instead of package resource APIs
3. **Missing Error Handling**: No checks for template existence before calling cookiecutter
4. **Tight Coupling**: Templates expected at specific relative locations with no configurability

## Solutions

### Option 1: Include Templates in Wheel (Recommended)
Update `pyproject.toml` to include templates:
```toml
[tool.hatch.build.targets.wheel]
packages = ["ai_mem"]
include = [
    "claude-dot-md-template/**/*",
    "shared-thoughts-template/**/*"
]
```

### Option 2: Bundle Templates Inside Package
Move templates into the package and update build config:
```toml
[tool.hatch.build.targets.wheel.force-include]
"claude-dot-md-template" = "ai_mem/templates/claude-dot-md-template"
"shared-thoughts-template" = "ai_mem/templates/shared-thoughts-template"
```

### Option 3: Fetch Templates from GitHub
Change implementation to use GitHub URLs:
```python
template_url = "https://github.com/killerapp/mem8/claude-dot-md-template"
cookiecutter(template_url, ...)
```

### Option 4: Use Package Resources API
For installed packages, use `importlib.resources` or `pkg_resources`:
```python
import importlib.resources as resources
template_path = resources.files("ai_mem") / "templates" / "claude-dot-md-template"
```

## Why OneDrive Appeared in Error
The error message showed "Using shared directory: C:\Users\vaski\OneDrive\mem8-Shared" - this is unrelated to the template path issue. It's the shared directory for thoughts synchronization, printed just before the cookiecutter call fails.

## Open Questions
1. Was the intention to distribute templates with the package or fetch from GitHub?
2. Should templates be versioned with the package or independently?
3. Are there licensing considerations for bundling cookiecutter templates?