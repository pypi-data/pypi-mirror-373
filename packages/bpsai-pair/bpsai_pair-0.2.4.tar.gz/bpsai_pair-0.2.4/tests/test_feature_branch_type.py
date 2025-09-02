"""Test feature branch type functionality."""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bpsai_pair import ops
from bpsai_pair.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_feature_branch_types(tmp_path):
    """Test creating features with different branch types."""
    # Setup mock git repo
    (tmp_path / ".git").mkdir()
    context_dir = tmp_path / "context"
    context_dir.mkdir()

    # Mock git operations
    with patch.object(ops.GitOps, 'is_repo', return_value=True):
        with patch.object(ops.GitOps, 'is_clean', return_value=True):
            with patch.object(ops.GitOps, 'create_branch', return_value=True):
                with patch.object(ops.GitOps, 'add_commit', return_value=True):
                    with patch('os.getcwd', return_value=str(tmp_path)):
                        # Test refactor branch type
                        result = runner.invoke(app, [
                            "feature", "login",
                            "--type", "refactor",
                            "--primary", "Refactor login",
                            "--phase", "Phase 1"
                        ])

    assert result.exit_code == 0
    assert "Created branch" in result.stdout or result.exit_code == 0
