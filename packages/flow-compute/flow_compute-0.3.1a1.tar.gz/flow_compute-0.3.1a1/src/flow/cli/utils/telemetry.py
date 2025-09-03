"""Opt-in telemetry for Flow CLI (stdonly).

Standalone implementation to avoid CLI->adapters import violations.
Writes JSONL events to ~/.flow/metrics.jsonl when FLOW_TELEMETRY=1.
Never raises; best-effort only.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CommandMetric:
    command: str
    duration: float
    success: bool
    error_type: str | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


@dataclass
class EventMetric:
    event: str
    properties: dict[str, Any]
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class Telemetry:
    def __init__(self) -> None:
        self.enabled = os.environ.get("FLOW_TELEMETRY", "0") == "1"
        self.metrics_file = Path.home() / ".flow" / "metrics.jsonl"
        self._lock = threading.Lock()

    def track_command(self, command: str):
        class CommandTracker:
            def __init__(self, telemetry: Telemetry, command: str) -> None:
                self.telemetry = telemetry
                self.command = command
                self.start_time: float | None = None

            def __enter__(self) -> CommandTracker:
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[override]
                if not self.telemetry.enabled:
                    return
                try:
                    duration = 0.0
                    if self.start_time is not None:
                        duration = time.time() - self.start_time
                    # Treat Click's Exit(code=0) as success
                    success = exc_type is None
                    err_name = None
                    try:
                        import click as _click  # local import

                        if exc_type is _click.exceptions.Exit and hasattr(exc_val, "exit_code"):
                            code = getattr(exc_val, "exit_code", 1)
                            success = (code == 0)
                            err_name = None if success else "Exit"
                        else:
                            err_name = exc_type.__name__ if exc_type else None
                    except Exception:
                        err_name = exc_type.__name__ if exc_type else None

                    metric = CommandMetric(
                        command=self.command,
                        duration=duration,
                        success=bool(success),
                        error_type=err_name,
                    )
                    # Local JSONL sink (opt-in)
                    self.telemetry._write_metric_as_json(metric)
                    # Optional Amplitude sink (opt-in via FLOW_AMPLITUDE_API_KEY)
                    try:
                        from flow.utils import analytics as _analytics

                        _analytics.track(
                            "cli_command",
                            {
                                "command": self.command,
                                "success": bool(metric.success),
                                "error_type": metric.error_type or "",
                                "duration_ms": int(metric.duration * 1000),
                                "origin": "cli",
                            },
                        )
                    except Exception:
                        pass
                except Exception:
                    pass

        return CommandTracker(self, command)

    def log_event(self, event: str, properties: dict[str, Any] | None = None) -> None:
        if not self.enabled:
            return
        try:
            payload = asdict(EventMetric(event=event, properties=_safe_dict(properties)))
            self._append_jsonl(payload)
            # Optional Amplitude sink
            try:
                from flow.utils import analytics as _analytics

                _analytics.track(event, _safe_dict(properties))
            except Exception:
                pass
        except Exception:
            pass

    # ---- internal helpers ----
    def _write_metric_as_json(self, metric: CommandMetric) -> None:
        try:
            payload = asdict(metric)
            self._append_jsonl(payload)
        except Exception:
            pass

    def _append_jsonl(self, payload: dict[str, Any]) -> None:
        with self._lock:
            try:
                self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.metrics_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload) + "\n")
            except Exception:
                pass


def _safe_dict(obj: dict[str, Any] | None) -> dict[str, Any]:
    try:
        if not obj:
            return {}
        result: dict[str, Any] = {}
        for k, v in obj.items():
            try:
                json.dumps({k: v})
                result[k] = v
            except Exception:
                result[k] = str(v)
        return result
    except Exception:
        return {}
