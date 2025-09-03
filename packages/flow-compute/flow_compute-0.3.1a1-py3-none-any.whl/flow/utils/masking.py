from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

__all__ = [
    "mask_text",
    # Structured value masking helpers
    "mask_sensitive_value",
    "mask_strict_last4",
    "mask_api_key",
    "mask_ssh_key_fingerprint",
    "mask_config_for_display",
]

# -------- Free-text redaction (log-safe) --------
_TOKEN_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([^\s,;]+)")


def mask_text(text: str) -> str:
    """Mask sensitive substrings in the given text.

    Redacts common credential-like key=value pairs. Best-effort redaction to
    avoid leaking secrets in logs.
    """

    def _repl(m: re.Match[str]) -> str:
        key = m.group(1)
        value = m.group(2)
        if len(value) <= 4:
            redacted = "***"
        else:
            redacted = value[:2] + "***" + value[-2:]
        # Normalize to key=value form for consistency
        return f"{key}={redacted}"

    try:
        return _TOKEN_RE.sub(_repl, text)
    except Exception:
        return text


# -------- Structured value masking (display-safe) --------
if TYPE_CHECKING:  # Only for type checkers; not executed at runtime
    ConfigFieldType = Any
else:
    ConfigFieldType = Any


def mask_sensitive_value(
    value: str | None, head: int = 8, tail: int = 4, min_length: int = 10
) -> str:
    """Mask a sensitive value for display.

    Returns a general placeholder for short or missing values.
    """
    if not value:
        return "[NOT SET]"

    if len(value) <= min_length:
        return "[CONFIGURED]"

    return f"{value[:head]}...{value[-tail:]}"


def mask_strict_last4(value: str | None, min_length: int = 10) -> str:
    """Strict masking that reveals only the last 4 characters."""
    if not value:
        return "[NOT SET]"

    if len(value) <= min_length:
        return "[CONFIGURED]"

    return f"••••{value[-4:]}"


def mask_api_key(api_key: str | None) -> str:
    """Mask an API key for safe display using strict last-4 style."""
    return mask_strict_last4(api_key)


def mask_ssh_key_fingerprint(fingerprint: str | None) -> str:
    """Mask an SSH key fingerprint for display."""
    return mask_sensitive_value(fingerprint, head=12, tail=8, min_length=20)


def mask_config_for_display(
    config: dict[str, Any], fields: list[ConfigFieldType]
) -> dict[str, Any]:
    """Return a masked copy of a configuration dict for safe display.

    Any field that is marked with ``mask_display`` in the provided field specs
    will be masked using strict last-4 if the value is a string.
    """
    masked: dict[str, Any] = dict(config)
    try:
        field_map = {getattr(f, "name", None): f for f in fields}
    except Exception:
        field_map = {}

    for key, value in list(config.items()):
        field = field_map.get(key)
        if field and getattr(field, "mask_display", False) and isinstance(value, str):
            masked[key] = mask_strict_last4(value)

    return masked
