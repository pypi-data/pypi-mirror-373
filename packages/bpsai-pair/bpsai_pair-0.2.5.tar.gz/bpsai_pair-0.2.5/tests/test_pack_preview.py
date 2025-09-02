"""Test pack preview functionality."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bpsai_pair import ops
from bpsai_pair.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_pack_preview_and_list(tmp_path):
    """Test pack preview, list, and JSON output."""
    # Setup
    (tmp_path / ".git").mkdir()
    context_dir = tmp_path / "context"
    context_dir.mkdir()

    dev_file = context_dir / "development.md"
    dev_file.write_text("# Development Log\n")

    agents_file = context_dir / "agents.md"
    agents_file.write_text("# Agents Guide\n")

    tree_file = context_dir / "project_tree.md"
    tree_file.write_text("# Project Tree\n")

    ignore_file = tmp_path / ".agentpackignore"
    ignore_file.write_text(".git/\n.venv/\n")

    with patch.object(ops.GitOps, 'is_repo', return_value=True):
        with patch('os.getcwd', return_value=str(tmp_path)):
            # Test dry-run
            result = runner.invoke(app, ["pack", "--dry-run"])
            assert result.exit_code == 0
            assert "Would pack" in result.stdout

            # Test list
            result = runner.invoke(app, ["pack", "--list"])
            assert result.exit_code == 0
            assert "context/development.md" in result.stdout

            # Test JSON output
            result = runner.invoke(app, ["pack", "--json", "--dry-run"])
            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert "files" in data
            assert data["dry_run"] == True
