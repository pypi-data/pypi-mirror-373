"""Tests for configuration module."""
from pathlib import Path
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bpsai_pair.config import Config, ContextTemplate


def test_default_config():
    """Test default configuration."""
    config = Config()
    assert config.project_name == "My Project"
    assert config.coverage_target == 80
    assert config.main_branch == "main"


def test_config_save_load(tmp_path):
    """Test saving and loading config."""
    config = Config(
        project_name="Test Project",
        primary_goal="Test Goal",
        coverage_target=90
    )
    config.save(tmp_path)

    assert (tmp_path / ".paircoder.yml").exists()

    loaded = Config.load(tmp_path)
    assert loaded.project_name == "Test Project"
    assert loaded.coverage_target == 90


def test_env_override(tmp_path, monkeypatch):
    """Test environment variable override."""
    monkeypatch.setenv("PAIRCODER_MAIN_BRANCH", "master")
    monkeypatch.setenv("PAIRCODER_PROJECT_NAME", "EnvProject")

    config = Config.load(tmp_path)
    assert config.main_branch == "master"
    assert config.project_name == "EnvProject"


def test_development_template():
    """Test template generation."""
    config = Config(project_name="Test", primary_goal="Build")
    template = ContextTemplate.development_md(config)

    assert "Test" in template
    assert "Build" in template
    assert "Context Sync" in template
