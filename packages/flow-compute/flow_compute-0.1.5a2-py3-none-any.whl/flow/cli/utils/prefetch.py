"""Background prefetch and in-memory cache used by CLI commands.

Prefetches likely-needed data after startup to improve responsiveness. Results
are stored in a process-local cache with short TTLs. Some consumers (for
example, `TaskFetcher`) consult this cache to avoid repeated API calls.

Environment variables:
- FLOW_PREFETCH: "0" to disable prefetch
- FLOW_PREFETCH_DEBUG: "1" to enable debug logs
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import logging
import os
import random
import socket
import sys
import threading
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

# Basic metrics for observability (debugging and future CLI surfacing)
_STATS: dict[str, int] = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "inflight_skipped": 0,
}

# Single-flight control for duplicate prefetches
_INFLIGHT: set[str] = set()
_INFLIGHT_LOCK = threading.Lock()


class _PrefetchCache:
    """Thread-safe in-memory cache with per-key TTL.

    Values are stored with a timestamp and a TTL to control staleness.
    The cache is process-local and intentionally simple to avoid IO.
    """

    def __init__(self) -> None:
        self._data: dict[str, tuple[float, float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            ts, ttl, value = entry
            if now - ts > ttl:
                # Expired
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        with self._lock:
            self._data[key] = (time.time(), ttl_seconds, value)

    def age(self, key: str) -> float | None:
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            ts, ttl, _ = entry
            return time.time() - ts


# Global cache instance
_CACHE = _PrefetchCache()


def _maybe_log_debug(message: str) -> None:
    if os.environ.get("FLOW_PREFETCH_DEBUG") == "1":
        _logger.debug(message)


# Context-aware namespacing ----------------------------------------------------


def _context_prefix() -> str:
    """Derive a cache namespace from provider base_url and project.

    Avoids cross-project leaks in long-lived shells and multiple accounts.
    """
    # Memoize per process, but allow explicit reset via reset_context()
    global _CTX_PREFIX
    try:
        prefix = globals().get("_CTX_PREFIX")
        if isinstance(prefix, str) and prefix:
            return prefix
        flow = _build_flow()
        provider = flow.provider  # ensure initialized lazily
        base_url = getattr(getattr(provider, "http", None), "base_url", "unknown")
        project = None
        try:
            project = (flow.config.provider_config or {}).get("project")
        except Exception:
            project = None
        prefix = f"{base_url}|{project or '-'}"
        globals()["_CTX_PREFIX"] = prefix
        return prefix
    except Exception:
        # Do not memoize unknown; retry later when config becomes available
        return "unknown|-"


def reset_context() -> None:
    """Reset the cached context prefix and clear current-context cache.

    Call this when the provider base URL or project changes during a long-lived
    process. It clears the in-memory cache for the old namespace and forces the
    next access to compute a fresh namespace derived from the current config.
    """
    try:
        # Snapshot known keys to clear for the current (old) context
        keys_to_clear = [
            "tasks_running",
            "tasks_pending",
            "tasks_all",
            "instance_catalog",
            "volumes_list",
            "ssh_keys",
            "projects",
            "me",
            "reservations",
        ]
        invalidate_cache_for_current_context(keys_to_clear)
    except Exception:
        pass
    # Drop memoized prefix so next call recomputes
    try:
        globals().pop("_CTX_PREFIX", None)
    except Exception:
        pass


def _ns(key: str) -> str:
    return f"{_context_prefix()}::{key}"


# Disk snapshot cache ---------------------------------------------------------


def _context_hash() -> str:
    try:
        prefix = _context_prefix()
        return hashlib.sha256(prefix.encode("utf-8")).hexdigest()[:16]
    except Exception:
        return "unknown"


def _cache_dir() -> Path:
    base = Path.home() / ".flow" / "cache"
    ctx_dir = base / _context_hash()
    try:
        ctx_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return ctx_dir


def _snapshot_path(key: str) -> Path:
    safe_key = key.replace("/", "_")
    return _cache_dir() / f"{safe_key}.json"


def _save_snapshot(key: str, value: Any) -> None:
    try:
        payload = {"ts": time.time(), "data": value}
        path = _snapshot_path(key)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, default=_json_default))
        tmp.replace(path)
    except Exception:
        pass


def _load_snapshot(key: str) -> tuple[Any, float] | None:
    try:
        path = _snapshot_path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text())
        ts = float(payload.get("ts", 0.0))
        return payload.get("data"), max(0.0, time.time() - ts)
    except Exception:
        return None


def _json_default(obj: Any) -> Any:
    # Best-effort serialization for pydantic models
    try:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
    except Exception:
        pass
    return str(obj)


def get_cached(key: str) -> Any | None:
    """Public accessor for cached prefetch results.

    Keys used by this module:
    - tasks_running: list[Task]
    - tasks_pending: list[Task]
    - tasks_all: list[Task]
    - instance_catalog: list[dict]
    - volumes_list: list[Volume]
    - ssh_keys: list[dict]
    - projects: list[dict]
    - me: dict
    """

    value = _CACHE.get(_ns(key))
    if value is None:
        _STATS["misses"] += 1
    else:
        _STATS["hits"] += 1
    return value


def get_age(key: str) -> float | None:
    """Get age (seconds) of a cached key in current context, or None if absent."""
    return _CACHE.age(_ns(key))


def invalidate_cache_for_current_context(keys: Iterable[str]) -> None:
    """Invalidate keys for the current context namespace."""
    try:
        with _CACHE._lock:
            for k in keys:
                _CACHE._data.pop(_ns(k), None)
    except Exception:
        pass


def invalidate_snapshots(keys: Iterable[str]) -> None:
    """Remove on-disk snapshots for the given cache keys in this context.

    This prevents a subsequent CLI invocation from rehydrating stale task lists
    from disk (e.g., right after a cancellation), ensuring the next command
    performs a live fetch instead of showing outdated results.
    """
    try:
        for k in keys:
            try:
                path = _snapshot_path(k)
                if path.exists():
                    path.unlink(missing_ok=True)  # type: ignore[arg-type]
            except Exception:
                # Best-effort cleanup; ignore any filesystem errors
                continue
    except Exception:
        pass


def _should_enable() -> bool:
    # Default enabled; explicitly disable with FLOW_PREFETCH=0
    return os.environ.get("FLOW_PREFETCH", "1") != "0"


def _with_safety(
    task_name: str, func: Callable[[], Any], ttl_seconds: float, cache_key: str
) -> None:
    """Execute func(), swallow errors, and cache result if available."""
    if not _should_enable():
        return
    ns_key = _ns(cache_key)
    # Single-flight: avoid duplicate concurrent work for the same key
    with _INFLIGHT_LOCK:
        if ns_key in _INFLIGHT:
            _STATS["inflight_skipped"] += 1
            return
        _INFLIGHT.add(ns_key)
    try:
        result = func()
        if result is not None:
            _CACHE.set(ns_key, result, ttl_seconds)
            _STATS["sets"] += 1
            _maybe_log_debug(f"Prefetched {task_name} → {ns_key} (ttl={ttl_seconds}s)")
            # Persist snapshot to disk for cross-invocation warm start
            try:
                # Serialize lists of models safely
                serializable = result
                _save_snapshot(cache_key, serializable)
            except Exception:
                pass
    except Exception as exc:
        # Best-effort: do not impact foreground UX
        _maybe_log_debug(f"Prefetch {task_name} failed: {exc}")
    finally:
        with _INFLIGHT_LOCK:
            _INFLIGHT.discard(ns_key)


def _build_flow():
    # Prefer factory to avoid direct client dependency; retain Flow symbol importability
    # auto_init=False to avoid accidental interactive prompts in background
    from flow.sdk.factory import create_client  # local import to avoid cold-start cost

    return create_client(auto_init=False)


def _prefetch_tasks(status: str | None, limit: int, cache_key: str) -> None:
    from flow.sdk.models import TaskStatus

    def _task_call():
        flow = _build_flow()
        status_enum = TaskStatus(status) if status else None
        return flow.tasks.list(status=status_enum, limit=limit, force_refresh=False)

    # Fresh enough for a short window; conservative TTLs to avoid API pressure
    ttl = 30.0 if status in {"running", "pending"} else 90.0
    _with_safety(
        task_name=f"tasks[{status or 'all'}]",
        func=_task_call,
        ttl_seconds=ttl,
        cache_key=cache_key,
    )


def _prefetch_catalog() -> None:
    def _call():
        flow = _build_flow()
        # Warms Flow's internal 5-min cache
        return flow._load_instance_catalog()

    _with_safety("instance_catalog", _call, ttl_seconds=300.0, cache_key="instance_catalog")


def _prefetch_volumes() -> None:
    def _call():
        flow = _build_flow()
        return flow.volumes.list(limit=200)

    _with_safety("volumes", _call, ttl_seconds=60.0, cache_key="volumes_list")


def _prefetch_ssh_keys() -> None:
    def _call():
        flow = _build_flow()
        return flow.list_ssh_keys()

    _with_safety("ssh_keys", _call, ttl_seconds=300.0, cache_key="ssh_keys")


def _prefetch_projects() -> None:
    def _call():
        flow = _build_flow()
        return flow.list_projects()

    _with_safety("projects", _call, ttl_seconds=300.0, cache_key="projects")


def _prefetch_me() -> None:
    # Reach directly to provider HTTP for a very quick /v2/me
    def _call():
        flow = _build_flow()
        provider = flow.provider  # Ensure provider exists
        api_client = getattr(provider, "_api_client", None)
        if api_client is None:
            return None
        return api_client.get_me()

    _with_safety("me", _call, ttl_seconds=300.0, cache_key="me")


def _prefetch_reservations() -> None:
    def _call():
        flow = _build_flow()
        try:
            return flow.reservations.list()
        except Exception:
            return None

    _with_safety("reservations", _call, ttl_seconds=30.0, cache_key="reservations")


# Convenience refresh helpers --------------------------------------------------


def refresh_tasks_cache_for_status(status: str | None) -> None:
    """Background refresh for task list slice (running, pending, or all)."""
    try:
        if status in {"running", "pending", None}:
            cache_key = (
                "tasks_running"
                if status == "running"
                else "tasks_pending" if status == "pending" else "tasks_all"
            )
            _prefetch_tasks(status, limit=100, cache_key=cache_key)
    except Exception:
        pass


def refresh_active_task_caches() -> None:
    try:
        _prefetch_tasks("running", limit=100, cache_key="tasks_running")
        _prefetch_tasks("pending", limit=100, cache_key="tasks_pending")
    except Exception:
        pass


def refresh_all_tasks_cache() -> None:
    try:
        _prefetch_tasks(None, limit=100, cache_key="tasks_all")
    except Exception:
        pass


def refresh_volumes_cache() -> None:
    try:
        _prefetch_volumes()
    except Exception:
        pass


def get_stats() -> dict[str, int]:
    """Return a snapshot of cache stats for diagnostics."""
    return dict(_STATS)


def prefetch_for_command(argv: list[str] | None = None) -> None:
    """Start background prefetch for a given CLI argv.

    This function is intentionally non-blocking. It returns immediately
    after scheduling background jobs.

    Args:
        argv: Full argv list. Defaults to sys.argv if None.
    """
    if not _should_enable():
        return

    args = argv or sys.argv
    cmd = args[1] if len(args) > 1 and not args[1].startswith("-") else None

    # Nothing to do if no subcommand was provided
    if not cmd:
        return

    # Seed cache from disk snapshot for instant UX where possible
    def _rehydrate(key: str, data: Any) -> Any:
        try:
            # Reconstruct typed models for common keys so downstream code can use attributes
            if key.startswith("tasks_") and isinstance(data, list):
                from flow.sdk.models import Task

                return [Task(**d) if isinstance(d, dict) else d for d in data]
            if key == "volumes_list" and isinstance(data, list):
                from flow.sdk.models import Volume

                return [Volume(**d) if isinstance(d, dict) else d for d in data]
        except Exception:
            return data
        return data

    def _seed_from_snapshot(keys_and_ttls: list[tuple[str, float]]):
        for key, ttl in keys_and_ttls:
            try:
                loaded = _load_snapshot(key)
                if not loaded:
                    continue
                data, age = loaded
                data = _rehydrate(key, data)
                # Respect TTL: if snapshot older than TTL, don't seed
                if age < ttl:
                    _CACHE.set(_ns(key), data, max(1.0, ttl - age))
            except Exception:
                continue

    # Daemon integration: best-effort hint to background agent
    def _daemon_refresh(which: str) -> None:
        try:
            sock_path = Path.home() / ".flow" / "flowd.sock"
            if not sock_path.exists():
                return
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(str(sock_path))
            s.sendall((json.dumps({"cmd": "refresh", "which": which}) + "\n").encode("utf-8"))
            # Fire-and-forget; don't wait for response
            s.close()
        except Exception:
            pass

    # Plan prefetch tasks based on command
    jobs: list[Callable[[], None]] = []

    # Universal small win: auth/profile and active tasks snapshot
    jobs.append(lambda: _prefetch_me())

    # Commands → Prefetch plan
    if cmd in {"status", "logs", "ssh", "cancel", "delete", "ports"}:
        # Likely to inspect active tasks next
        jobs.append(lambda: _prefetch_tasks("running", limit=100, cache_key="tasks_running"))
        jobs.append(lambda: _prefetch_tasks("pending", limit=100, cache_key="tasks_pending"))
        # Do not eagerly prefetch the general slice; fetch on demand when needed
        _seed_from_snapshot([("tasks_running", 30.0), ("tasks_pending", 30.0)])
        _daemon_refresh("active")
    if cmd in {"run", "grab", "dev"}:
        jobs.append(_prefetch_catalog)
        jobs.append(_prefetch_ssh_keys)
        _seed_from_snapshot([("instance_catalog", 300.0), ("ssh_keys", 300.0)])
        _daemon_refresh("all")
    if cmd in {"init", "tutorial", "ssh-keys"}:
        jobs.append(_prefetch_projects)
        jobs.append(_prefetch_ssh_keys)
        _seed_from_snapshot([("projects", 300.0), ("ssh_keys", 300.0)])
        _daemon_refresh("all")
    if cmd in {"reservations"}:
        jobs.append(_prefetch_reservations)
        _seed_from_snapshot([("reservations", 30.0)])
        _daemon_refresh("all")
    if cmd in {"volumes", "mount"}:
        jobs.append(_prefetch_volumes)
        # For mount flows, warm active task slices to make the task selector instant
        if cmd == "mount":
            jobs.append(lambda: _prefetch_tasks("running", limit=100, cache_key="tasks_running"))
            jobs.append(lambda: _prefetch_tasks("pending", limit=100, cache_key="tasks_pending"))
            _seed_from_snapshot(
                [("volumes_list", 60.0), ("tasks_running", 30.0), ("tasks_pending", 30.0)]
            )
        else:
            _seed_from_snapshot([("volumes_list", 60.0)])
        _daemon_refresh("all")

    # Opportunistic: if user passed a task id in argv, we could prefetch its logs.
    # Keep this extremely conservative to avoid surprises.
    # (We skip here to remain minimal and surgical.)

    # Execute in a very small thread pool to keep resource usage low
    def _run_background(jobs_to_run: list[Callable[[], None]]) -> None:
        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(3, len(jobs_to_run) or 1)
            ) as ex:
                futures = [ex.submit(job) for job in jobs_to_run]
                # Do not block; arrange callbacks to observe errors only in debug mode
                for f in futures:
                    f.add_done_callback(
                        lambda fut: _maybe_log_debug(
                            f"Prefetch job done, error={fut.exception()}"
                            if fut.exception()
                            else "Prefetch job done"
                        )
                    )
        except Exception as exc:
            _maybe_log_debug(f"Prefetch scheduling failed: {exc}")

    # Fire and forget in a single short-lived thread
    t = threading.Thread(target=_run_background, args=(jobs,), daemon=True)
    t.start()

    # Periodic refresh is disabled by default; enable via FLOW_PREFETCH_PERIODIC=1
    try:

        def _start_periodic(cmd_name: str | None) -> None:
            if not cmd_name or os.environ.get("FLOW_PREFETCH_PERIODIC", "0") != "1":
                return
            if cmd_name not in {"status"}:
                return

            # Conservative intervals with jitter
            try:
                active_ivl = float(os.environ.get("FLOW_PREFETCH_ACTIVE_INTERVAL", "30.0"))
            except Exception:
                active_ivl = 30.0
            try:
                all_ivl = float(os.environ.get("FLOW_PREFETCH_ALL_INTERVAL", "90.0"))
            except Exception:
                all_ivl = 90.0
            try:
                jitter_pct = float(os.environ.get("FLOW_PREFETCH_JITTER", "0.2"))
            except Exception:
                jitter_pct = 0.2

            def _jittered(ivl: float) -> float:
                if ivl <= 0:
                    return 0
                return ivl * (1.0 + random.uniform(-jitter_pct, jitter_pct))

            def _loop() -> None:
                next_run_running = time.time()
                next_run_pending = time.time()
                next_run_all = time.time()
                while _should_enable() and os.environ.get("FLOW_PREFETCH_PERIODIC", "0") == "1":
                    now = time.time()
                    try:
                        if now >= next_run_running:
                            _prefetch_tasks("running", limit=100, cache_key="tasks_running")
                            next_run_running = now + _jittered(active_ivl)
                        if now >= next_run_pending:
                            _prefetch_tasks("pending", limit=100, cache_key="tasks_pending")
                            next_run_pending = now + _jittered(active_ivl)
                        if all_ivl > 0 and now >= next_run_all:
                            _prefetch_tasks(None, limit=100, cache_key="tasks_all")
                            next_run_all = now + _jittered(all_ivl)
                    except Exception as exc:
                        _maybe_log_debug(f"Periodic prefetch error: {exc}")
                    time.sleep(0.5)

            threading.Thread(target=_loop, daemon=True).start()

        _start_periodic(cmd)
    except Exception as exc:
        _maybe_log_debug(f"Failed to start periodic prefetch: {exc}")


# Convenience alias used by consumers
start_prefetch_for_command = prefetch_for_command
