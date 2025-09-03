from __future__ import annotations

"""Local transport placeholder for providers without SSH.

This module provides a minimal, provider-agnostic stub that conforms to the
`Transport` Protocol for environments where SSH is not applicable (e.g.,
local provider). It is intentionally conservative and not wired by default.

Providers may choose to compose and expose this transport (or their own
specialized variant) via a `get_transport()` helper similar to Mithril.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LocalConnectionInfo:
    host: str = "localhost"
    port: int = 0
    user: str = ""
    key_path: Path | None = None
    task_id: str = ""


class LocalTransport:
    def wait_for_ssh(self, task: object, timeout: int | None = None) -> LocalConnectionInfo:  # type: ignore[override]
        # Local provider does not use SSH; return a stub connection description
        return LocalConnectionInfo(task_id=str(getattr(task, "task_id", "")))

    def upload_code(self, task: object, source_dir: object, target_dir: str = "~") -> Any:  # type: ignore[override]
        # No-op by default. Providers can implement file sync to a local path if desired.
        return {
            "success": True,
            "bytes_transferred": 0,
            "files_transferred": 0,
            "target_dir": target_dir,
        }
