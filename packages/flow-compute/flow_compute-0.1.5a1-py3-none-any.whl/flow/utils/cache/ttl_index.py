"""Generic TTL-backed JSON cache helper.

Provides a small utility to persist a JSON payload with a timestamp and
enforce a time-to-live when loading. Designed for ephemeral CLI index caches.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TTLIndex:
    """Small helper to persist JSON payloads with TTL enforcement.

    Notes:
    - Uses a migration-friendly schema: ``{"timestamp": <float>, ...payload}``.
      This matches existing caches so legacy readers continue to work.
    - On load, returns ``None`` if file missing, invalid, or expired.
    """

    path: Path
    ttl_seconds: int

    def load(self) -> dict[str, Any] | None:
        """Load cache if present and fresh; otherwise return None."""
        try:
            if not self.path.exists():
                return None
            data = json.loads(self.path.read_text())
            ts = float(data.get("timestamp", 0))
            if time.time() - ts > self.ttl_seconds:
                return None
            return data
        except Exception:
            return None

    def save(self, payload: dict[str, Any]) -> None:
        """Atomically save payload with current timestamp."""
        tmp = self.path.with_suffix(".tmp")
        to_write = {"timestamp": time.time(), **payload}
        tmp.write_text(json.dumps(to_write, indent=2))
        tmp.replace(self.path)

    def clear(self) -> None:
        try:
            if self.path.exists():
                self.path.unlink()
        except Exception:
            pass
