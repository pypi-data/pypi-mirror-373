# Example Configurations

This directory contains example configuration files for both cookiecutter templates:
- **claude-dot-md/** - Claude AI memory configurations (.claude directory)
- **shared-thoughts/** - Shared thoughts repository configurations

## Usage

Use these configuration files with the `--config-file` option:

```bash
# For Claude AI memory template
cookiecutter claude-dot-md-template --config-file example-configs/claude-dot-md/default.yaml

# For shared thoughts template
cookiecutter shared-thoughts-template --config-file example-configs/shared-thoughts/default.yaml
```

## Claude AI Memory Configurations

### default.yaml
Standard configuration with basic features:
- All agents and commands included
- Web search enabled
- No Linear/Ralph workflows
- Suitable for individual developers

### minimal.yaml
Bare minimum configuration:
- Core agents and commands only
- No web search
- No integrations
- Lightweight setup

### enterprise-full.yaml
Complete enterprise configuration:
- All features enabled
- Linear ticket integration
- Ralph workflows (plan, research, implement)
- Web search capabilities
- Team collaboration features

## Shared Thoughts Configurations

### default.yaml
Standard thoughts repository:
- Git-based synchronization
- Searchable directory links
- Personal and shared directories
- Sync scripts included

### team-collaboration.yaml
Multi-user team setup:
- GitHub organization integration
- Full directory structure
- Cross-repository global thoughts
- Team-focused paths

### personal-notes.yaml
Single-user personal setup:
- No searchable links
- No global directory
- Simplified structure
- Local git repository

## Customization

Copy any configuration file and modify the values:

```yaml
default_context:
  username: "your-name"
  github_org: "your-org"
  project_root: "/your/project/path"
```

## Quick Start Commands

```bash
# Generate both templates with defaults
cookiecutter claude-dot-md-template --config-file example-configs/claude-dot-md/default.yaml
cookiecutter shared-thoughts-template --config-file example-configs/shared-thoughts/default.yaml

# Generate enterprise setup
cookiecutter claude-dot-md-template --config-file example-configs/claude-dot-md/enterprise-full.yaml
cookiecutter shared-thoughts-template --config-file example-configs/shared-thoughts/team-collaboration.yaml
```

## Configuration Override

You can override specific values from the command line:

```bash
cookiecutter claude-dot-md-template \
  --config-file example-configs/claude-dot-md/default.yaml \
  --no-input \
  organization_name="My Company" \
  include_linear_integration=true
```