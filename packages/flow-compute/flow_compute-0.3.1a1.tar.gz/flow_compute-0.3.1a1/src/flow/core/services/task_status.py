"""Task status service (moved from CLI) for reuse across layers.

Provides task listing, filtering, and JSON shaping logic.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from flow.sdk.contracts import IClient
from flow.sdk.factory import create_client


@dataclass
class StatusQuery:
    task_identifier: str | None = None
    show_all: bool = False
    state: str | None = None
    limit: int = 20
    since: datetime | None = None
    until: datetime | None = None


class TaskStatusService:
    def __init__(self, flow_client: IClient | None = None) -> None:
        self.flow_client = flow_client or create_client(auto_init=True)

    def resolve_single_task(self, identifier: str):
        from flow.cli.utils.task_resolver import resolve_task_identifier

        task, error = resolve_task_identifier(self.flow_client, identifier)
        return task, error

    def list_tasks(self, query: StatusQuery) -> list[Any]:
        from flow.cli.utils.task_fetcher import TaskFetcher
        from flow.sdk.models import TaskStatus

        status_enum = TaskStatus(query.state) if query.state else None
        if status_enum is None and not query.show_all and not (query.since or query.until):
            try:
                return self.flow_client.tasks.list(
                    status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                    limit=min(200, max(1, query.limit)),
                )
            except Exception:
                return []

        fetcher = TaskFetcher(self.flow_client)
        return fetcher.fetch_all_tasks(
            limit=query.limit, prioritize_active=False, status_filter=status_enum
        )

    def filter_by_time(
        self, tasks: Iterable[Any], since: datetime | None, until: datetime | None
    ) -> list[Any]:
        if not since and not until:
            return list(tasks)

        def _normalize(ts: datetime | None) -> datetime | None:
            if ts is None:
                return None
            return ts.replace(tzinfo=timezone.utc) if getattr(ts, "tzinfo", None) is None else ts

        filtered: list[Any] = []
        for t in tasks:
            ts = _normalize(getattr(t, "created_at", None))
            if not ts:
                continue
            if since and ts < since:
                continue
            if until and ts > until:
                continue
            filtered.append(t)
        return filtered

    def to_json_single(self, task: Any) -> dict:
        return {
            "schema_version": "1.0",
            "task": {
                "task_id": getattr(task, "task_id", None),
                "name": getattr(task, "name", None),
                "status": getattr(getattr(task, "status", None), "value", None),
                "instance_type": getattr(task, "instance_type", None),
                "num_instances": getattr(task, "num_instances", 1),
                "region": getattr(task, "region", None),
                "priority": self._derive_priority(task),
                "created_at": (
                    getattr(task, "created_at", None).isoformat()
                    if getattr(task, "created_at", None)
                    else None
                ),
                "started_at": (
                    getattr(task, "started_at", None).isoformat()
                    if getattr(task, "started_at", None)
                    else None
                ),
                "completed_at": (
                    getattr(task, "completed_at", None).isoformat()
                    if getattr(task, "completed_at", None)
                    else None
                ),
                "ssh_host": getattr(task, "ssh_host", None),
            },
        }

    def to_json_list(self, tasks: Iterable[Any]) -> dict:
        items: list[dict] = []
        for task in tasks:
            items.append(
                {
                    "task_id": getattr(task, "task_id", None),
                    "name": getattr(task, "name", None),
                    "status": getattr(getattr(task, "status", None), "value", None),
                    "instance_type": getattr(task, "instance_type", None),
                    "num_instances": getattr(task, "num_instances", 1),
                    "region": getattr(task, "region", None),
                    "priority": self._derive_priority(task),
                    "created_at": (
                        getattr(task, "created_at", None).isoformat()
                        if getattr(task, "created_at", None)
                        else None
                    ),
                    "started_at": (
                        getattr(task, "started_at", None).isoformat()
                        if getattr(task, "started_at", None)
                        else None
                    ),
                    "completed_at": (
                        getattr(task, "completed_at", None).isoformat()
                        if getattr(task, "completed_at", None)
                        else None
                    ),
                }
            )
        return {"schema_version": "1.0", "tasks": items}

    def _derive_priority(self, task: Any) -> str | None:
        try:
            cfg = getattr(task, "config", None)
            prio = getattr(cfg, "priority", None) if cfg is not None else None
            if prio:
                return str(prio)

            meta = getattr(task, "provider_metadata", {}) or {}
            limit_price_str = meta.get("limit_price")
            instance_type = getattr(task, "instance_type", None)
            if isinstance(limit_price_str, str) and instance_type:
                try:
                    from flow.cli.utils.parsing import extract_gpu_info, parse_price
                    from flow.resources import get_gpu_pricing as get_pricing_data

                    price_val = parse_price(limit_price_str)
                    gpu_type, gpu_count = extract_gpu_info(instance_type)
                    pricing = get_pricing_data().get("gpu_pricing", {})
                    table = pricing.get(gpu_type, pricing.get("default", {}))
                    med_per_gpu = table.get("med", 4.0)
                    med_total = med_per_gpu * max(1, gpu_count)
                    if price_val <= med_total * 0.75:
                        return "low"
                    if price_val >= med_total * 1.5:
                        return "high"
                    return "med"
                except Exception:
                    pass
            return "med"
        except Exception:
            return "med"
