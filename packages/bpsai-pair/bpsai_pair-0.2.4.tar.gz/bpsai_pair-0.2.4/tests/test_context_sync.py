"""Test context sync functionality."""
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bpsai_pair import ops
from bpsai_pair.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_context_sync_updates(tmp_path):
    """Test that context sync updates the development.md file."""
    # Setup
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    dev_file = context_dir / "development.md"

    dev_content = """# Development Log

**Phase:** X
**Primary Goal:** Y

## Context Sync (AUTO-UPDATED)

Overall goal is: old goal
Last action was: old action
Next action will be: old next
Blockers: none
"""
    dev_file.write_text(dev_content)

    # Mock git repo check
    with patch.object(ops.GitOps, 'is_repo', return_value=True):
        with patch('os.getcwd', return_value=str(tmp_path)):
            # Run context-sync command
            result = runner.invoke(app, [
                "context-sync",
                "--last", "New action completed",
                "--next", "Next step to take",
                "--blockers", "Some blocker"
            ])

    # Verify
    assert result.exit_code == 0
    updated_content = dev_file.read_text()
    assert "Last action was: New action completed" in updated_content
    assert "Next action will be: Next step to take" in updated_content
    assert "Blockers/Risks: Some blocker" in updated_content
