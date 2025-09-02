"""Tests for CLI commands."""
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bpsai_pair.cli import app
from bpsai_pair import ops

runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Create initial commit
    (repo / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)

    # Create main branch
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, check=True, capture_output=True)

    return repo


@pytest.fixture
def initialized_repo(temp_repo):
    """Create a repo with PairCoder initialized."""
    context_dir = temp_repo / "context"
    context_dir.mkdir()
    (context_dir / "development.md").write_text("""# Development Log

**Phase:** Phase 1
**Primary Goal:** Test Goal

## Context Sync (AUTO-UPDATED)

Overall goal is: Test Goal
Last action was: Init
Next action will be: Test
Blockers: None
""")
    (context_dir / "agents.md").write_text("# Agents Guide\n")
    (context_dir / "project_tree.md").write_text("# Project Tree\n```\n.\n```")
    (temp_repo / ".agentpackignore").write_text(".git/\n.venv/\n")

    return temp_repo


def test_version():
    """Test version display."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "bpsai-pair" in result.stdout


def test_init_not_in_repo(tmp_path, monkeypatch):
    """Test init when not in a git repo."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "Not in a git repository" in result.stdout


def test_status_basic(initialized_repo, monkeypatch):
    """Test status command."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "PairCoder Status" in result.stdout


def test_context_sync(initialized_repo, monkeypatch):
    """Test context sync."""
    monkeypatch.chdir(initialized_repo)

    result = runner.invoke(app, [
        "context-sync",
        "--last", "Did something",
        "--next", "Do something else"
    ])
    assert result.exit_code == 0
    assert "Context Sync updated" in result.stdout

    # Check file was updated
    content = (initialized_repo / "context" / "development.md").read_text()
    assert "Last action was: Did something" in content


def test_validate(initialized_repo, monkeypatch):
    """Test validate command."""
    monkeypatch.chdir(initialized_repo)

    # Add missing files first
    (initialized_repo / ".editorconfig").touch()
    (initialized_repo / "CONTRIBUTING.md").touch()

    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
