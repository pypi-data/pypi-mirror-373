# Claude AI Memory Template

Cookiecutter template for generating `.claude` directory configurations.

## Quick Start

```bash
# Install cookiecutter
uv tool install cookiecutter

# Generate with defaults
cookiecutter claude-dot-md-template --output-dir out

# Interactive mode
cookiecutter claude-dot-md-template
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | Claude AI Memory | Display name for the configuration |
| `project_slug` | .claude | Output directory name |
| `include_agents` | true | Include agent definitions |
| `include_commands` | true | Include command definitions |
| `include_ralph_commands` | false | Include Ralph workflow commands |
| `include_linear_integration` | false | Include Linear ticket integration |
| `include_web_search` | true | Include web search researcher agent |
| `default_tools` | Read, Grep, Glob, LS | Default tools for agents |
| `repository_path` | /shared/ | Path for shared repository data |

## Generated Structure

```
.claude/
├── agents/
│   ├── codebase-analyzer.md      # Analyzes implementation details
│   ├── codebase-locator.md       # Finds files and components
│   └── web-search-researcher.md  # Web research specialist (optional)
└── commands/
    ├── commit.md                  # Git commit workflow
    ├── create_plan.md            # Implementation planning
    └── ralph_plan.md             # Ralph ticket workflow (optional)
```

## Customization

### Command Line Options
```bash
# Disable web search and Ralph commands
cookiecutter claude-dot-md-template \
  --no-input \
  --output-dir my-config \
  -f include_web_search=false \
  -f include_ralph_commands=false
```

### Post-Generation
The template includes a post-generation hook that:
- Removes optional files based on configuration
- Cleans up empty directories
- Validates the generated structure

## Adding New Templates

1. Add markdown files to `{{cookiecutter.project_slug}}/agents/` or `/commands/`
2. Use Jinja2 variables: `{{ cookiecutter.variable_name }}`
3. Wrap optional content in `{% if cookiecutter.condition %}`
4. Update `hooks/post_gen_project.py` for conditional file removal