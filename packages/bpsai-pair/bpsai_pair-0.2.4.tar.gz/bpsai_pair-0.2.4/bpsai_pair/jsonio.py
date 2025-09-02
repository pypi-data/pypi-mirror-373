from __future__ import annotations
import json
from typing import Any, Dict

def dump(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)