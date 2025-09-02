"""
Configuration management for PairCoder.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json
from dataclasses import dataclass, asdict, field


@dataclass
class Config:
    """PairCoder configuration."""

    # Project settings
    project_name: str = "My Project"
    primary_goal: str = "Build awesome software"
    coverage_target: int = 80

    # Branch settings
    default_branch_type: str = "feature"
    main_branch: str = "main"

    # Context settings
    context_dir: str = "context"

    # Pack settings
    default_pack_name: str = "agent_pack.tgz"
    pack_excludes: list[str] = field(default_factory=lambda: [
        ".git", ".venv", "__pycache__", "node_modules",
        "dist", "build", "*.log", "*.bak"
    ])

    # CI settings
    python_formatter: str = "ruff"
    node_formatter: str = "prettier"

    @classmethod
    def load(cls, root: Path) -> "Config":
        """Load configuration from .paircoder.yml or environment."""
        config_file = root / ".paircoder.yml"

        data = {}
        if config_file.exists():
            with open(config_file) as f:
                yaml_data = yaml.safe_load(f) or {}

                # Handle both flat and nested structures
                if "version" in yaml_data:
                    # New nested structure
                    if "project" in yaml_data:
                        project = yaml_data["project"]
                        data["project_name"] = project.get("name", "My Project")
                        data["primary_goal"] = project.get("primary_goal", "Build awesome software")
                        data["coverage_target"] = project.get("coverage_target", 80)

                    if "workflow" in yaml_data:
                        workflow = yaml_data["workflow"]
                        data["default_branch_type"] = workflow.get("default_branch_type", "feature")
                        data["main_branch"] = workflow.get("main_branch", "main")
                        data["context_dir"] = workflow.get("context_dir", "context")

                    if "pack" in yaml_data:
                        pack = yaml_data["pack"]
                        data["default_pack_name"] = pack.get("default_name", "agent_pack.tgz")
                        data["pack_excludes"] = pack.get("excludes", [])

                    if "ci" in yaml_data:
                        ci = yaml_data["ci"]
                        data["python_formatter"] = ci.get("python_formatter", "ruff")
                        data["node_formatter"] = ci.get("node_formatter", "prettier")
                else:
                    # Old flat structure (backwards compatibility)
                    data = yaml_data

        # Override with environment variables
        env_mappings = {
            "PAIRCODER_MAIN_BRANCH": "main_branch",
            "PAIRCODER_CONTEXT_DIR": "context_dir",
            "PAIRCODER_DEFAULT_BRANCH": "default_branch_type",
            "PAIRCODER_PROJECT_NAME": "project_name",
        }

        for env_var, config_key in env_mappings.items():
            if env_value := os.getenv(env_var):
                data[config_key] = env_value

        # Create config with collected data
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def save(self, root: Path) -> None:
        """Save configuration to .paircoder.yml."""
        config_file = root / ".paircoder.yml"

        data = {
            "version": "0.1.3",
            "project": {
                "name": self.project_name,
                "primary_goal": self.primary_goal,
                "coverage_target": self.coverage_target,
            },
            "workflow": {
                "default_branch_type": self.default_branch_type,
                "main_branch": self.main_branch,
                "context_dir": self.context_dir,
            },
            "pack": {
                "default_name": self.default_pack_name,
                "excludes": self.pack_excludes,
            },
            "ci": {
                "python_formatter": self.python_formatter,
                "node_formatter": self.node_formatter,
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ContextTemplate:
    """Templates for context files."""

    @staticmethod
    def development_md(config: Config) -> str:
        """Generate development.md template."""
        return f"""# Development Log

**Project:** {config.project_name}
**Phase:** Phase 1: Initial Setup
**Primary Goal:** {config.primary_goal}

## KPIs & Non-Functional Targets

- Test Coverage: ≥ {config.coverage_target}%
- Documentation: Complete for all public APIs
- Performance: Response time < 200ms (p95)

## Phase 1 — Foundation (Weeks 1–2)

**Objectives**
- Set up project structure and CI/CD
- Define core architecture and interfaces
- Establish testing framework

**Tasks**
- [ ] Initialize repository with PairCoder
- [ ] Set up CI workflows
- [ ] Create initial project structure
- [ ] Write architectural decision records

**Testing Plan**
- Unit tests for all business logic
- Integration tests for external boundaries
- End-to-end tests for critical user flows

**Risks & Rollback**
- Risk: Incomplete requirements — Mitigation: Regular stakeholder reviews
- Rollback: Git revert with documented rollback procedures

## Context Sync (AUTO-UPDATED)

- **Overall goal is:** {config.primary_goal}
- **Last action was:** Initialized project
- **Next action will be:** Set up CI/CD pipeline
- **Blockers:** None
"""

    @staticmethod
    def agents_md(config: Config) -> str:
        """Generate agents.md template."""
        return f"""# Agents Guide — AI Pair Coding Playbook

**Project:** {config.project_name}
**Purpose:** {config.primary_goal}

## Ground Rules

1. **Context is King**: Always refer to `/context/development.md` for current state
2. **Test First**: Write tests before implementation
3. **Small Changes**: Keep PRs under 200 lines when possible
4. **Update Loop**: Run `bpsai-pair context-sync` after every significant change

## Project Structure

```
.
├── {config.context_dir}/          # Project context and memory
├── src/                            # Source code
├── tests/                          # Test suites
├── docs/                           # Documentation
└── .paircoder.yml                  # Configuration
```

## Workflow

1. Check status: `bpsai-pair status`
2. Create feature: `bpsai-pair feature <name> --primary "<goal>" --phase "<phase>"`
3. Make changes (with tests)
4. Update context: `bpsai-pair context-sync --last "<what>" --next "<next>"`
5. Create pack: `bpsai-pair pack`
6. Share with AI agent

## Testing Requirements

- Minimum coverage: {config.coverage_target}%
- All new code must have tests
- Integration tests for external dependencies
- Performance tests for critical paths

## Code Style

- Python: {config.python_formatter} for formatting and linting
- JavaScript: {config.node_formatter} for formatting
- Commit messages: Conventional Commits format
- Branch names: {config.default_branch_type}/<description>

## Context Loop Protocol

After EVERY meaningful change:
```bash
bpsai-pair context-sync \\
    --last "What was just completed" \\
    --next "The immediate next step" \\
    --blockers "Any impediments"
```

## Excluded from Context

The following are excluded from agent packs (see `.agentpackignore`):
{chr(10).join(f'- {exclude}' for exclude in config.pack_excludes)}

## Commands Reference

- `bpsai-pair init` - Initialize scaffolding
- `bpsai-pair feature` - Create feature branch
- `bpsai-pair pack` - Create context package
- `bpsai-pair sync` - Update context loop
- `bpsai-pair status` - Show current state
- `bpsai-pair validate` - Check structure
- `bpsai-pair ci` - Run local CI checks
"""

    @staticmethod
    def gitignore() -> str:
        """Generate .gitignore template."""
        return """# PairCoder
.paircoder.yml.local
agent_pack*.tgz
*.bak

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# OS
Thumbs.db
Desktop.ini
"""
