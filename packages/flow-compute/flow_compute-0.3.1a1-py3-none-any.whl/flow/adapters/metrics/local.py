from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flow.adapters.integrations.health.storage import MetricsBatcher, MetricsStore
from flow.protocols.metrics import MetricsProtocol


@dataclass
class LocalMetrics(MetricsProtocol):
    """Lightweight metrics adapter writing locally with optional remote batching.

    - `increment(name, value, **tags)` emits a counter metric
    - `timing(name, ms, **tags)` emits a timing metric in milliseconds

    Records are batched via `MetricsBatcher` and flushed to a local JSONL store
    with optional remote streaming when an endpoint is configured.
    """

    batcher: MetricsBatcher
    default_tags: dict[str, str]

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        batch_size: int = 100,
        flush_interval: int = 60,
        base_path: str | None = None,
        retention_days: int = 7,
        compress_after_days: int = 1,
        default_tags: dict[str, str] | None = None,
        api_key: str | None = None,
    ) -> None:
        store = MetricsStore(
            base_path=None if base_path is None else __import__("pathlib").Path(base_path),
            retention_days=retention_days,
            compress_after_days=compress_after_days,
        )
        self.batcher = MetricsBatcher(
            store=store,
            endpoint=endpoint,
            batch_size=batch_size,
            flush_interval=flush_interval,
            api_key=api_key,
        )
        self.default_tags = default_tags or {}

    def increment(self, name: str, value: float = 1.0, **tags: str) -> None:
        payload: dict[str, Any] = {
            "type": "counter",
            "name": name,
            "value": float(value),
            "tags": {**self.default_tags, **tags},
        }
        self.batcher.add(payload)

    def timing(self, name: str, ms: float, **tags: str) -> None:
        payload: dict[str, Any] = {
            "type": "timing",
            "name": name,
            "ms": float(ms),
            "tags": {**self.default_tags, **tags},
        }
        self.batcher.add(payload)


def from_health_config(cfg: dict[str, Any] | None) -> MetricsProtocol:
    """Build a LocalMetrics instance from a health configuration dict.

    Expected keys (all optional):
      - metrics_endpoint: str | None
      - metrics_batch_size: int
      - metrics_interval: int
      - retention_days: int
      - compress_after_days: int

    Returns a `LocalMetrics` configured with safe defaults when values are
    missing. This helper avoids importing application config types here.
    """
    cfg = cfg or {}
    endpoint = cfg.get("metrics_endpoint")
    batch_size = int(cfg.get("metrics_batch_size", 100) or 100)
    interval = int(cfg.get("metrics_interval", 60) or 60)
    retention_days = int(cfg.get("retention_days", 7) or 7)
    compress_after_days = int(cfg.get("compress_after_days", 1) or 1)
    return LocalMetrics(
        endpoint=endpoint,
        batch_size=batch_size,
        flush_interval=interval,
        retention_days=retention_days,
        compress_after_days=compress_after_days,
    )
