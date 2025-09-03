from __future__ import annotations

from contextlib import suppress


def parse_price(value: str | float | int | None) -> float:
    """Parse a price string like "$1.50" to a float 1.5.

    Returns 0.0 on None or unparsable input.
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    with suppress(Exception):
        if s.startswith("$"):
            s = s[1:]
    with suppress(Exception):
        return float(s)
    return 0.0


def extract_gpu_info(instance_type: str | None) -> tuple[str, int]:
    """Return (gpu_type, count) from an instance_type string.

    Heuristic, resilient, and side-effect free. Defaults to ("default", 1).
    """
    if not instance_type:
        return "default", 1
    s = instance_type.lower()
    gpu_type = "default"
    for t in ("h100", "a100", "a10", "t4"):
        if t in s:
            gpu_type = t
            break
    count = 1
    with suppress(Exception):
        if "x" in s:
            prefix, _ = s.split("x", 1)
            if prefix.isdigit():
                count = max(1, int(prefix))
    return gpu_type, count
