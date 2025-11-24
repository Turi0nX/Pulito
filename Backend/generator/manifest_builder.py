from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from generator.config import GITHUB_PAGES_URL, OUTPUT_DIR, VERSION


@dataclass
class Manifest:
    kind: str            # "base" o "pro"
    version: str
    generated_at: str
    blocker_list_url: str
    blocker_list_sha256: str


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(kind: str, filename: str) -> Dict[str, Any]:
    blocker_path = Path(OUTPUT_DIR) / filename
    sha = compute_sha256(blocker_path)

    m = Manifest(
        kind=kind,
        version=VERSION,
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        blocker_list_url=f"{GITHUB_PAGES_URL.rstrip('/')}/{filename}",
        blocker_list_sha256=sha,
    )
    return asdict(m)