from __future__ import annotations
from pathlib import Path
from typing import Iterable, List

def project_files(root: Path, excludes: Iterable[str] | None = None) -> List[Path]:
    """
    Return project files relative to root, respecting simple directory/file excludes.
    Excludes are glob-like segments (e.g., '.git/', '.venv/', '__pycache__/').
    This is intentionally minimal and cross-platform safe.
    """
    ex = list(excludes or [])
    out: List[Path] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        # skip directories that match excludes early
        if any(str(rel).startswith(e.rstrip("/")) for e in ex):
            # if it's a dir, skip its subtree
            if p.is_dir():
                # rely on rglob: cannot prune; filtering below suffices
                pass
        if p.is_file():
            s = str(rel)
            if any(s.startswith(e.rstrip("/")) for e in ex):
                continue
            out.append(rel)
    return out