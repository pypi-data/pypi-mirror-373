---
date: 2025-08-31T02:15:00-05:00
researcher: vaski
topic: "Template packaging best practices for CLI tools"
tags: [research, packaging, templates, cli, npm, python, cookiecutter]
status: complete
---

# Research: Template Packaging Best Practices for CLI Tools

## Executive Summary

Research into how modern CLI tools (Next.js, Vite, and Python packages) handle template distribution reveals several key strategies. Our proposed approach using Hatch's `force-include` aligns with industry best practices, though there are alternative approaches worth considering.

## Key Findings

### 1. Next.js create-next-app Approach

**Strategy**: Download templates on-demand from GitHub
- Templates stored in Next.js monorepo examples directory
- CLI downloads templates at runtime using GitHub API
- Supports offline mode using local npm cache
- Zero dependencies in the CLI package itself

**Advantages**:
- Small package size
- Always get latest templates
- Easy to update templates independently

**Disadvantages**:
- Requires internet connection (except offline cache)
- Depends on GitHub availability

### 2. Vite create-vite Approach

**Strategy**: Bundle minimal templates directly in package
- Templates are part of the npm package
- Each template is minimal scaffolding (basic structure)
- Templates stored as directories within the package

**Advantages**:
- Works offline immediately
- Fast project creation (no downloads)
- Predictable template versions

**Disadvantages**:
- Larger package size
- Templates versioned with CLI

### 3. Python/Cookiecutter Best Practices

**Strategy**: Include templates as package data
- Use `tool.hatch.build.targets.wheel.force-include` for Hatchling
- Alternative: `tool.setuptools.package-data` for setuptools
- Templates become part of the wheel distribution

**Configuration Examples**:

#### Hatchling (Recommended for our use case):
```toml
[tool.hatch.build.targets.wheel.force-include]
"claude-dot-md-template" = "ai_mem/templates/claude-dot-md-template"
"shared-thoughts-template" = "ai_mem/templates/shared-thoughts-template"
```

#### Setuptools Alternative:
```toml
[tool.setuptools.package-data]
ai_mem = ["templates/**/*"]
```

## Comparison with Our Implementation Plan

Our proposed approach aligns well with Python packaging best practices:

### ✅ Strengths of Our Approach:
1. **Uses Hatchling's force-include**: Modern, recommended approach for non-Python files
2. **Maps templates to package directory**: Follows Python conventions
3. **Maintains backward compatibility**: Fallback for development mode
4. **Uses importlib.resources**: Proper resource access API

### 🔄 Potential Enhancements:

1. **Consider template versioning**: Could add version metadata to templates
2. **Add template validation**: Verify template integrity before use
3. **Implement template caching**: Cache extracted templates for faster access
4. **Support remote templates**: Add option to fetch from GitHub (like Next.js)

## Alternative Approaches Considered

### 1. GitHub Download Approach (like Next.js)
```python
def get_template(template_name, use_cache=True):
    if use_cache and template_exists_locally(template_name):
        return get_local_template(template_name)
    else:
        return download_from_github(template_name)
```

**Pros**: Smaller package, always latest templates
**Cons**: Network dependency, complexity

### 2. Separate Template Package
```toml
dependencies = [
    "mem8-templates>=1.0.0",
]
```

**Pros**: Independent versioning, smaller main package
**Cons**: More complex deployment, version synchronization issues

### 3. Embedded as Python Strings
```python
TEMPLATES = {
    "claude-config": {...},  # Template data as dict
}
```

**Pros**: Simple, no file I/O
**Cons**: Hard to maintain, poor developer experience

## Best Practices Identified

### 1. Resource Access Pattern
```python
# Good: Use importlib.resources (Python 3.9+)
from importlib import resources
template_path = resources.files("package.templates") / "template_name"

# Fallback for development
if not template_path.exists():
    template_path = Path(__file__).parent / "templates" / "template_name"
```

### 2. Template Discovery
```python
def list_available_templates():
    """List all available templates."""
    try:
        import ai_mem.templates
        return [p.name for p in resources.files(ai_mem.templates).iterdir()]
    except ImportError:
        # Development fallback
        return [p.name for p in (Path(__file__).parent / "templates").iterdir()]
```

### 3. Offline Support
- Always bundle critical templates
- Cache downloaded templates locally
- Provide clear offline/online mode feedback

### 4. Version Compatibility
- Include template version in metadata
- Warn on version mismatches
- Support multiple template versions if needed

## Recommendations

1. **Proceed with current plan**: Our Hatchling force-include approach is solid
2. **Add template validation**: Verify templates exist and are complete before use
3. **Improve error messages**: Clearly indicate when templates are missing
4. **Consider future enhancement**: Add optional GitHub template fetching for updates
5. **Add template tests**: Verify templates are included in built wheels

## Industry Trends (2024)

- **Move to single configuration files**: pyproject.toml for Python, package.json for Node
- **Preference for bundled templates**: Better offline experience, predictable behavior
- **Interactive setup wizards**: Guide users through configuration choices
- **Template marketplace**: Growing trend of community templates (Vite, Next.js)

## Conclusion

Our implementation plan using Hatch's `force-include` follows Python packaging best practices and aligns with how modern tools handle template distribution. The approach balances simplicity, reliability, and maintainability while avoiding the complexity of runtime downloads or separate packages.