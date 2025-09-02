"""
Operations module for cross-platform compatibility.
Replaces shell scripts with Python implementations.
"""
from __future__ import annotations

import os
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set
import shutil
import json


class GitOps:
    """Git operations helper."""

    @staticmethod
    def is_repo(path: Path) -> bool:
        """Check if path is a git repo."""
        return (path / ".git").exists()

    @staticmethod
    def is_clean(path: Path) -> bool:
        """Check if working tree is clean."""
        try:
            # Check for unstaged changes
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=path,
                capture_output=True
            )
            if result.returncode != 0:
                return False

            # Check for staged changes
            staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=path,
                capture_output=True
            )
            if staged.returncode != 0:
                return False

            # Check for untracked files
            untracked = subprocess.run(
                ["git", "ls-files", "--other", "--exclude-standard"],
                cwd=path,
                capture_output=True,
                text=True
            )
            if untracked.stdout.strip():
                return False

            return True
        except:
            return False

    @staticmethod
    def current_branch(path: Path) -> str:
        """Get current branch name."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""

    @staticmethod
    def create_branch(path: Path, branch: str, from_branch: str = "main") -> bool:
        """Create and checkout a new branch."""
        # Check if source branch exists
        check = subprocess.run(
            ["git", "rev-parse", "--verify", from_branch],
            cwd=path,
            capture_output=True
        )
        if check.returncode != 0:
            return False

        # Checkout source branch
        subprocess.run(["git", "checkout", from_branch], cwd=path, capture_output=True)

        # Pull if upstream exists
        upstream = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=path,
            capture_output=True
        )
        if upstream.returncode == 0:
            subprocess.run(["git", "pull", "--ff-only"], cwd=path, capture_output=True)

        # Create new branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch],
            cwd=path,
            capture_output=True
        )
        return result.returncode == 0

    @staticmethod
    def add_commit(path: Path, files: List[Path], message: str) -> bool:
        """Add files and commit."""
        for f in files:
            subprocess.run(["git", "add", str(f)], cwd=path, capture_output=True)

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=path,
            capture_output=True
        )
        return result.returncode == 0


class ProjectTree:
    """Generate project tree snapshots."""

    @staticmethod
    def generate(root: Path, excludes: Optional[Set[str]] = None) -> str:
        """Generate a tree structure of the project."""
        if excludes is None:
            excludes = {
                '.git', '.venv', 'venv', '__pycache__',
                'node_modules', 'dist', 'build', '.mypy_cache',
                '.pytest_cache', '.tox', '*.egg-info', '.DS_Store'
            }

        tree_lines = []

        def should_skip(path: Path) -> bool:
            name = path.name
            for pattern in excludes:
                if pattern.startswith('*') and name.endswith(pattern[1:]):
                    return True
                if name == pattern:
                    return True
            return False

        def walk_dir(dir_path: Path, prefix: str = ""):
            items = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name))
            items = [i for i in items if not should_skip(i)]

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{current}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    walk_dir(item, prefix + extension)

        tree_lines.append(".")
        walk_dir(root)
        return "\n".join(tree_lines)


class ContextPacker:
    """Package context files for AI agents."""

    @staticmethod
    def read_ignore_patterns(ignore_file: Path) -> Set[str]:
        """Read patterns from .agentpackignore file."""
        patterns = set()
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        else:
            # Default patterns
            patterns = {
                '.git', '.venv', '__pycache__', 'node_modules',
                'dist', 'build', '*.log', '*.bak', '*.tgz',
                '*.tar.gz', '*.zip', '.env*'
            }
        return patterns

    @staticmethod
    def should_exclude(path: Path, patterns: Set[str]) -> bool:
        """Check if path should be excluded based on patterns."""
        from pathlib import PurePath

        p = PurePath(path.as_posix())

        for pattern in patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                dir_pattern = pattern.rstrip('/')
                # Check if this is the directory itself or if it's inside the directory
                if path.is_dir() and p.match(dir_pattern):
                    return True
                if any(parent.match(dir_pattern) for parent in p.parents):
                    return True
            # Handle file/general patterns
            else:
                if p.match(pattern):
                    return True
                if any(parent.match(pattern) for parent in p.parents):
                    return True

        return False

    @staticmethod
    def pack(
        root: Path,
        output: Path,
        extra_files: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> List[Path]:
        """Create a context pack for AI agents."""
        # Default files to include
        context_files = [
            root / "context" / "development.md",
            root / "context" / "agents.md",
            root / "context" / "project_tree.md",
        ]

        # Add directory_notes if it exists
        dir_notes = root / "context" / "directory_notes"
        if dir_notes.exists():
            for note in dir_notes.rglob("*.md"):
                context_files.append(note)

        # Add extra files
        if extra_files:
            for extra in extra_files:
                extra_path = root / extra
                if extra_path.exists():
                    context_files.append(extra_path)

        # Filter out non-existent files
        context_files = [f for f in context_files if f.exists()]

        if dry_run:
            return context_files

        # Read ignore patterns
        ignore_file = root / ".agentpackignore"
        patterns = ContextPacker.read_ignore_patterns(ignore_file)

        # Create tarball
        with tarfile.open(output, "w:gz") as tar:
            for file_path in context_files:
                # Check if file should be excluded
                if not ContextPacker.should_exclude(file_path, patterns):
                    arcname = file_path.relative_to(root)
                    tar.add(file_path, arcname=str(arcname))

        return context_files


class FeatureOps:
    """Operations for feature branch management."""

    @staticmethod
    def create_feature(
        root: Path,
        name: str,
        branch_type: str = "feature",
        primary_goal: str = "",
        phase: str = "",
        force: bool = False
    ) -> bool:
        """Create a feature branch and update context."""
        # Check if working tree is clean
        if not force and not GitOps.is_clean(root):
            raise ValueError("Working tree not clean. Commit or stash changes, or use --force")

        # Create branch
        branch_name = f"{branch_type}/{name}"
        if not GitOps.create_branch(root, branch_name):
            raise ValueError(f"Failed to create branch {branch_name}")

        # Ensure context directory structure
        context_dir = root / "context"
        context_dir.mkdir(exist_ok=True)
        (context_dir / "directory_notes").mkdir(exist_ok=True)

        # Update or create development.md
        dev_file = context_dir / "development.md"
        if not dev_file.exists():
            dev_content = f"""# Development Log

**Phase:** {phase or 'Phase 1'}
**Primary Goal:** {primary_goal or 'To be defined'}

## Context Sync (AUTO-UPDATED)

- **Overall goal is:** {primary_goal or 'To be defined'}
- **Last action was:** Created feature branch {branch_name}
- **Next action will be:** {phase or 'Define first task'}
- **Blockers:** None
"""
            dev_file.write_text(dev_content)
        else:
            # Update existing file
            content = dev_file.read_text()

            # Update Primary Goal
            if primary_goal:
                import re
                content = re.sub(
                    r'\*\*Primary Goal:\*\*.*',
                    f'**Primary Goal:** {primary_goal}',
                    content
                )
                content = re.sub(
                    r'Overall goal is:.*',
                    f'Overall goal is: {primary_goal}',
                    content
                )

            # Update Phase
            if phase:
                content = re.sub(
                    r'\*\*Phase:\*\*.*',
                    f'**Phase:** {phase}',
                    content
                )
                content = re.sub(
                    r'Next action will be:.*',
                    f'Next action will be: {phase}',
                    content
                )

            # Update Last action
            content = re.sub(
                r'Last action was:.*',
                f'Last action was: Created feature branch {branch_name}',
                content
            )

            dev_file.write_text(content)

        # Create agents.md if missing
        agents_file = context_dir / "agents.md"
        if not agents_file.exists():
            agents_content = """# Agents Guide

This project uses a **Context Loop**. Always keep these fields current:

- **Overall goal is:** Single-sentence mission
- **Last action was:** What just completed
- **Next action will be:** The very next step
- **Blockers:** Known issues or decisions needed

### Working Rules for Agents
- Do not modify or examine ignored directories (see `.agentpackignore`). Assume large assets exist even if excluded.
- Prefer minimal, reversible changes.
- After committing code, run `bpsai-pair context-sync` to update the loop.
- Request a new context pack when the tree or docs change significantly.

### Context Pack
Run `bpsai-pair pack --out agent_pack.tgz` and upload to your session.
"""
            agents_file.write_text(agents_content)

        # Generate project tree
        tree_file = context_dir / "project_tree.md"
        tree_content = f"""# Project Tree (snapshot)
_Generated: {datetime.now(timezone.utc).isoformat()}Z_

```
{ProjectTree.generate(root)}
```
"""
        tree_file.write_text(tree_content)

        # Commit changes
        GitOps.add_commit(
            root,
            [dev_file, agents_file, tree_file],
            f"feat(context): start {branch_name} — Primary Goal: {primary_goal or 'TBD'}"
        )

        return True


class LocalCI:
    """Cross-platform local CI runner."""

    @staticmethod
    def run_python_checks(root: Path) -> dict:
        """Run Python linting, formatting, and tests."""
        results = {}

        # Check if Python project
        if not ((root / "pyproject.toml").exists() or (root / "requirements.txt").exists()):
            return results

        # Try to run ruff
        try:
            subprocess.run(["ruff", "format", "--check", "."], cwd=root, check=True)
            subprocess.run(["ruff", "check", "."], cwd=root, check=True)
            results["ruff"] = "passed"
        except:
            results["ruff"] = "failed or not installed"

        # Try to run mypy
        try:
            subprocess.run(["mypy", "."], cwd=root, check=True)
            results["mypy"] = "passed"
        except:
            results["mypy"] = "failed or not installed"

        # Try to run pytest
        try:
            subprocess.run(["pytest", "-q"], cwd=root, check=True)
            results["pytest"] = "passed"
        except:
            results["pytest"] = "failed or not installed"

        return results

    @staticmethod
    def run_node_checks(root: Path) -> dict:
        """Run Node.js linting, formatting, and tests."""
        results = {}

        if not (root / "package.json").exists():
            return results

        # Try npm commands
        try:
            subprocess.run(["npm", "run", "lint"], cwd=root, check=True)
            results["eslint"] = "passed"
        except:
            results["eslint"] = "failed or not configured"

        try:
            subprocess.run(["npm", "test"], cwd=root, check=True)
            results["npm test"] = "passed"
        except:
            results["npm test"] = "failed or not configured"

        return results

    @staticmethod
    def run_all(root: Path) -> dict:
        """Run all applicable CI checks."""
        results = {
            "python": LocalCI.run_python_checks(root),
            "node": LocalCI.run_node_checks(root)
        }
        return results
