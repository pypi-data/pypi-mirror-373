"""Mock provider for demo/dry-run mode.

Implements IProvider semantics entirely in-memory to simulate task lifecycle
without provisioning any real resources. Suitable for demos, tutorials, and
offline exploration. Activated by setting FLOW_PROVIDER=mock or --demo.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from flow.adapters.providers.base import ProviderCapabilities
from flow.adapters.providers.registry import ProviderRegistry
from flow.application.config.config import Config
from flow.errors import FlowError, TaskNotFoundError
from flow.protocols.provider import ProviderProtocol as IProvider
from flow.sdk.models import (
    AvailableInstance,
    Instance,
    InstanceStatus,
    Task,
    TaskConfig,
    TaskStatus,
    User,
    Volume,
)


@dataclass
class _MockTaskState:
    task: Task
    logs: list[str]
    created_at: datetime
    lock: threading.Lock


class MockProvider(IProvider):
    """In-memory fake provider with predictable, fast behavior."""

    def __init__(self, config: Config):
        self.config = config
        self._tasks: dict[str, _MockTaskState] = {}
        self._volumes: dict[str, Volume] = {}
        # Load persistent state if present; otherwise seed initial demo data
        if not self._load_state():
            try:
                self._seed_demo_tasks()
                # Normalize demo state to avoid stale active tasks on first run
                self._cleanup_stale_active_tasks()
                self._save_state()
            except Exception:
                pass
        else:
            # If restoring from disk, normalize any stale active tasks
            try:
                self._cleanup_stale_active_tasks()
                self._save_state()
            except Exception:
                pass

    @classmethod
    def from_config(cls, config: Config) -> MockProvider:
        return cls(config)

    # ===== Task APIs =====
    def submit_task(
        self, instance_type: str, config: TaskConfig, volume_ids: list[str] | None = None
    ) -> Task:
        self._apply_latency("submit")
        import os

        task_id = f"mock-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        task = Task(
            task_id=task_id,
            name=config.name,
            status=TaskStatus.PENDING,
            config=config,
            created_at=now,
            instance_type=instance_type or (config.instance_type or "a100"),
            num_instances=getattr(config, "num_instances", 1) or 1,
            region=(config.region or "demo-region-1"),
            cost_per_hour="$8.00",
            created_by=os.environ.get("FLOW_DEMO_OWNER", "you"),
            ssh_host=None,  # Never assigns a real host
            ssh_port=22,
            ssh_user="ubuntu",
        )
        # Mark origin and provisioning state for UX
        try:
            from flow.cli.utils.origin import detect_origin as _detect_origin

            origin = _detect_origin()
        except Exception:
            origin = "flow-compute"
        task.provider_metadata = {
            "origin": origin,
            "instance_status": "STATUS_STARTING",
        }
        # Create stable instance IDs and attach to task
        try:
            task.instances = [f"inst-{task_id}-{i}" for i in range(task.num_instances or 1)]
        except Exception:
            task.instances = [f"inst-{task_id}-0"]
        state = _MockTaskState(task=task, logs=[], created_at=now, lock=threading.Lock())
        self._tasks[task_id] = state

        # Simulate quick lifecycle transitions in background
        threading.Thread(target=self._simulate_task_lifecycle, args=(task_id,), daemon=True).start()
        # Persist
        self._save_state()
        return task

    # Simulate lifecycle transitions
    def _simulate_task_lifecycle(self, task_id: str) -> None:
        self._apply_latency("lifecycle")
        state = self._tasks.get(task_id)
        if not state:
            return
        # PENDING -> RUNNING -> COMPLETED
        time.sleep(0.3)
        with state.lock:
            state.task.status = TaskStatus.RUNNING
            state.task.started_at = datetime.now(timezone.utc)
            state.logs.append("[mock] task started")
            # Update instance_status to reflect running
            try:
                meta = state.task.provider_metadata or {}
                meta["instance_status"] = "STATUS_RUNNING"
                state.task.provider_metadata = meta
            except Exception:
                pass
            # Assign a deterministic demo IP and shell command to indicate SSH readiness
            try:
                demo_ip = self._generate_demo_ip(state.task)
                state.task.ssh_host = demo_ip
                state.task.shell_command = f"ssh ubuntu@{demo_ip}"
            except Exception:
                pass
        # Persist transition so restarts don't revert to PENDING
        try:
            self._save_state()
        except Exception:
            pass
        # Generate a few log lines
        for i in range(3):
            time.sleep(0.2)
            with state.lock:
                state.logs.append(f"[mock] step {i+1} complete")
        time.sleep(0.2)
        with state.lock:
            state.task.status = TaskStatus.COMPLETED
            state.task.completed_at = datetime.now(timezone.utc)
            state.logs.append("[mock] task completed successfully")
        # Persist terminal state for stability across sessions
        try:
            self._save_state()
        except Exception:
            pass

    def get_task(self, task_id: str) -> Task:
        self._apply_latency("get_task")
        state = self._tasks.get(task_id)
        if not state:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return state.task

    def get_task_status(self, task_id: str) -> TaskStatus:
        self._apply_latency("status")
        return self.get_task(task_id).status

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Task]:  # type: ignore[override]
        self._apply_latency("list")
        tasks = [s.task for s in self._tasks.values()]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        if status:
            if isinstance(status, list):
                allowed = set(status)
                tasks = [t for t in tasks if t.status in allowed]
            else:
                tasks = [t for t in tasks if t.status == status]
        return tasks[:limit]

    def stop_task(self, task_id: str) -> bool:
        self._apply_latency("cancel")
        state = self._tasks.get(task_id)
        if not state:
            return False
        with state.lock:
            if state.task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                return True
            state.task.status = TaskStatus.CANCELLED
            state.task.completed_at = datetime.now(timezone.utc)
            state.logs.append("[mock] task cancelled")
        self._save_state()
        return True

    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        self._apply_latency("logs")
        state = self._tasks.get(task_id)
        if not state:
            raise TaskNotFoundError(f"Task {task_id} not found")
        with state.lock:
            return "\n".join(state.logs[-tail:])

    def stream_task_logs(self, task_id: str, log_type: str = "stdout") -> Iterator[str]:
        state = self._tasks.get(task_id)
        if not state:
            raise TaskNotFoundError(f"Task {task_id} not found")
        idx = 0
        while True:
            with state.lock:
                lines = state.logs[idx:]
                done = state.task.is_terminal
            for line in lines:
                yield line
            idx += len(lines)
            if done:
                break
            time.sleep(0.2)

    # ===== Volumes =====
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume:
        self._apply_latency("volume_create")
        vol_id = f"mock-vol-{uuid.uuid4().hex[:8]}"
        vol = Volume(
            volume_id=vol_id,
            name=name or vol_id,
            size_gb=size_gb,
            region=(region or self.config.provider_config.get("region") or "demo-region-1"),
            interface=interface,  # type: ignore[arg-type]
            created_at=datetime.now(timezone.utc),
        )
        self._volumes[vol_id] = vol
        self._save_state()
        return vol

    def delete_volume(self, volume_id: str) -> bool:
        self._apply_latency("volume_delete")
        ok = self._volumes.pop(volume_id, None) is not None
        if ok:
            self._save_state()
        return ok

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        self._apply_latency("volume_list")
        return list(self._volumes.values())[:limit]

    # ===== Instance discovery =====
    def find_instances(
        self, requirements: dict[str, Any], limit: int = 10
    ) -> list[AvailableInstance]:
        self._apply_latency("instances")
        region = self.config.provider_config.get("region") or "demo-region-1"
        # Provide a small catalog independent of requirements for demo richness
        catalog: list[AvailableInstance] = [
            AvailableInstance(
                allocation_id="alloc-a100",
                instance_type="a100",
                region=region,
                price_per_hour=8.0,
                gpu_type="a100",
                gpu_count=1,
                memory_gb=40,
                available_quantity=50,
                status="available",
            ),
            AvailableInstance(
                allocation_id="alloc-8xa100",
                instance_type="8xa100",
                region=region,
                price_per_hour=64.0,
                gpu_type="a100",
                gpu_count=8,
                memory_gb=40,
                available_quantity=12,
                status="available",
            ),
            AvailableInstance(
                allocation_id="alloc-h100",
                instance_type="h100",
                region=region,
                price_per_hour=24.0,
                gpu_type="h100",
                gpu_count=1,
                memory_gb=80,
                available_quantity=20,
                status="available",
            ),
            AvailableInstance(
                allocation_id="alloc-8xh100",
                instance_type="8xh100",
                region=region,
                price_per_hour=192.0,
                gpu_type="h100",
                gpu_count=8,
                memory_gb=80,
                available_quantity=5,
                status="available",
            ),
        ]
        # Quick filter if user specified instance_type
        itype = (requirements.get("instance_type") or "").lower()
        if itype:
            catalog = [c for c in catalog if c.instance_type.lower() == itype]
        return catalog[: max(1, min(limit, len(catalog)))]

    # Catalog parsing expected by client._load_instance_catalog
    def parse_catalog_instance(self, inst: AvailableInstance) -> dict[str, Any]:
        return {
            "name": inst.instance_type,
            "gpu_type": inst.gpu_type or "a100",
            "gpu_count": inst.gpu_count or 1,
            "price_per_hour": inst.price_per_hour,
            "available": True,
            "gpu": {"model": (inst.gpu_type or "A100").upper(), "memory_gb": inst.memory_gb or 40},
        }

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        # Ensure minimal defaults
        if not config.instance_type and not config.min_gpu_memory_gb:
            config = config.model_copy(update={"instance_type": "a100"})
        return config

    def get_task_instances(self, task_id: str) -> list[Instance]:
        # Provide a single mock instance entry
        self._apply_latency()
        t = self.get_task(task_id)
        instances: list[Instance] = []
        for idx in range(max(1, getattr(t, "num_instances", 1) or 1)):
            instances.append(
                Instance(
                    instance_id=f"inst-{task_id}-{idx}",
                    task_id=task_id,
                    status=(
                        InstanceStatus.RUNNING
                        if t.status == TaskStatus.RUNNING
                        else InstanceStatus.PENDING
                    ),
                    created_at=t.created_at,
                    terminated_at=t.completed_at,
                )
            )
        return instances

    # ===== Unsupported operations in mock mode =====
    def upload_code_to_task(self, *args, **kwargs) -> Any:  # pragma: no cover - simple stub
        # Simulate some delay and a plausible transfer summary
        self._apply_latency("upload")
        time.sleep(0.2)
        return {
            "files_transferred": 27,
            "bytes_transferred": 2_560_000,
            "transfer_rate": "12.3 MB/s",
        }

    def get_remote_operations(self):  # pragma: no cover - not supported in mock
        raise FlowError("Remote operations not supported in mock provider")

    # Provider init interface (minimal stub)
    class _InitIface:
        def get_config_fields(self):
            return []

        def list_projects(self):
            return [{"name": "demo-project", "region": "demo-region-1"}]

        def list_ssh_keys(self, project_id: str | None = None):
            return [{"id": "sshkey_demo", "name": "demo-key"}]

    def get_init_interface(self):
        return self._InitIface()

    # Minimal extras
    def mount_volume(self, volume_id: str, task_id: str, mount_point: str | None = None) -> None:
        # Attach volume to all instances of the task
        self._apply_latency("mount")
        state = self._tasks.get(task_id)
        if not state:
            raise TaskNotFoundError(f"Task {task_id} not found")
        # Ensure volume exists
        vol = self._volumes.get(volume_id)
        if not vol:
            # Allow name-based lookup for convenience
            for v in self._volumes.values():
                if v.name == volume_id:
                    vol = v
                    volume_id = v.volume_id
                    break
        if not vol:
            raise FlowError(f"Volume {volume_id} not found")
        # Initialize instances list if missing
        if not getattr(state.task, "instances", None):
            try:
                state.task.instances = [
                    f"inst-{task_id}-{i}" for i in range(state.task.num_instances or 1)
                ]
            except Exception:
                state.task.instances = [f"inst-{task_id}-0"]
        # Update volume attachments
        attached = set(vol.attached_to or [])
        for inst_id in state.task.instances:
            attached.add(inst_id)
        vol.attached_to = list(attached)
        self._volumes[volume_id] = vol
        self._save_state()
        return None

    def get_user(self, user_id: str) -> User:
        # Return a demo user for UI purposes
        return User(user_id=user_id, username="demo-user", email="demo@example.com")

    # Helpers
    def _apply_latency(self, operation: str | None = None):
        """Apply configurable latency with optional per-operation overrides and jitter.

        Environment variables:
          - FLOW_MOCK_LATENCY_MS: base latency in ms (default 0)
          - FLOW_MOCK_LATENCY_<OP>_MS: per-op override (e.g., SUBMIT, LIST, LOGS)
          - FLOW_MOCK_LATENCY_JITTER_MS: additional random jitter (default 0)
          - FLOW_MOCK_LATENCY_JITTER_PCT: percent jitter of base (e.g., 0.1 for 10%)
        """
        try:
            import os
            import random

            base_ms = int(os.environ.get("FLOW_MOCK_LATENCY_MS", "0") or 0)
            op_ms = None
            if operation:
                key = f"FLOW_MOCK_LATENCY_{operation.upper()}_MS"
                val = os.environ.get(key)
                if val is not None and str(val).strip() != "":
                    try:
                        op_ms = int(val)
                    except ValueError:
                        op_ms = None
            ms = op_ms if op_ms is not None else base_ms

            # Jitter handling: absolute ms or percentage of ms
            jitter_ms_env = os.environ.get("FLOW_MOCK_LATENCY_JITTER_MS")
            jitter_pct_env = os.environ.get("FLOW_MOCK_LATENCY_JITTER_PCT")
            jitter = 0
            try:
                if jitter_ms_env is not None:
                    jitter = int(jitter_ms_env)
                elif jitter_pct_env is not None and ms > 0:
                    pct = float(jitter_pct_env)
                    jitter = int(ms * pct)
            except Exception:
                jitter = 0

            if ms > 0:
                # Uniform jitter in [-jitter, +jitter]
                if jitter > 0:
                    delta = random.randint(-jitter, jitter)
                    ms = max(0, ms + delta)
                time.sleep(ms / 1000.0)
        except Exception:
            pass

    # ---- Persistence helpers ----
    def _state_path(self) -> Path:
        return Path.home() / ".flow" / "demo_state.json"

    def _load_state(self) -> bool:
        """Load tasks/volumes from disk. Returns True if loaded."""
        try:
            path = self._state_path()
            if not path.exists():
                return False
            data = json.loads(path.read_text())
            tasks = data.get("tasks", [])
            volumes = data.get("volumes", [])
            self._tasks.clear()
            self._volumes.clear()
            for t in tasks:
                try:
                    task = Task.model_validate(t)
                    self._tasks[task.task_id] = _MockTaskState(
                        task=task,
                        logs=t.get("_logs", ["[mock] restored"]),
                        created_at=task.created_at,
                        lock=threading.Lock(),
                    )
                except Exception:
                    continue
            for v in volumes:
                try:
                    self._volumes[v["volume_id"]] = Volume.model_validate(v)
                except Exception:
                    continue
            # Normalize stale demo states so old tasks don't appear as "starting" forever
            try:
                now = datetime.now(timezone.utc)
                changed = False
                for s in self._tasks.values():
                    task = s.task
                    created = getattr(task, "created_at", None)
                    age_s = (now - created).total_seconds() if created else 0
                    # Promote long-pending tasks to RUNNING with a demo IP
                    if task.status == TaskStatus.PENDING and age_s > 10:
                        task.status = TaskStatus.RUNNING
                        task.started_at = task.started_at or (task.created_at or now)
                        meta = dict(task.provider_metadata or {})
                        meta["instance_status"] = "STATUS_RUNNING"
                        task.provider_metadata = meta
                        try:
                            demo_ip = self._generate_demo_ip(task)
                            task.ssh_host = task.ssh_host or demo_ip
                            task.shell_command = task.shell_command or f"ssh ubuntu@{demo_ip}"
                        except Exception:
                            pass
                        changed = True
                    # If RUNNING but instance_status suggests starting and it's old, fix it
                    try:
                        inst_status = (task.provider_metadata or {}).get("instance_status")
                    except Exception:
                        inst_status = None
                    if (
                        task.status == TaskStatus.RUNNING
                        and inst_status in {"STATUS_STARTING", "STATUS_INITIALIZING"}
                        and age_s > 15 * 60
                    ):
                        meta = dict(task.provider_metadata or {})
                        meta["instance_status"] = "STATUS_RUNNING"
                        task.provider_metadata = meta
                        changed = True
                if changed:
                    self._save_state()
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _save_state(self) -> None:
        """Persist tasks/volumes to disk (best-effort)."""
        try:
            path = self._state_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            tasks: list[dict] = []
            for s in self._tasks.values():
                d = s.task.model_dump()
                # Include recent logs tail to improve UX after restart
                d["_logs"] = s.logs[-50:]
                tasks.append(d)
            vols = [v.model_dump() for v in self._volumes.values()]
            path.write_text(json.dumps({"tasks": tasks, "volumes": vols}, default=str))
        except Exception:
            pass

    def _generate_demo_ip(self, task: Task) -> str:
        """Generate a deterministic, non-routable demo IP based on task identity."""
        try:
            base = task.name or task.task_id or "task"
            h = int(hashlib.sha256(base.encode("utf-8")).hexdigest()[:6], 16)
            return f"10.{(h >> 16) & 0xFF}.{(h >> 8) & 0xFF}.{h & 0xFF}"
        except Exception:
            return "10.0.0.1"

    def _cleanup_stale_active_tasks(self, max_age_minutes: int = 15) -> None:
        """Mark obviously stale active tasks as completed in demo mode.

        In demo/mock mode tasks are transient. If the process exits before the
        background lifecycle thread persists updates, we can end up with many
        PENDING/RUNNING tasks lingering on disk. This routine normalizes those
        on startup so the CLI doesn't show a flood of duplicate-looking entries.

        Args:
            max_age_minutes: Age threshold after which active tasks are considered stale.
        """
        try:
            now = datetime.now(timezone.utc)
            threshold = timedelta(minutes=max_age_minutes)
            for state in list(self._tasks.values()):
                try:
                    task = state.task
                    created_at = getattr(task, "created_at", None)
                    if not created_at:
                        continue
                    age = now - created_at
                    if age > threshold and task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                        with state.lock:
                            if task.started_at is None and task.status == TaskStatus.RUNNING:
                                task.started_at = task.created_at
                            if task.started_at is None:
                                task.started_at = task.created_at
                            task.status = TaskStatus.COMPLETED
                            task.completed_at = now
                            # Clear transitional instance status to avoid "starting" label
                            try:
                                meta = task.provider_metadata or {}
                                meta["instance_status"] = "STATUS_RUNNING"
                                task.provider_metadata = meta
                            except Exception:
                                pass
                except Exception:
                    continue
        except Exception:
            # Best-effort only; never fail initialization
            pass

    def _seed_demo_tasks(self):
        # Seed Flow (CLI) tasks with diverse GPU types and ages, plus one External cluster
        now = datetime.now(timezone.utc)
        # Flow CLI welcome task (running, created_by you)
        t0 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="cli-welcome",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(seconds=15),
            started_at=now,
            instance_type="a100",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$8.00",
            created_by="you",
            ssh_host=None,
            ssh_port=22,
            ssh_user="ubuntu",
            provider_metadata={
                "origin": "flow-cli",
                "instance_status": "STATUS_STARTING",
                "project": "post-training-team",
            },
        )
        t0.instances = [f"inst-{t0.task_id}-0"]
        self._tasks[t0.task_id] = _MockTaskState(
            task=t0,
            logs=["[mock] welcome to Flow CLI"],
            created_at=t0.created_at,
            lock=threading.Lock(),
        )
        t1 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="pretraining-train-8xa100",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(minutes=7),
            started_at=now - timedelta(minutes=6),
            instance_type="8xa100",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$64.00",
            created_by="you",
            ssh_host="10.0.0.11",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.0.11",
        )
        # Older than t0; mark as fully running to avoid showing as "starting"
        t1.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_RUNNING",
            "project": "pretraining",
        }
        t1.instances = [f"inst-{t1.task_id}-0"]
        self._tasks[t1.task_id] = _MockTaskState(
            task=t1,
            logs=["[mock] demo-training running"],
            created_at=t1.created_at,
            lock=threading.Lock(),
        )

        t2 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="pretraining-pending-a100-40g",
            status=TaskStatus.PENDING,
            config=None,
            created_at=now - timedelta(minutes=1),
            instance_type="a100-40gb",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$8.00",
            created_by="you",
            ssh_host=None,
            ssh_port=22,
            ssh_user="ubuntu",
        )
        t2.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_SCHEDULED",
            "project": "pretraining",
        }
        t2.instances = [f"inst-{t2.task_id}-0"]
        self._tasks[t2.task_id] = _MockTaskState(
            task=t2,
            logs=["[mock] provisioning"],
            created_at=t2.created_at,
            lock=threading.Lock(),
        )

        t3 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="inference-serving",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(minutes=3),
            started_at=now - timedelta(minutes=3),
            instance_type="h100",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$24.00",
            created_by="you",
            ssh_host="10.0.0.13",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.0.13",
        )
        # Keep this as running (only two very young tasks should appear as starting)
        t3.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_RUNNING",
            "project": "inference-optimization",
        }
        t3.instances = [f"inst-{t3.task_id}-0"]
        self._tasks[t3.task_id] = _MockTaskState(
            task=t3,
            logs=["[mock] demo-inference serving"],
            created_at=t3.created_at,
            lock=threading.Lock(),
        )

        t4 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="post-training-eval",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=5),
            started_at=now - timedelta(days=5, minutes=1),
            completed_at=None,
            instance_type="a100-40gb",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$8.00",
            created_by="you",
            ssh_host=None,
            ssh_port=22,
            ssh_user="ubuntu",
        )
        t4.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_RUNNING",
            "project": "post-training-team",
        }
        t4.instances = [f"inst-{t4.task_id}-0"]
        self._tasks[t4.task_id] = _MockTaskState(
            task=t4,
            logs=["[mock] post-processing complete"],
            created_at=t4.created_at,
            lock=threading.Lock(),
        )

        t5 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="post-training-fine-tune",
            status=TaskStatus.RUNNING,  # shown as 'starting' (no ssh_host)
            config=None,
            created_at=now - timedelta(minutes=2),
            started_at=now - timedelta(minutes=2),
            instance_type="8xh100",
            num_instances=1,
            region="demo-region-1",
            cost_per_hour="$192.00",
            message="Starting fine-tune pipeline",
            created_by="you",
            ssh_host=None,
            ssh_port=22,
            ssh_user="ubuntu",
        )
        # One of the two very young tasks that appear as starting (<12 min)
        t5.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_STARTING",
            "project": "post-training-team",
        }
        t5.instances = [f"inst-{t5.task_id}-0"]
        self._tasks[t5.task_id] = _MockTaskState(
            task=t5,
            logs=[
                "[mock] pulling container image",
                "[mock] preparing datasets",
                "[mock] launching trainers",
            ],
            created_at=t5.created_at,
            lock=threading.Lock(),
        )

        t6 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="pretraining-2048-h100",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(hours=6),
            started_at=now - timedelta(hours=6),
            instance_type="8xh100",
            num_instances=256,
            region="demo-region-1",
            cost_per_hour="$384.00",
            created_by="you",
            ssh_host="10.0.1.1",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.1.1",
        )
        # This one is older; show as fully running
        t6.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_RUNNING",
            "project": "pretraining",
        }
        t6.instances = [f"inst-{t6.task_id}-{i}" for i in range(256)]
        self._tasks[t6.task_id] = _MockTaskState(
            task=t6,
            logs=["[mock] orchestrator ready", "[mock] workers connected: 256"],
            created_at=t6.created_at,
            lock=threading.Lock(),
        )

        # Additional Flow tasks with varied ages and GPUs (H200/B200/A100-40GB), aligned to teams
        def add_simple(
            name: str,
            itype: str,
            age: timedelta,
            status: TaskStatus,
            project: str,
            logs: list[str],
            completed: timedelta | None = None,
        ):
            t_id = f"mock-{uuid.uuid4().hex[:8]}"
            created = now - age
            started = created if status != TaskStatus.PENDING else None
            completed_at = (
                (now - completed)
                if (
                    completed
                    and status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
                )
                else None
            )
            # Assign a deterministic demo IP for RUNNING tasks to reflect SSH readiness
            demo_ip = None
            if status == TaskStatus.RUNNING:
                # Derive simple pseudo IPs from name hash (stable but not real)
                import hashlib

                h = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:6], 16)
                demo_ip = f"10.{(h >> 16) & 0xFF}.{(h >> 8) & 0xFF}.{h & 0xFF}"

            t = Task(
                task_id=t_id,
                name=name,
                status=status,
                config=None,
                created_at=created,
                started_at=started,
                completed_at=completed_at,
                instance_type=itype,
                num_instances=1,
                region="demo-region-1",
                cost_per_hour="$8.00",
                created_by="you",
                ssh_host=demo_ip,
                ssh_port=22,
                ssh_user="ubuntu",
                shell_command=(f"ssh ubuntu@{demo_ip}" if demo_ip else None),
            )
            # Older jobs should appear as fully running (not "starting")
            t.provider_metadata = {
                "origin": "flow-cli",
                "instance_status": "STATUS_RUNNING",
                "project": project,
            }
            t.instances = [f"inst-{t_id}-0"]
            self._tasks[t.task_id] = _MockTaskState(
                task=t, logs=logs, created_at=t.created_at, lock=threading.Lock()
            )

        add_simple(
            "post-training-sanity-1",
            "a100-40gb",
            timedelta(seconds=45),
            TaskStatus.RUNNING,
            "post-training-team",
            ["[mock] sanity checks running"],
        )
        # Keep both sanity tasks running for demo richness
        add_simple(
            "post-training-sanity-2",
            "a100-40gb",
            timedelta(minutes=10),
            TaskStatus.RUNNING,
            "post-training-team",
            ["[mock] additional checks running"],
        )
        add_simple(
            "reasoning-train-h200",
            "h200",
            timedelta(weeks=3),
            TaskStatus.RUNNING,
            "reasoning-research",
            ["[mock] h200 training loop active"],
        )
        # Add a running B200 job so it appears in the default (active) status view
        # Use an 8xB200 node configuration (multi-GPU per node)
        add_simple(
            "reasoning-rollout-b200",
            "8xb200",
            timedelta(hours=2),
            TaskStatus.RUNNING,
            "reasoning-research",
            ["[mock] 8xB200 rollout running"],
        )
        add_simple(
            "reasoning-experiment-b200",
            "b200",
            timedelta(days=365),
            TaskStatus.FAILED,
            "reasoning-research",
            ["[mock] oom on step 42"],
            completed=timedelta(days=364, hours=23),
        )

        # External cluster task (GUI-managed) under External section
        ext = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="cluster-mithril-gui",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=2),
            started_at=now - timedelta(days=2),
            instance_type="8xh100",
            num_instances=256,
            region="demo-region-1",
            cost_per_hour="$0.00",
            created_by="console",
            ssh_host="10.0.2.1",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.2.1",
        )
        # External cluster appears under the External group and should be running
        ext.provider_metadata = {
            "origin": "external",
            "instance_status": "STATUS_RUNNING",
            "project": "pretraining",
        }
        ext.instances = [f"inst-{ext.task_id}-{i}" for i in range(256)]
        self._tasks[ext.task_id] = _MockTaskState(
            task=ext,
            logs=["[mock] managed via GUI"],
            created_at=ext.created_at,
            lock=threading.Lock(),
        )

        # Flow-pane big GB200 NVL72 cluster (72 GPUs per node, 100 nodes)
        gb_flow = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="gb200-nvl72-cluster",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=1),
            started_at=now - timedelta(days=1),
            instance_type="gb200nvl72",
            num_instances=100,  # 100 nodes × 72 GPUs = 7200 GPUs
            region="demo-region-1",
            cost_per_hour="$0.00",
            created_by="you",
            ssh_host="10.0.3.1",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.3.1",
        )
        gb_flow.provider_metadata = {
            "origin": "flow-cli",
            "instance_status": "STATUS_RUNNING",
            "project": "infrastructure",
        }
        gb_flow.instances = [f"inst-{gb_flow.task_id}-{i}" for i in range(100)]
        self._tasks[gb_flow.task_id] = _MockTaskState(
            task=gb_flow,
            logs=["[mock] GB200 NVL72 cluster running (Flow-managed)"],
            created_at=gb_flow.created_at,
            lock=threading.Lock(),
        )

        # Additional External mega-clusters
        # 1) training cluster with ~20k GPUs (8×H100 per node × 2,500 nodes)
        ext1 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="training-cluster",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=10),
            started_at=now - timedelta(days=10),
            instance_type="8xh100",
            num_instances=2500,  # 8 * 2500 = 20000 GPUs
            region="demo-region-1",
            cost_per_hour="$0.00",
            created_by="external",
            ssh_host="10.0.2.2",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.2.2",
        )
        ext1.provider_metadata = {"origin": "external", "instance_status": "STATUS_RUNNING"}
        self._tasks[ext1.task_id] = _MockTaskState(
            task=ext1,
            logs=["[mock] external training cluster active"],
            created_at=ext1.created_at,
            lock=threading.Lock(),
        )

        # 2) guilds-cluster with ~100k GPUs (8×H100 per node × 12,500 nodes)
        ext2 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="guilds-cluster",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=21),
            started_at=now - timedelta(days=21),
            instance_type="8xh100",
            num_instances=12500,  # 8 * 12500 = 100000 GPUs
            region="demo-region-1",
            cost_per_hour="$0.00",
            created_by="external",
            ssh_host="10.0.2.3",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.2.3",
        )
        ext2.provider_metadata = {"origin": "external", "instance_status": "STATUS_RUNNING"}
        self._tasks[ext2.task_id] = _MockTaskState(
            task=ext2,
            logs=["[mock] guilds mega cluster active"],
            created_at=ext2.created_at,
            lock=threading.Lock(),
        )

        # 3) integrated-private-cloud with ~100k GPUs (8×H100 per node × 12,500 nodes)
        ext3 = Task(
            task_id=f"mock-{uuid.uuid4().hex[:8]}",
            name="integrated-private-cloud",
            status=TaskStatus.RUNNING,
            config=None,
            created_at=now - timedelta(days=30),
            started_at=now - timedelta(days=30),
            instance_type="8xh100",
            num_instances=12500,  # 8 * 12500 = 100000 GPUs
            region="demo-region-1",
            cost_per_hour="$0.00",
            created_by="external",
            ssh_host="10.0.2.4",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh ubuntu@10.0.2.4",
        )
        ext3.provider_metadata = {"origin": "external", "instance_status": "STATUS_RUNNING"}
        self._tasks[ext3.task_id] = _MockTaskState(
            task=ext3,
            logs=["[mock] integrated private cloud active"],
            created_at=ext3.created_at,
            lock=threading.Lock(),
        )

        # Seed some demo volumes
        for name, size in (
            ("dataset-imagenet", 500),
            ("pretrained-llama-7b", 100),
            ("checkpoints", 200),
        ):
            vol_id = f"mock-vol-{uuid.uuid4().hex[:6]}"
            self._volumes[vol_id] = Volume(
                volume_id=vol_id,
                name=name,
                size_gb=size,
                region="demo-region-1",
                interface="block",  # type: ignore
                created_at=now,
            )

    # ===== Capabilities and optional stubs =====
    def get_capabilities(self) -> ProviderCapabilities:  # type: ignore[override]
        """Return feature flags for the mock provider.

        Demo/mock provider intentionally does not support reservations or remote ops.
        """
        return ProviderCapabilities(
            supports_spot_instances=True,
            supports_on_demand=True,
            supports_multi_node=True,
            supports_attached_storage=True,
            supports_shared_storage=False,
            supports_reservations=False,
        )

    # Reservations are not supported in mock mode; provide safe stubs to avoid AttributeError
    def list_reservations(
        self, params: dict[str, Any] | None = None
    ) -> list[dict]:  # pragma: no cover - simple stub
        return []

    def get_reservation(self, reservation_id: str):  # pragma: no cover - simple stub
        raise FlowError(
            "Reservations are not supported by the mock provider",
        )

    def normalize_instance_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:  # pragma: no cover - simple stub
        """Basic normalization mirroring the interface's default guidance.

        Returns (instance_type, num_instances, warning_message).
        """
        if not gpu_type:
            gpu_type = "a100"
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return f"8x{gpu_type}", gpu_count // 8, None
        if gpu_count >= 4 and gpu_count % 4 == 0:
            return f"4x{gpu_type}", gpu_count // 4, None
        if gpu_count >= 2 and gpu_count % 2 == 0:
            return f"2x{gpu_type}", gpu_count // 2, None
        return gpu_type, gpu_count, None


# Register provider on import
ProviderRegistry.register("mock", MockProvider)
