"""Minimal async analytics sink (Amplitude-compatible).

This module centralizes optional remote analytics delivery for the CLI and
adapters without creating layering violations. It is intentionally tiny,
best-effort, and completely optional:

- Enabled only when FLOW_TELEMETRY=1 and FLOW_AMPLITUDE_API_KEY is set
- Sends non-blocking, batched events to Amplitude's HTTP API
- Never raises or logs noisy errors; silently drops on failures
- Uses a stable, anonymous device_id stored under ~/.flow/analytics_id

Environment variables:
- FLOW_TELEMETRY: set to "1" to enable local+remote telemetry
- FLOW_AMPLITUDE_API_KEY: Amplitude project API key to enable remote delivery
- FLOW_AMPLITUDE_URL: override ingestion URL (default: https://api2.amplitude.com/2/httpapi)
"""

from __future__ import annotations

import atexit
import json
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

try:  # requests is already a dependency in this project
    import requests  # type: ignore
except Exception:  # pragma: no cover - extremely defensive
    requests = None  # type: ignore


DEFAULT_INGEST_URL: Final[str] = "https://api2.amplitude.com/2/httpapi"


def _get_flow_version() -> str:
    try:
        from flow._version import get_version  # local import to avoid early import cost

        return get_version()
    except Exception:
        return "0.0.0+unknown"


def _bool_env(name: str) -> bool:
    try:
        v = os.environ.get(name, "").strip().lower()
        return v in {"1", "true", "yes", "on"}
    except Exception:
        return False


def _get_device_id() -> str:
    """Return a stable, anonymous device id (persisted locally)."""
    try:
        path = Path.home() / ".flow" / "analytics_id"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = path.read_text(encoding="utf-8").strip()
            if data:
                return data
        # Generate and persist a new UUIDv4 string
        import uuid

        new_id = str(uuid.uuid4())
        path.write_text(new_id, encoding="utf-8")
        return new_id
    except Exception:
        # Worst case, return a volatile identifier for this process
        return f"ephemeral-{int(time.time())}"


@dataclass
class AnalyticsEvent:
    event_type: str
    event_properties: dict[str, Any]
    time_ms: int | None = None


class _AmplitudeWorker:
    """Background worker that batches and ships events to Amplitude."""

    def __init__(self) -> None:
        self._enabled = os.environ.get("FLOW_AMPLITUDE_API_KEY", "").strip() != ""
        self._also_enabled_by_telemetry = os.environ.get("FLOW_TELEMETRY", "0") == "1"
        self._queue: "queue.Queue[AnalyticsEvent]" = queue.Queue(maxsize=1024)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._device_id = _get_device_id()
        self._app_version = _get_flow_version()

    def enabled(self) -> bool:
        return bool(self._enabled and self._also_enabled_by_telemetry and requests is not None)

    def start(self) -> None:
        if not self.enabled() or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="flow-amplitude", daemon=True)
        self._thread.start()
        atexit.register(self.flush)

    def enqueue(self, event: AnalyticsEvent) -> None:
        if not self.enabled():
            return
        try:
            self._queue.put_nowait(event)
        except Exception:
            # Drop if the queue is full or closed
            pass

    def flush(self) -> None:
        if not self.enabled():
            return
        # Allow up to ~1s to drain
        deadline = time.time() + 1.0
        while not self._queue.empty() and time.time() < deadline:
            time.sleep(0.02)

    # --- internal ---
    def _run(self) -> None:
        url = os.environ.get("FLOW_AMPLITUDE_URL", DEFAULT_INGEST_URL).strip() or DEFAULT_INGEST_URL
        api_key = os.environ.get("FLOW_AMPLITUDE_API_KEY", "").strip()
        session = None
        try:
            if requests is not None:
                session = requests.Session()
        except Exception:
            session = None

        batch: list[dict[str, Any]] = []
        last_send = time.time()
        while not self._stop.is_set():
            # Batch up to N events or every T seconds
            try:
                ev = self._queue.get(timeout=0.25)
                batch.append(self._to_amplitude(ev))
            except Exception:
                pass

            now = time.time()
            if batch and (len(batch) >= 20 or (now - last_send) > 1.0):
                try:
                    payload = {"api_key": api_key, "events": batch}
                    # Best-effort; 750ms timeout to avoid any blocking
                    if session is not None:
                        session.post(url, json=payload, timeout=0.75)
                    else:
                        requests.post(url, json=payload, timeout=0.75)  # type: ignore[union-attr]
                except Exception:
                    # Drop on failure; never raise
                    pass
                batch = []
                last_send = now

        # Drain remaining events on stop
        if batch:
            try:
                payload = {"api_key": api_key, "events": batch}
                if session is not None:
                    session.post(url, json=payload, timeout=0.5)
                else:
                    requests.post(url, json=payload, timeout=0.5)  # type: ignore[union-attr]
            except Exception:
                pass

    def _to_amplitude(self, ev: AnalyticsEvent) -> dict[str, Any]:
        t_ms = ev.time_ms if isinstance(ev.time_ms, int) else int(time.time() * 1000)
        # Minimal, privacy-conscious envelope
        out = {
            "event_type": ev.event_type,
            "time": t_ms,
            "device_id": self._device_id,
            "event_properties": ev.event_properties,
            "app_version": self._app_version,
            "platform": "python",
        }
        # Add a small amount of contextual metadata safely
        try:
            import platform
            import sys

            out["os_name"] = platform.system()
            out["os_version"] = platform.version()[:64]
            out["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        except Exception:
            pass
        return out


_worker = _AmplitudeWorker()


def start() -> None:
    """Start the background worker (no-op if already started/disabled)."""
    try:
        _worker.start()
    except Exception:
        pass


def track(event_type: str, properties: dict[str, Any] | None = None, *, time_ms: int | None = None) -> None:
    """Enqueue an analytics event for async delivery.

    Does nothing unless both FLOW_TELEMETRY=1 and FLOW_AMPLITUDE_API_KEY are set.
    """
    try:
        if not _worker.enabled():
            return
        start()
        _worker.enqueue(
            AnalyticsEvent(event_type=event_type, event_properties=properties or {}, time_ms=time_ms)
        )
    except Exception:
        pass

