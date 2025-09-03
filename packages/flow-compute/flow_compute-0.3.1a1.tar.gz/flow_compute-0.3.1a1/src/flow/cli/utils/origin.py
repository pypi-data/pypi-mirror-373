"""Origin detection utilities.

Lightweight helpers to consistently tag where a Flow operation originated from
(CLI vs SDK), without introducing leaky abstractions.

Rules:
- CLI sets FLOW_ORIGIN=flow-cli in its entrypoint.
- Libraries/programmatic usage (SDK) defaults to flow-compute.
- Tests or advanced users can override with FLOW_ORIGIN.

These helpers are intentionally tiny and provider-agnostic.
"""

from __future__ import annotations

import os


def detect_origin() -> str:
    """Return the current process origin string.

    Precedence:
    1) FLOW_ORIGIN env var if present (must be a short token)
    2) Default to "flow-compute"
    """
    val = (os.environ.get("FLOW_ORIGIN") or "").strip().lower()
    if not val:
        return "flow-compute"
    # Sanitize to a small allowlist to avoid noisy/tagged values
    allowed = {"flow-cli", "flow-compute", "external", "unknown"}
    return val if val in allowed else "flow-compute"


def set_cli_origin_env() -> None:
    """Best-effort: mark this process as CLI-originating.

    Does not override if the user explicitly set FLOW_ORIGIN.
    """
    if not os.environ.get("FLOW_ORIGIN"):
        os.environ["FLOW_ORIGIN"] = "flow-cli"


__all__ = ["detect_origin", "set_cli_origin_env"]
