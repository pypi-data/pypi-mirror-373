import subprocess
from pathlib import Path
from typing import List

class Shell:
    @staticmethod
    def run(cmd: List[str], cwd: Path | None = None, check: bool = True) -> str:
        res = subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)
        return (res.stdout or "") + (res.stderr or "")
