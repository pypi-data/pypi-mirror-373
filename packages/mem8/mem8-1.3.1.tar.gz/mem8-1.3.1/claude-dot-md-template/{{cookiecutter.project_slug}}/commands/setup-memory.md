---
allowed-tools: Bash(ai-mem:*), Bash(git:*), Bash(mkdir:*), Bash(uv:*) 
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
- Use `ai-mem dashboard` to open the web interface anytime