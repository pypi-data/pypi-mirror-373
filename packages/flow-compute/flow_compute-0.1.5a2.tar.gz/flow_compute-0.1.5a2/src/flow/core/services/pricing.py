"""Centralized pricing configuration for Flow SDK (core service).

Single source of truth for GPU pricing defaults and helpers.
"""

from __future__ import annotations

import re

try:
    # Prefer robust parser that understands variants like
    # "8xh100", "h100-80gb.sxm.8x", "gpu.nvidia.h100"
    from flow.domain.parsers.instance_parser import InstanceParser
except Exception:  # pragma: no cover - fallback path
    InstanceParser = None  # type: ignore[assignment]

# Single source of truth for default pricing
# Prices are per-GPU per-hour in USD
DEFAULT_PRICING = {
    "h100": {"low": 4.0, "med": 8.0, "high": 16.0},
    "a100": {"low": 3.0, "med": 6.0, "high": 12.0},
    "a10": {"low": 1.0, "med": 2.0, "high": 4.0},
    "t4": {"low": 0.5, "med": 1.0, "high": 2.0},
    "default": {"low": 2.0, "med": 4.0, "high": 8.0},
}


def extract_gpu_info(instance_type: str) -> tuple[str, int]:
    """Extract GPU type and count from instance type string."""
    # Robust path: use central parser when available
    try:
        if InstanceParser is not None:
            comps = InstanceParser.parse(instance_type)
            return comps.gpu_type, int(max(1, comps.gpu_count))
    except Exception:
        # Fall back to regex-based heuristics below
        pass

    # Heuristic fallback for environments where InstanceParser is unavailable
    spec = instance_type.strip().lower()

    # 1) Handle trailing count form (e.g., "h100-80gb.sxm.8x")
    trailing = re.search(r"(?:^|\.)((\d+)x)$", spec)
    if trailing:
        gpu_count = int(trailing.group(2))
        # Remove trailing ".8x" to recover the base GPU token
        base = re.sub(r"(\.|-)?\d+x$", "", spec)
        # Take leftmost token as GPU family (split on '-' then '.')
        gpu_type = base.split("-")[0].split(".")[0]
        return gpu_type, gpu_count

    # 2) Prefix count form (e.g., "8xh100")
    match = re.match(r"(\d+)x([a-z0-9-]+)", spec)
    if match:
        return match.group(2).split("-")[0], int(match.group(1))

    # 3) API-style or simple names (e.g., "gpu.nvidia.h100", "a100-80gb")
    if "." in spec:
        parts = spec.split(".")
        # Prefer last non-count token as GPU family
        for token in reversed(parts):
            if not token.endswith("x") and not token.isdigit():
                return token.split("-")[0], 1

    # 4) Fallback: treat first token as GPU family; assume single GPU
    return spec.split("-")[0].split(".")[0], 1


def get_pricing_table(config_overrides: dict | None = None) -> dict:
    """Get pricing table with optional config overrides."""
    if not config_overrides:
        return DEFAULT_PRICING

    # Deep merge to support partial overrides
    result = {}
    for gpu_type, prices in DEFAULT_PRICING.items():
        result[gpu_type] = prices.copy()

    for gpu_type, prices in config_overrides.items():
        if gpu_type in result:
            result[gpu_type].update(prices)
        else:
            result[gpu_type] = prices

    return result


def calculate_instance_price(
    instance_type: str, priority: str = "med", pricing_table: dict | None = None
) -> float:
    """Calculate total price for instance type and priority tier."""
    if pricing_table is None:
        pricing_table = DEFAULT_PRICING

    gpu_type, gpu_count = extract_gpu_info(instance_type)

    # Get prices for GPU type, fall back to default
    gpu_prices = pricing_table.get(gpu_type, pricing_table.get("default", {}))

    # Get price for tier, fall back to med
    per_gpu_price = gpu_prices.get(priority, gpu_prices.get("med", 4.0))

    return per_gpu_price * gpu_count


def parse_price(price_str: str | None) -> float:
    """Parse a price string like "$10.00" into a float."""
    if not price_str:
        return 0.0
    try:
        clean = str(price_str).strip().lstrip("$").replace(",", "").strip()
        return float(clean)
    except Exception:
        return 0.0
