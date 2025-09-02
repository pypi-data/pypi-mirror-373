from pathlib import Path

def repo_root() -> Path:
    p = Path.cwd()
    if not (p / ".git").exists():
        raise SystemExit("Run from repo root (where .git exists).")
    return p

def ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | 0o111)
