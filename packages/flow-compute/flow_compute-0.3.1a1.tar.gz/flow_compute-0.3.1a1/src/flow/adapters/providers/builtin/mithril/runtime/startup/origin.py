"""Flow origin header utilities for startup scripts.

Provides a single, consistent header line that is injected at the top of all
startup scripts (inline, compressed, and remote-download bootstraps). The
header allows us to reliably detect Flow-origin tasks from Mithril bid data
without requiring server-side metadata support.
"""

from __future__ import annotations

import os
import random
import string

from flow._version import __version__ as flow_version
from flow.cli.utils.origin import detect_origin

_SESSION_ID: str | None = None


def _generate_session_id(length: int = 6) -> str:
    """Generate a short, non-sensitive session identifier.

    Uses lowercase base36 characters for compactness. The session identifier is
    intended only for correlating tasks within a single client session. It MUST
    NOT contain sensitive data.
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def get_flow_session_id() -> str:
    """Get a stable per-process session identifier for Flow startup scripts.

    Respects environment override via FLOW_SESSION_ID for debugging/testing.
    """
    global _SESSION_ID
    if _SESSION_ID:
        return _SESSION_ID

    override = os.environ.get("FLOW_SESSION_ID")
    if override:
        _SESSION_ID = override.strip()
    else:
        _SESSION_ID = _generate_session_id(6)
    return _SESSION_ID


def get_flow_origin_header() -> str:
    """Return the canonical Flow origin header comment line.

    Example:
        # FLOW_ORIGIN: flow-cli v0.9.2 session:abc123
    """
    session = get_flow_session_id()
    origin = detect_origin()
    # Export FLOW_ORIGIN to environment for downstream sections/telemetry
    return (
        f'# FLOW_ORIGIN: {origin} v{flow_version} session:{session}\nexport FLOW_ORIGIN="{origin}"'
    )
