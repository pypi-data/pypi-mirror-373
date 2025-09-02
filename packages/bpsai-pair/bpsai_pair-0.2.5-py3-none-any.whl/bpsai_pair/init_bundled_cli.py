from __future__ import annotations
import os, sys, stat, shutil
from pathlib import Path
try:
    from importlib.resources import files as res_files
except ImportError:
    from importlib_resources import files as res_files  # py<=3.8 fallback

APP_NAME = "bpsai-pair-init"

def copytree_non_destructive(src: Path, dst: Path) -> None:
    # copy files/dirs only if missing; never overwrite existing files
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        out_dir = dst / rel
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in files:
            s = Path(root) / name
            d = out_dir / name
            if not d.exists():
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
    # make scripts executable
    scripts_dir = dst / "scripts"
    if scripts_dir.exists():
        for p in scripts_dir.glob("*.sh"):
            mode = p.stat().st_mode
            p.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    # Resolve packaged template '{{cookiecutter.project_slug}}'
    pkg_root = res_files("bpsai_pair") / "data" / "cookiecutter-paircoder"
    # Find the one subdir under cookiecutter-paircoder (the cookiecutter slug dir)
    candidates = [p for p in pkg_root.iterdir() if p.is_dir()]
    if not candidates:
        print(f"[{APP_NAME}] ERROR: packaged template not found", file=sys.stderr)
        return 1
    template_root = candidates[0]  # '{{cookiecutter.project_slug}}'
    # copy into current directory without clobber
    dst = Path(".").resolve()
    copytree_non_destructive(Path(template_root), dst)
    print(f"[{APP_NAME}] Initialized repo with bundled scaffolding (non-destructive). Review diffs and commit.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
