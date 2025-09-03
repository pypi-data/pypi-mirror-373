"""Lightweight local background agent for Flow CLI.

This daemon maintains warm caches and disk snapshots to make CLI commands
feel instant across invocations. It exposes a tiny JSON-over-UNIX-socket
RPC for basic control and diagnostics.

Focus: minimal dependencies, robust error handling, small footprint.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any
from concurrent.futures import ThreadPoolExecutor
import secrets
import logging
from collections import deque

SOCKET_PATH = Path.home() / ".flow" / "flowd.sock"
PID_PATH = Path.home() / ".flow" / "flowd.pid"
TOKEN_PATH = Path.home() / ".flow" / "flowd.token"

_logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple sliding-window rate limiter per client id.

    Configured via env:
      - FLOW_DAEMON_MAX_REQUESTS (default: 100)
      - FLOW_DAEMON_WINDOW_SECONDS (default: 60)
    """

    def __init__(self) -> None:
        try:
            self.max_requests = max(1, int(os.environ.get("FLOW_DAEMON_MAX_REQUESTS", "100")))
        except Exception:
            self.max_requests = 100
        try:
            self.window_seconds = max(1, int(os.environ.get("FLOW_DAEMON_WINDOW_SECONDS", "60")))
        except Exception:
            self.window_seconds = 60
        self.requests: deque[tuple[float, str]] = deque()
        self._lock = threading.Lock()

    def allow(self, client_id: str) -> bool:
        now = time.time()
        with self._lock:
            # Drop old entries
            cutoff = now - self.window_seconds
            while self.requests and self.requests[0][0] < cutoff:
                self.requests.popleft()
            # Count client requests
            cnt = 0
            for _, cid in self.requests:
                if cid == client_id:
                    cnt += 1
            if cnt >= self.max_requests:
                return False
            self.requests.append((now, client_id))
            return True


def _ensure_runtime_dir() -> None:
    try:
        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _send_json(conn: socket.socket, payload: dict[str, Any]) -> None:
    try:
        data = (json.dumps(payload) + "\n").encode("utf-8")
        conn.sendall(data)
    except Exception:
        pass


def _recv_json(conn: socket.socket) -> dict[str, Any] | None:
    try:
        buf = b""
        # Read until newline (one JSON per connection)
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
        if not buf:
            return None
        line = buf.split(b"\n", 1)[0].decode("utf-8", errors="ignore")
        return json.loads(line)
    except Exception:
        return None


def _prefetch_tick(active_only: bool = True) -> None:
    """Perform one refresh tick using CLI prefetch helpers."""
    try:
        from flow.cli.utils.prefetch import (
            _prefetch_catalog,
            _prefetch_projects,
            _prefetch_ssh_keys,
            _prefetch_volumes,
            refresh_active_task_caches,
            refresh_all_tasks_cache,
        )

        # Active tasks are the highest value for responsiveness
        refresh_active_task_caches()
        # Opportunistically refresh others in longer cadence
        if not active_only:
            refresh_all_tasks_cache()
            _prefetch_catalog()
            _prefetch_ssh_keys()
            _prefetch_projects()
            _prefetch_volumes()
    except Exception:
        # Daemon must be silent on transient errors
        pass


class DaemonState:
    def __init__(self) -> None:
        self.start_time = time.time()
        self.last_refresh_active = 0.0
        self.last_refresh_all = 0.0
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.connections_handled = 0
        self.token: str = ""
        self.rate_limiter = RateLimiter()

    def to_dict(self) -> dict[str, Any]:
        with self.lock:
            return {
                "uptime": time.time() - self.start_time,
                "last_refresh_active": self.last_refresh_active,
                "last_refresh_all": self.last_refresh_all,
                "connections_handled": self.connections_handled,
                "pid": os.getpid(),
            }


def _refresh_loop(state: DaemonState) -> None:
    # Active refresh every ~30s, all refresh every ~90s with jitter
    def _jitter(base: float) -> float:
        try:
            import random

            return base * (1.0 + random.uniform(-0.2, 0.2))
        except Exception:
            return base

    next_active = time.time()
    next_all = time.time()
    while not state.shutdown_event.is_set():
        now = time.time()
        try:
            if now >= next_active:
                _prefetch_tick(active_only=True)
                with state.lock:
                    state.last_refresh_active = time.time()
                next_active = now + _jitter(30.0)
            if now >= next_all:
                _prefetch_tick(active_only=False)
                with state.lock:
                    state.last_refresh_all = time.time()
                next_all = now + _jitter(90.0)
        except Exception:
            pass
        time.sleep(0.5)


def _handle_connection(conn: socket.socket, state: DaemonState) -> None:
    try:
        req = _recv_json(conn) or {}
        # Simple token auth to ensure only local CLI can control the daemon
        token = req.get("token")
        if not token or token != state.token:
            _send_json(conn, {"ok": False, "error": "unauthorized"})
            return
        # Rate limit per token
        if not state.rate_limiter.allow(client_id=token):
            _send_json(conn, {"ok": False, "error": "rate_limited"})
            return
        cmd = req.get("cmd")
        if cmd == "ping":
            _send_json(conn, {"ok": True, "pong": True})
        elif cmd == "status":
            _send_json(conn, {"ok": True, "status": state.to_dict()})
        elif cmd == "refresh":
            which = req.get("which", "active")
            if which == "all":
                _prefetch_tick(active_only=False)
            else:
                _prefetch_tick(active_only=True)
            _send_json(conn, {"ok": True})
        elif cmd == "shutdown":
            state.shutdown_event.set()
            _send_json(conn, {"ok": True})
        elif cmd == "version":
            try:
                from flow._version import get_version

                v = get_version()
            except Exception:
                v = "unknown"
            _send_json(conn, {"ok": True, "version": v})
        else:
            _send_json(conn, {"ok": False, "error": "unknown command"})
    except Exception as e:
        # Log once per error occurrence without crashing the daemon
        try:
            _logger.debug(f"daemon handle_connection error: {e}")
        except Exception:
            pass
    finally:
        with state.lock:
            state.connections_handled += 1
        try:
            conn.close()
        except Exception:
            pass


def run_server() -> int:
    _ensure_runtime_dir()
    # Clean up stale socket
    try:
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()
    except Exception:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET_PATH))
    os.chmod(str(SOCKET_PATH), 0o600)
    server.listen(16)

    # Write PID file
    try:
        PID_PATH.write_text(str(os.getpid()))
    except Exception:
        pass

    state = DaemonState()
    # Create or load token for simple auth
    try:
        token = None
        if TOKEN_PATH.exists():
            try:
                token = TOKEN_PATH.read_text().strip()
            except Exception:
                token = None
        if not token:
            token = secrets.token_urlsafe(32)
            # Write with restricted permissions
            try:
                TOKEN_PATH.write_text(token)
                TOKEN_PATH.chmod(0o600)
            except Exception:
                pass
        state.token = token or ""
    except Exception:
        state.token = ""
    # Start background refresh loop
    t = threading.Thread(target=_refresh_loop, args=(state,), daemon=True)
    t.start()

    # Idle shutdown after TTL if no connections and no refresh demanded externally
    idle_ttl = float(os.environ.get("FLOW_DAEMON_IDLE_TTL", "1800"))  # 30 minutes default
    last_activity = time.time()

    max_workers = 8
    try:
        max_workers = max(2, int(os.environ.get("FLOW_DAEMON_WORKERS", "8")))
    except Exception:
        max_workers = 8
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="flowd")

    try:
        while not state.shutdown_event.is_set():
            server.settimeout(1.0)
            try:
                conn, _ = server.accept()
                last_activity = time.time()
            except TimeoutError:
                # Idle shutdown
                if (time.time() - last_activity) > idle_ttl:
                    break
                continue
            except Exception:
                continue

            # Handle request in thread (short, one-shot)
            try:
                executor.submit(_handle_connection, conn, state)
            except Exception:
                # Fallback to direct handling on executor failure
                try:
                    _handle_connection(conn, state)
                except Exception:
                    pass
    finally:
        try:
            server.close()
        except Exception:
            pass
        try:
            if SOCKET_PATH.exists():
                SOCKET_PATH.unlink()
        except Exception:
            pass
        try:
            if PID_PATH.exists():
                PID_PATH.unlink()
        except Exception:
            pass
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass

    return 0


def main() -> int:
    # Minimal shim to allow -m execution
    return run_server()


if __name__ == "__main__":
    sys.exit(main())
