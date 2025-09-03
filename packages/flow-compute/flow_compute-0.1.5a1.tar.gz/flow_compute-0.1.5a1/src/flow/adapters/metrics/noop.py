from __future__ import annotations

from flow.protocols.metrics import MetricsProtocol


class NoopMetrics(MetricsProtocol):
    def increment(self, name: str, value: float = 1.0, **tags: str) -> None:  # noqa: D401
        return None

    def timing(self, name: str, ms: float, **tags: str) -> None:  # noqa: D401
        return None
