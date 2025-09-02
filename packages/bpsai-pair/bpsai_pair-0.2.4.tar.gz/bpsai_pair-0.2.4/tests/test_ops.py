"""Tests for operations module."""
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bpsai_pair import ops


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Initial commit
    (repo / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, capture_output=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo, capture_output=True)

    return repo


def test_is_repo(temp_repo, tmp_path):
    """Test repo detection."""
    assert ops.GitOps.is_repo(temp_repo) == True
    assert ops.GitOps.is_repo(tmp_path) == False


def test_is_clean(temp_repo):
    """Test clean detection."""
    assert ops.GitOps.is_clean(temp_repo) == True

    # Make dirty
    (temp_repo / "test.txt").write_text("test")
    assert ops.GitOps.is_clean(temp_repo) == False


def test_current_branch(temp_repo):
    """Test getting current branch."""
    branch = ops.GitOps.current_branch(temp_repo)
    assert branch == "main"


def test_project_tree(temp_repo):
    """Test tree generation."""
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "main.py").write_text("print('hello')")

    tree = ops.ProjectTree.generate(temp_repo)
    assert "src" in tree
    assert "main.py" in tree
    assert ".git" not in tree  # Should be excluded


def test_context_packer_patterns():
    """Test exclusion patterns."""
    patterns = {".git", "*.log", "node_modules"}

    assert ops.ContextPacker.should_exclude(Path(".git"), patterns) == True
    assert ops.ContextPacker.should_exclude(Path("test.log"), patterns) == True
    assert ops.ContextPacker.should_exclude(Path("main.py"), patterns) == False


def test_pack_respects_directory_ignore(tmp_path):
    """Ensure directory patterns exclude contents from pack."""
    root = tmp_path

    context_dir = root / "context"
    context_dir.mkdir()
    (context_dir / "development.md").write_text("dev")
    (context_dir / "agents.md").write_text("agents")
    (context_dir / "project_tree.md").write_text("tree")

    private_dir = root / "private"
    private_dir.mkdir()
    (private_dir / "secret.txt").write_text("shh")

    (root / ".agentpackignore").write_text("private/\n")

    output = root / "pack.tgz"
    ops.ContextPacker.pack(root, output, extra_files=["private/secret.txt"])

    with tarfile.open(output, "r:gz") as tar:
        names = tar.getnames()

    assert "context/development.md" in names
    assert "private/secret.txt" not in names
