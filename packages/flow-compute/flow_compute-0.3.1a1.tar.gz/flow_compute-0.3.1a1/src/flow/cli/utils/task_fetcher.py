"""Centralized task fetching for the CLI.

Provides efficient fetching that prioritizes active tasks and handles large
lists gracefully, including pagination edge cases.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    # Optional cache import; fallback to no-ops if unavailable
    from flow.cli.utils.prefetch import (
        get_age,  # type: ignore
        get_cached,  # type: ignore
        refresh_active_task_caches,  # type: ignore
        refresh_all_tasks_cache,  # type: ignore
    )
except Exception:  # pragma: no cover - optional dependency for CLI path

    def get_cached(_: str):  # type: ignore
        return None

    def get_age(_: str):  # type: ignore
        return None

    def refresh_active_task_caches():  # type: ignore
        return None

    def refresh_all_tasks_cache():  # type: ignore
        return None


from flow.sdk.client import Flow
from flow.sdk.factory import create_client
from flow.sdk.models import Task, TaskStatus


class TaskFetcher:
    """Centralized service for fetching tasks with active task prioritization."""

    def __init__(self, flow_client: Flow | None = None):
        """Initialize with optional Flow client.

        Args:
            flow_client: Optional Flow client instance. Creates one if not provided.
        """
        # Prefer factory to avoid direct client construction in CLI layer
        self.flow_client = flow_client or create_client(auto_init=True)

    def _dbg(self, msg: str) -> None:
        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.fetcher").info(msg)
        except Exception:
            pass

    def fetch_all_tasks(
        self,
        limit: int = 1000,
        prioritize_active: bool = True,
        status_filter: TaskStatus | None = None,
    ) -> list[Task]:
        """Fetch tasks with intelligent prioritization.

        This method handles the common case where active tasks (running/pending)
        might not appear in the default task list due to pagination ordering.
        It explicitly fetches active tasks first, then merges with the general list.

        Args:
            limit: Maximum number of tasks to return
            prioritize_active: Whether to prioritize active tasks in results
            status_filter: Optional status filter for tasks

        Returns:
            List of tasks with active tasks prioritized if requested
        """
        # Detect demo/mock mode to avoid cross-provider duplication
        demo_active = False
        try:
            # Safe import (CLI path); in SDK contexts this may not exist
            from flow.cli.ui.runtime.mode import is_demo_active  # type: ignore

            demo_active = bool(is_demo_active())
        except Exception:
            demo_active = False

        # Fast path: consult prefetch cache when available (skip in demo to avoid duplicates)
        if status_filter:
            cache_key = None
            if status_filter == TaskStatus.RUNNING:
                cache_key = "tasks_running"
            elif status_filter == TaskStatus.PENDING:
                cache_key = "tasks_pending"
            # Use cached slice first if present (still fall back to live if miss)
            if cache_key and not demo_active:
                cached = get_cached(cache_key)
                # Soft SWR: if cache is older than a conservative threshold, refresh in background
                # Soft SWR: if cache is older than a conservative threshold, refresh in background
                try:
                    age = get_age(cache_key) or 0.0
                    if age > 20.0:
                        import threading

                        threading.Thread(target=refresh_active_task_caches, daemon=True).start()
                except Exception:
                    pass
                self._dbg(
                    f"fetch_all(status={getattr(status_filter,'value',status_filter)}): cache_key={cache_key} age={age if 'age' in locals() else 'n/a'} cached_count={len(cached) if cached else 0}"
                )
                if cached:
                    try:
                        cached_sorted = sorted(cached, key=lambda t: t.created_at, reverse=True)
                        return cached_sorted[:limit]
                    except Exception:
                        # Fall back if cached objects are not fully typed yet
                        return list(cached)[:limit]
            # If filtering by specific status, just fetch those
            tasks = self.flow_client.tasks.list(status=status_filter, limit=limit)
            self._dbg(
                f"fetch_all: provider returned {len(tasks) if tasks else 0} for status={getattr(status_filter,'value',status_filter)}"
            )
            return tasks

        tasks_by_id: dict[str, Task] = {}

        if prioritize_active:
            # Check cached active slices first for instant response
            cached_running = [] if demo_active else (get_cached("tasks_running") or [])
            cached_pending = [] if demo_active else (get_cached("tasks_pending") or [])

            # Soft SWR: background refresh if slices are getting stale
            try:
                age_r = get_age("tasks_running") or 0.0
                age_p = get_age("tasks_pending") or 0.0
                if max(age_r, age_p) > 20.0:
                    import threading

                    threading.Thread(target=refresh_active_task_caches, daemon=True).start()
            except Exception:
                pass

            # If caches are cold, wait briefly for prefetch to populate
            if not demo_active and not cached_running and not cached_pending:
                end = time.time() + 0.15
                while time.time() < end:
                    cached_running = get_cached("tasks_running") or []
                    cached_pending = get_cached("tasks_pending") or []
                    if cached_running or cached_pending:
                        break
                    time.sleep(0.05)
            try:
                cached_running = sorted(cached_running, key=lambda t: t.created_at, reverse=True)
                cached_pending = sorted(cached_pending, key=lambda t: t.created_at, reverse=True)
            except Exception:
                # If cache elements are not fully typed, proceed without sorting
                pass
            self._dbg(
                f"fetch_all(active): cached_running={len(cached_running)} cached_pending={len(cached_pending)}"
            )
            for task in list(cached_running)[: min(100, limit)]:
                tasks_by_id[getattr(task, "task_id", getattr(task, "id", ""))] = task
            for task in list(cached_pending)[: min(100, max(0, limit - len(tasks_by_id)))]:
                tasks_by_id[getattr(task, "task_id", getattr(task, "id", ""))] = task

            # Fetch active tasks concurrently to ensure they're included even if cache is stale
            try:
                # Prefer provider-side batching if supported: request both RUNNING and PENDING
                try:
                    batched = self.flow_client.tasks.list(
                        status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                        limit=min(200, max(100, limit)),
                    )
                    self._dbg(
                        f"fetch_all(active): provider batched returned {len(batched) if batched else 0}"
                    )
                    for task in batched:
                        tasks_by_id[task.task_id] = task
                except Exception:
                    # Fallback to parallel individual calls
                    with ThreadPoolExecutor(max_workers=2) as ex:
                        futures = [
                            ex.submit(
                                self.flow_client.tasks.list,
                                status=TaskStatus.RUNNING,
                                limit=min(100, limit),
                            ),
                            ex.submit(
                                self.flow_client.tasks.list,
                                status=TaskStatus.PENDING,
                                limit=min(100, limit),
                            ),
                        ]
                        for f in as_completed(futures, timeout=1.0):
                            try:
                                active_tasks = f.result()
                                for task in active_tasks:
                                    tasks_by_id[task.task_id] = task
                            except Exception:
                                pass
            except Exception:
                pass

        # Fetch general task list
        remaining_limit = limit - len(tasks_by_id)
        if remaining_limit > 0:
            try:
                if demo_active:
                    # In demo/mock mode, avoid merging cache (from other provider instances)
                    general_tasks = self.flow_client.tasks.list(limit=remaining_limit)
                else:
                    # Consult broader cached slice to avoid an immediate API call
                    general_tasks = get_cached("tasks_all") or []
                    # Soft SWR for general list
                    try:
                        age_all = get_age("tasks_all") or 0.0
                        if age_all > 60.0:
                            import threading

                            threading.Thread(target=refresh_all_tasks_cache, daemon=True).start()
                    except Exception:
                        pass
                    if not general_tasks:
                        # Give prefetch a brief moment to complete
                        end = time.time() + 0.15
                        while time.time() < end:
                            general_tasks = get_cached("tasks_all") or []
                            if general_tasks:
                                break
                            time.sleep(0.05)
                    if not general_tasks:
                        general_tasks = self.flow_client.tasks.list(limit=remaining_limit)
                self._dbg(
                    f"fetch_all(general): remaining_limit={remaining_limit} provider_count={len(general_tasks) if general_tasks else 0}"
                )
                for task in general_tasks:
                    tid = getattr(task, "task_id", getattr(task, "id", None))
                    if tid and tid not in tasks_by_id:
                        tasks_by_id[tid] = task
            except Exception as e:
                # If general fetch fails, at least return active tasks
                self._dbg(f"fetch_all(general): error={e}")

        # Return as list, sorted by created_at (newest first)
        all_tasks = list(tasks_by_id.values())

        # Always sort by created_at in descending order (newest first)
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)

        final = all_tasks[:limit]
        self._dbg(f"fetch_all: final_count={len(final)}")
        return final

    def fetch_for_display(
        self, show_all: bool = False, status_filter: str | None = None, limit: int = 100
    ) -> list[Task]:
        """Fetch tasks optimized for display commands (status, list).

        Args:
            show_all: Whether to show all tasks or apply time filtering
            status_filter: Optional status string to filter by
            limit: Maximum number of tasks to return

        Returns:
            List of tasks ready for display
        """
        # Convert status string to enum if provided
        self._dbg(
            f"fetch_for_display: show_all={show_all} status_filter={status_filter} limit={limit}"
        )
        status_enum = TaskStatus(status_filter) if status_filter else None

        if not show_all and not status_filter:
            # Default view: Show only running/pending tasks
            # If none exist, fall back to showing all recent tasks

            # First, try to fetch only active (running/pending) tasks
            active_tasks = []
            tasks_by_id = {}

            # Fast path: consult prefetch cache for running/pending slices
            try:
                cached_running = get_cached("tasks_running") or []
                cached_pending = get_cached("tasks_pending") or []
                # If both caches are empty, wait briefly for prefetch to complete
                if not cached_running and not cached_pending:
                    end = time.time() + 0.15
                    while time.time() < end:
                        cached_running = get_cached("tasks_running") or []
                        cached_pending = get_cached("tasks_pending") or []
                        if cached_running or cached_pending:
                            break
                        time.sleep(0.05)
                # Use cached if any present to avoid immediate network calls
                if cached_running or cached_pending:
                    self._dbg(
                        f"fetch_for_display(active): cached_running={len(cached_running)} cached_pending={len(cached_pending)}"
                    )
                    combined = list(cached_running) + list(cached_pending)
                    # Deduplicate by task_id while preserving order
                    seen: dict[str, Task] = {}
                    for t in combined:
                        tid = getattr(t, "task_id", getattr(t, "id", None))
                        if tid and tid not in seen:
                            seen[tid] = t
                    # Sort newest first if timestamps available; otherwise return as-is
                    try:
                        result = sorted(seen.values(), key=lambda t: t.created_at, reverse=True)
                    except Exception:
                        result = list(seen.values())
                    return result[:limit]
            except Exception:
                # Ignore cache errors and proceed with live fetch
                pass

            # Prefer provider-side batching for RUNNING and PENDING
            try:
                batched_active = self.flow_client.tasks.list(
                    status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                    limit=min(200, max(100, limit)),
                )
                self._dbg(
                    f"fetch_for_display(active): provider batched returned {len(batched_active) if batched_active else 0}"
                )
                for task in batched_active:
                    if task.task_id not in tasks_by_id:
                        tasks_by_id[task.task_id] = task
                        active_tasks.append(task)
            except Exception as e:
                # Fallback: fetch RUNNING and PENDING concurrently
                try:
                    with ThreadPoolExecutor(max_workers=2) as ex:
                        futures = [
                            ex.submit(
                                self.flow_client.tasks.list,
                                status=TaskStatus.RUNNING,
                                limit=min(100, limit),
                            ),
                            ex.submit(
                                self.flow_client.tasks.list,
                                status=TaskStatus.PENDING,
                                limit=min(100, limit),
                            ),
                        ]
                        for f in as_completed(futures, timeout=1.5):
                            try:
                                status_tasks = f.result()
                                for task in status_tasks:
                                    if task.task_id not in tasks_by_id:
                                        tasks_by_id[task.task_id] = task
                                        active_tasks.append(task)
                            except Exception:
                                pass
                except Exception:
                    pass
                self._dbg(f"fetch_for_display(active): batched error={e}")

            # If we found active tasks, return only those
            if active_tasks:
                # Sort by created_at (newest first)
                active_tasks.sort(key=lambda t: t.created_at, reverse=True)
                return active_tasks[:limit]

            # No active tasks found - perform a single provider call and return empty if also empty
            try:
                general = self.flow_client.tasks.list(limit=limit)
                self._dbg(
                    f"fetch_for_display(general): provider_count={len(general) if general else 0}"
                )
                if not general:
                    return []
                # Else, sort and return most recent general list
                general = sorted(general, key=lambda t: getattr(t, "created_at", 0), reverse=True)
                return general[:limit]
            except Exception as e:
                # Fallback to prior behavior
                self._dbg(f"fetch_for_display(general): error={e}")
                return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
        else:
            # Specific status filter or --all flag
            return self.fetch_all_tasks(
                limit=limit, prioritize_active=False, status_filter=status_enum
            )

    def fetch_for_resolution(self, limit: int = 1000) -> list[Task]:
        """Fetch tasks optimized for name/ID resolution (cancel, ssh, logs).

        This method prioritizes active tasks since those are most likely
        to be the target of user actions.

        Args:
            limit: Maximum number of tasks to fetch

        Returns:
            List of tasks with active tasks prioritized
        """
        return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
