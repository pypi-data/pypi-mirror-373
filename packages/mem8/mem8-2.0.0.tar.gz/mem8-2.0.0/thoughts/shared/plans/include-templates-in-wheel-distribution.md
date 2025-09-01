# Include Templates in Wheel Distribution Implementation Plan

## Overview

Fix the `uvx mem8 init` command failure by including cookiecutter templates in the wheel distribution. Currently, templates are missing from the packaged distribution, causing initialization to fail when installed via uvx/pip.

## Current State Analysis

The templates (`claude-dot-md-template` and `shared-thoughts-template`) exist in the source repository but are not included in the wheel distribution. The code attempts to find templates relative to the installed package location, which fails when installed via uvx because the templates aren't packaged.

## Desired End State

After implementation, users should be able to run `uvx mem8 init` successfully with all template options working correctly. The templates will be bundled within the wheel distribution and accessible through proper resource APIs.

### Key Discoveries:
- Templates are at repository root, not inside `ai_mem/` package directory (pyproject.toml:63-64)
- Code uses `Path(__file__).parent.parent` to find templates (ai_mem/cli.py:119)
- Tests expect template operations to fail currently (tests/test_init_data_preservation.py)
- No MANIFEST.in file exists for including non-Python files
- Build process uses `uv build` (.releaserc.json:9)

## What We're NOT Doing

- Not changing the template structure or content
- Not modifying cookiecutter invocation logic
- Not changing command-line interface or options
- Not implementing remote template fetching from GitHub
- Not changing the test suite expectations yet (separate task)

## Implementation Approach

Use Hatch's build configuration to include template directories in the wheel distribution. This is the simplest approach that maintains backward compatibility while ensuring templates are packaged correctly.

## Phase 1: Configure Hatch to Include Templates

### Overview
Update `pyproject.toml` to include template directories in the wheel distribution using Hatch's build configuration.

### Changes Required:

#### 1. Update pyproject.toml Build Configuration
**File**: `pyproject.toml`
**Changes**: Add template inclusion configuration

```toml
[tool.hatch.build.targets.wheel]
packages = ["ai_mem"]

[tool.hatch.build.targets.wheel.force-include]
"claude-dot-md-template" = "ai_mem/templates/claude-dot-md-template"
"shared-thoughts-template" = "ai_mem/templates/shared-thoughts-template"
```

### Success Criteria:

#### Automated Verification:
- [x] Build completes successfully: `uv build`
- [x] Wheel file contains template directories: `unzip -l dist/*.whl | grep templates`
- [x] Template files are present in wheel: `unzip -l dist/*.whl | grep cookiecutter.json`

#### Manual Verification:
- [ ] None required for this phase

---

## Phase 2: Update Template Path Resolution

### Overview
Modify the code to use package resources API to locate templates correctly whether running from source or installed package.

### Changes Required:

#### 1. Update Template Path Resolution in CLI
**File**: `ai_mem/cli.py`
**Changes**: Update lines 119-131 to use package resources

```python
# Add import at top of file
from importlib import resources

# Replace lines 119-131 with:
try:
    # Try to use package resources (for installed package)
    import ai_mem.templates
    template_base = resources.files(ai_mem.templates)
    if template == 'claude-config':
        template_path = template_base / "claude-dot-md-template"
        needs_shared = False
    elif template == 'thoughts-repo':
        template_path = template_base / "shared-thoughts-template"
        needs_shared = True
    else:  # full
        claude_template_path = template_base / "claude-dot-md-template"
        thoughts_template_path = template_base / "shared-thoughts-template"
        needs_shared = True
except (ImportError, AttributeError):
    # Fallback to file-based path (for development)
    project_root = Path(__file__).parent.parent
    if template == 'claude-config':
        template_path = project_root / "claude-dot-md-template"
        needs_shared = False
    elif template == 'thoughts-repo':
        template_path = project_root / "shared-thoughts-template"
        needs_shared = True
    else:  # full
        claude_template_path = project_root / "claude-dot-md-template"
        thoughts_template_path = project_root / "shared-thoughts-template"
        needs_shared = True
```

#### 2. Update Template Path Resolution in Memory Module
**File**: `ai_mem/core/memory.py`
**Changes**: Update lines 271 and 284 to use package resources

```python
# Add import at top of file
from importlib import resources

# Replace line 271 with:
try:
    import ai_mem.templates
    template_agents_dir = resources.files(ai_mem.templates) / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "agents"
except (ImportError, AttributeError):
    # Fallback for development
    template_agents_dir = Path(__file__).parent.parent.parent / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "agents"

# Replace line 284 with:
try:
    import ai_mem.templates
    template_commands_dir = resources.files(ai_mem.templates) / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "commands"
except (ImportError, AttributeError):
    # Fallback for development
    template_commands_dir = Path(__file__).parent.parent.parent / "claude-dot-md-template" / "{{cookiecutter.project_slug}}" / "commands"
```

### Success Criteria:

#### Automated Verification:
- [x] Code imports successfully: `uv run python -c "from ai_mem import cli"`
- [x] No syntax errors: `uv run python -m py_compile ai_mem/cli.py`
- [x] No syntax errors: `uv run python -m py_compile ai_mem/core/memory.py`

#### Manual Verification:
- [x] Development mode still works: `uv run python -m ai_mem.cli init --help`

---

## Phase 3: Create Templates Module

### Overview
Create the `ai_mem/templates/` directory structure and ensure it's recognized as a Python package for resource loading.

### Changes Required:

#### 1. Create Templates Module Structure
**File**: `ai_mem/templates/__init__.py`
**Changes**: Create empty init file

```python
"""Templates package for mem8."""
```

### Success Criteria:

#### Automated Verification:
- [x] Templates module imports: `uv run python -c "import ai_mem.templates"`
- [x] Build includes new module: `uv build`

#### Manual Verification:
- [ ] None required for this phase

---

## Phase 4: Test Package Installation

### Overview
Verify the packaged wheel works correctly when installed via uvx/pip.

### Changes Required:

No code changes - this is a verification phase.

### Success Criteria:

#### Automated Verification:
- [ ] Build wheel successfully: `uv build`
- [ ] Install in fresh virtual environment: `uv venv test-env && test-env/Scripts/activate && pip install dist/*.whl`

#### Manual Verification:
- [x] `mem8 init --template claude-config` works in test environment
- [x] `mem8 init --template thoughts-repo` works in test environment (finds templates correctly)
- [ ] `mem8 init --template full` works in test environment
- [x] Templates are correctly applied with expected directory structure
- [x] `uvx mem8 init` works without template path errors (interactive prompts are separate UX issue)

---

## Testing Strategy

### Unit Tests:
- Add test to verify templates are included in package resources
- Add test for template path resolution in both dev and installed modes
- Update existing tests to expect success instead of failure

### Integration Tests:
- Test installation from wheel in isolated environment
- Test all three template options (claude-config, thoughts-repo, full)
- Verify cookiecutter correctly uses bundled templates

### Manual Testing Steps:
1. Build the wheel: `uv build`
2. Create test environment: `uv venv test-env`
3. Install from wheel: `test-env/Scripts/pip install dist/*.whl`
4. Test init command: `test-env/Scripts/mem8 init --template full`
5. Verify created structure matches expectations
6. Test with uvx: `uvx --from dist/*.whl mem8 init`

## Performance Considerations

- Template files add ~100KB to wheel size (acceptable)
- No runtime performance impact - templates loaded on-demand
- Resource loading is cached by importlib

## Migration Notes

- Existing installations will need to upgrade to get templates
- Development installations continue working with file-based paths
- No data migration required

## References

- Original ticket: `thoughts/shared/research/2025-08-31_01-10-23_mem8_init_template_path_issue.md`
- Template path resolution: `ai_mem/cli.py:119-131`
- Template usage in memory: `ai_mem/core/memory.py:271-289`
- Packaging configuration: `pyproject.toml:63-64`
- Build process: `.releaserc.json:9`