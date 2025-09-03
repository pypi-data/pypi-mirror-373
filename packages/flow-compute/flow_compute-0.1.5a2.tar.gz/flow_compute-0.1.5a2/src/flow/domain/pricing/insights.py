"""Pricing insights: defaults/overrides and market-derived recommendations.

This module provides small, provider-agnostic helpers to:
- Merge default pricing with user overrides
- Compute per-instance limit prices for common GPU counts
- Aggregate market listings into quantiles (P50/P90/P95) per GPU/region
- Derive recommended limit prices from quantiles

The helpers return plain dicts for easy consumption by CLI/UI/SDK and
to keep dependencies light.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

# ---------- Basics / Utilities ----------


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Compute a percentile from a non-empty sorted list.

    Uses linear interpolation between closest ranks. For small N, this is
    good enough; callers can surface a confidence score via sample size.
    """
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    if n == 1:
        return float(sorted_values[0])
    # Clamp percentile
    if pct <= 0:
        return float(sorted_values[0])
    if pct >= 100:
        return float(sorted_values[-1])
    # Rank position (0-indexed)
    pos = (pct / 100.0) * (n - 1)
    low = int(pos)
    high = min(low + 1, n - 1)
    frac = pos - low
    return float(sorted_values[low] * (1 - frac) + sorted_values[high] * frac)


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "-"
    try:
        return f"${float(value):.2f}/hr"
    except Exception:
        return "-"


def _infer_gpu_type_from_name(name: str) -> str:
    s = (name or "").lower()
    for tok in ("h100", "a100", "a10", "t4"):
        if tok in s:
            return tok
    return "unknown"


# ---------- Defaults / Overrides ----------


@dataclass
class DefaultsInsight:
    table: dict[str, dict[str, float]]  # per-GPU: {low, med, high}
    base: dict[str, dict[str, float]]
    overrides: dict[str, dict[str, float]]


def build_defaults_insight(
    *, base: dict[str, dict[str, float]], overrides: dict[str, dict[str, float]] | None = None
) -> DefaultsInsight:
    """Merge base pricing with overrides and surface what changed."""
    overrides = overrides or {}
    merged: dict[str, dict[str, float]] = {}
    for gpu in {**base, **overrides}.keys():
        merged[gpu] = {**base.get(gpu, {}), **overrides.get(gpu, {})}
    return DefaultsInsight(table=merged, base=base, overrides=overrides)


def per_instance_caps(per_gpu: float, gpu_counts: Iterable[int]) -> dict[int, float]:
    """Compute per-instance limit prices for given GPU counts from a per-GPU price."""
    caps: dict[int, float] = {}
    for c in gpu_counts:
        try:
            cc = max(1, int(c))
            caps[cc] = float(per_gpu) * cc
        except Exception:
            continue
    return caps


# ---------- Market aggregation ----------


def aggregate_market(
    listings: Iterable[dict[str, Any]],
    *,
    target_gpu: str | None = None,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Aggregate listings into quantiles per GPU and region.

    Args:
        listings: Iterable of dicts with keys: region, gpu_type, price_per_hour
        target_gpu: optional filter to restrict to a GPU type (e.g., "h100")

    Returns:
        { gpu_type: { region: { 'p50': float, 'p90': float, 'p95': float, 'n': int } } }
    """
    # Collect prices per (gpu_type, region)
    buckets: dict[str, dict[str, list[float]]] = {}
    for item in listings:
        try:
            gpu = (item.get("gpu_type") or "").lower()
            if not gpu:
                # Try to infer from instance_type/name when missing
                gpu = _infer_gpu_type_from_name(item.get("instance_type") or item.get("name") or "")
            if target_gpu and gpu != target_gpu.lower():
                continue
            rgn = str(item.get("region") or "")
            price = float(item.get("price_per_hour"))
            if price <= 0 or not rgn:
                continue
            buckets.setdefault(gpu, {}).setdefault(rgn, []).append(price)
        except Exception:
            continue

    # Compute quantiles per bucket
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for gpu, by_region in buckets.items():
        result[gpu] = {}
        for rgn, prices in by_region.items():
            if not prices:
                continue
            prices.sort()
            n = len(prices)
            result[gpu][rgn] = {
                "p50": _percentile(prices, 50),
                "p90": _percentile(prices, 90),
                "p95": _percentile(prices, 95),
                "n": n,
            }
    return result


def derive_recommendations(
    stats: dict[str, dict[str, dict[str, Any]]],
    *,
    multipliers: dict[str, float] | None = None,
) -> dict[str, dict[str, dict[str, float]]]:
    """From quantiles, derive recommended per-GPU limit prices for low/med/high.

    Default multipliers (explainable, conservative):
        low = p50 * 1.15
        med = p90 * 1.10
        high = p95 * 1.25
    """
    m = multipliers or {"low": 1.15, "med": 1.10, "high": 1.25}
    out: dict[str, dict[str, dict[str, float]]] = {}
    for gpu, by_region in stats.items():
        out[gpu] = {}
        for rgn, q in by_region.items():
            p50, p90, p95 = float(q.get("p50", 0)), float(q.get("p90", 0)), float(q.get("p95", 0))
            out[gpu][rgn] = {
                "low": round(p50 * m.get("low", 1.0), 2),
                "med": round(p90 * m.get("med", 1.0), 2),
                "high": round(p95 * m.get("high", 1.0), 2),
            }
    return out


def top_regions(
    stats: dict[str, dict[str, dict[str, Any]]],
    *,
    gpu: str,
    by: str = "p50",
    k: int = 3,
) -> list[tuple[str, dict[str, Any]]]:
    """Return top-k regions for a gpu sorted by a given quantile key (asc)."""
    data = stats.get(gpu.lower()) or {}
    items = [(r, q) for r, q in data.items() if by in q]
    items.sort(key=lambda rq: float(rq[1].get(by, 0.0)))
    return items[:k]
