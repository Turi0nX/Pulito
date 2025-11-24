import json
import os
from pathlib import Path
from typing import Any, Dict


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(data: Dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    ensure_parent_dir(target)
    # Safe write: write to temp and then replace
    tmp_path = target.with_suffix(target.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(tmp_path, target)