"""Unified GPU workload orchestration.

A concise, explicit interface for submitting, monitoring, and managing GPU
workloads across providers. Designed for the common path with clear escape
hatches.

Examples:
    Quick start:
        >>> flow = Flow()
        >>> task = flow.run("python train.py", instance_type="a100", wait=True)
        >>> print(task.status)

    Using TaskConfig with volumes, environment, image, and code_root:
        >>> from flow.sdk.models import TaskConfig, VolumeSpec
        >>> cfg = TaskConfig(
        ...     name="ddp-train",
        ...     instance_type="8xa100",
        ...     command=["torchrun", "--nproc_per_node=8", "train.py"],
        ...     env={"EPOCHS": "100", "BATCH_SIZE": "512"},
        ...     volumes=[VolumeSpec(size_gb=500, mount_path="/data", name="datasets")],
        ...     image="pytorch/pytorch:2.2.2-cuda12.1-cudnn8",
        ...     code_root="./src",
        ...     max_price_per_hour=25.0,
        ... )
        >>> task = flow.run(cfg, wait=True)
        >>> for line in flow.logs(task.task_id, follow=True):
        ...     if "loss:" in line: break
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

"""
Note: core and adapter dependencies are imported lazily inside methods to keep
the SDK surface thin and reduce cold import time, and to avoid hard coupling
to infrastructure layers in static analysis.
"""

# Avoid importing loaders here to prevent circular imports during module import
from flow.sdk.models import (
    AvailableInstance,
    MountSpec,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
)

if TYPE_CHECKING:  # avoid runtime circular imports during module import
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore
from flow.application.run_task import RunService
from flow.errors import (
    AuthenticationError,
    FlowError,
    ResourceNotAvailableError,
    VolumeError,
)
from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit

if TYPE_CHECKING:  # pragma: no cover - imported for static type checking only
    from flow.sdk.dev import DevEnvironment

logger = logging.getLogger(__name__)


# ================== Type Definitions ==================


class GPUInstanceDict(TypedDict):
    """GPU instance dictionary returned by _find_gpus_by_memory()."""

    name: str
    gpu_memory_gb: int
    price_per_hour: float
    gpu_model: str


class TaskDict(TypedDict):
    """Task dictionary returned by list() method."""

    id: str
    name: str
    status: str
    instance_type: str
    created: str | None


class InstanceRequirements(TypedDict, total=False):
    """Instance requirements dictionary for find_instances()."""

    instance_type: str
    min_gpu_count: int
    max_price: float
    region: str
    gpu_memory_gb: int
    gpu_type: str


class CatalogEntry(TypedDict):
    """Instance catalog entry dictionary."""

    name: str
    gpu_type: str
    gpu_count: int
    price_per_hour: float
    available: bool
    gpu: dict[str, Any]  # Nested GPU info with model and memory_gb


class Flow:
    """Primary client for submitting and managing GPU jobs.

    - Simple for 90% of use cases (one obvious way to run a task)
    - Explicit configuration via `TaskConfig` when needed
    - Clean access to logs, SSH, volumes, and instance discovery
    """

    def __init__(self, config: Config | None = None, auto_init: bool = False):
        """Create a Flow client.

        Args:
            config: Explicit configuration. If omitted, environment discovery is used.
            auto_init: If True and auth is missing, trigger interactive setup (CLI contexts).

        Raises:
            AuthenticationError: If credentials are missing and `auto_init` is False.
        """
        if config:
            self.config = config
        else:
            try:
                # In demo/mock mode, do not require auth
                require_auth = True
                # Avoid importing CLI from API: detect demo mode via env
                try:
                    demo_env = (os.environ.get("FLOW_DEMO_MODE") or "").strip().lower()
                    if demo_env in {"1", "true", "yes", "on"}:
                        require_auth = False
                except Exception:
                    pass
                from flow.application.config.config import Config  # local import

                self.config = Config.from_env(require_auth=require_auth)
            except ValueError as e:
                if auto_init:
                    # Non-CLI contexts should not attempt interactive setup here.
                    # Retry a strict load once; otherwise instruct the user to run 'flow init'.
                    try:
                        from flow.application.config.config import Config  # local import

                        self.config = Config.from_env(require_auth=True)
                    except Exception:
                        raise AuthenticationError(
                            "Authentication not configured",
                            suggestions=[
                                "Run 'flow init' to configure your API key interactively",
                                "Or set MITHRIL_API_KEY in your environment",
                                "Non-interactive: flow init --api-key $MITHRIL_API_KEY --yes",
                            ],
                            error_code="AUTH_001",
                        ) from e
                else:
                    # In SDK usage, re-raise as structured auth error
                    raise AuthenticationError(
                        "Authentication not configured",
                        suggestions=[
                            "Set MITHRIL_API_KEY in your environment",
                            "Or initialize credentials with flow.init() / 'flow init'",
                        ],
                        error_code="AUTH_001",
                    ) from e

        self._provider: IProvider | None = None
        self._run_svc: RunService | None = None
        self._dev = None
        self._storage_svc = None
        self._provider_facets = None  # cached facets view (optional)

    @property
    def dev(self) -> DevEnvironment:
        """Access the persistent dev VM API.

        Returns:
            DevEnvironment: Manage a long-lived VM for fast iteration.
        """
        if self._dev is None:
            from flow.sdk.dev import DevEnvironment

            self._dev = DevEnvironment(self)
        return self._dev

    def dev_context(self, auto_stop: bool = False) -> DevEnvironment:
        """Context manager for the dev VM.

        Args:
            auto_stop: Stop the VM on context exit.

        Returns:
            DevEnvironment.
        """
        from flow.sdk.dev import DevEnvironment

        return DevEnvironment(self, auto_stop=auto_stop)

    def _find_gpus_by_memory(
        self, min_memory_gb: int, max_price: float | None = None
    ) -> list[GPUInstanceDict]:
        """Find GPUs by minimum memory and optional limit price via selection service."""
        provider = self._ensure_provider()
        from flow.core.resources.gpu_selection import GPUSelectionService  # local import

        selector = GPUSelectionService(provider)
        results = selector.find_instances_by_min_memory(min_memory_gb, max_price)
        # Cast to GPUInstanceDict list to satisfy type expectations
        return [
            {
                "name": r.get("name", "unknown"),
                "gpu_memory_gb": int(r.get("gpu_memory_gb", 0) or 0),
                "price_per_hour": float(r.get("price_per_hour", 0.0) or 0.0),
                "gpu_model": str(r.get("gpu_model", "unknown")),
            }
            for r in results
        ]

    def get_remote_operations(self) -> object:
        """Return the provider's remote operations interface.

        Raises:
            NotImplementedError: If the provider lacks remote ops.
        """
        provider = self._ensure_provider()

        if not hasattr(provider, "get_remote_operations"):
            raise NotImplementedError(
                f"Provider {provider.__class__.__name__} doesn't support remote operations"
            )

        return provider.get_remote_operations()

    def wait_for_ssh(
        self,
        task_id: str,
        timeout: int = 600,
        show_progress: bool = True,
        *,
        progress_adapter: object | None = None,
    ) -> Task:
        """Block until SSH is ready for the task or time out.

        Raises:
            SSHNotReadyError | TimeoutError.
        """
        from flow.sdk.ssh_utils import wait_for_task_ssh_info

        task = self.get_task(task_id)
        provider = self._ensure_provider()

        return wait_for_task_ssh_info(
            task=task,
            provider=provider,
            timeout=timeout,
            show_progress=show_progress,
            progress_adapter=progress_adapter,
        )

    def get_ssh_tunnel_manager(self) -> object:
        """Return the provider's SSH tunnel manager.

        Raises:
            NotImplementedError: If unsupported by the provider.
        """
        provider = self._ensure_provider()

        if not hasattr(provider, "get_ssh_tunnel_manager"):
            raise NotImplementedError(
                f"Provider {provider.__class__.__name__} doesn't support SSH tunnels"
            )

        return provider.get_ssh_tunnel_manager()

    # ---- SSH helpers (provider fallback) ----
    def resolve_ssh_endpoint(self, task_id: str, node: int | None = None) -> tuple[str, int]:
        """Resolve SSH endpoint (host, port) for a task (provider fallback)."""
        provider = self._ensure_provider()
        if hasattr(provider, "resolve_ssh_endpoint"):
            return provider.resolve_ssh_endpoint(task_id, node)  # type: ignore[attr-defined]
        task = self.get_task(task_id)
        host = getattr(task, "ssh_host", None)
        port = getattr(task, "ssh_port", 22) or 22
        if not host:
            raise ValueError("SSH endpoint not available for this task")
        return str(host), int(port)

    def get_task_ssh_connection_info(self, task_id: str) -> tuple[Path | None, str]:
        """Return (ssh_key_path, error_message) for a task, if provider supports it."""
        provider = self._ensure_provider()
        if hasattr(provider, "get_task_ssh_connection_info"):
            return provider.get_task_ssh_connection_info(task_id)  # type: ignore[attr-defined]
        return None, "Provider does not expose SSH connection info"

    def _ensure_provider(self) -> IProvider:
        """Return the lazily-initialized provider instance (cached)."""
        if self._provider is None:
            from flow.adapters.providers.factory import create_provider  # local import

            self._provider = create_provider(self.config)
        return self._provider

    @property
    def provider(self) -> IProvider:
        """Compute provider backing this client (lazily created)."""
        return self._ensure_provider()

    def run(
        self,
        task: TaskConfig | str | Path,
        wait: bool = False,
        mounts: str | dict[str, str] | None = None,
    ) -> Task:
        """Submit a task.

        Args:
            task: `TaskConfig`, path to YAML, or string path for YAML.
            wait: If True, block until the task is running before returning.
            mounts: Optional data mounts; string or mapping of target->source.

        Returns:
            Task: Handle for status, logs, SSH, cancel, etc.

        Raises:
            ValidationError: Invalid configuration or missing fields.
            FlowError: Provider errors or capacity issues.
            FileNotFoundError: When a YAML file does not exist.

        Examples:
            Command as a string with an explicit instance type:
                >>> task = flow.run("python train.py --epochs 10", instance_type="a100", wait=True)

            Full TaskConfig with volumes and limit price:
                >>> from flow.sdk.models import TaskConfig, VolumeSpec
                >>> cfg = TaskConfig(
                ...     name="train",
                ...     instance_type="4xa100",
                ...     command=["python", "-m", "torch.distributed.run", "--nproc_per_node=4", "train.py"],
                ...     volumes=[VolumeSpec(size_gb=200, mount_path="/data", name="train-data")],
                ...     max_price_per_hour=12.0,
                ... )
                >>> task = flow.run(cfg)

            Capability-based selection (cheapest GPU with >= 40GB):
                >>> cfg = TaskConfig(name="infer", min_gpu_memory_gb=40, command="python serve.py")
                >>> task = flow.run(cfg)
        """
        # Capability-based selection fallback (before submission) when using TaskConfig
        if isinstance(task, TaskConfig) and (not task.instance_type) and task.min_gpu_memory_gb:
            catalog = self._load_instance_catalog()
            min_mem = int(task.min_gpu_memory_gb or 0)
            max_price = getattr(task, "max_price_per_hour", None)
            candidates: list[dict[str, Any]] = []
            for entry in catalog:
                try:
                    gpu = entry.get("gpu", {}) or {}
                    mem = int(gpu.get("memory_gb", 0) or 0)
                    price = float(entry.get("price_per_hour", 0.0) or 0.0)
                    if mem >= min_mem and (max_price is None or price <= max_price):
                        candidates.append(entry)
                except Exception:
                    continue
            if not candidates:
                if max_price is not None:
                    raise ResourceNotAvailableError(
                        f"No GPU instances found under ${float(max_price):.1f}/hour"
                    )
                raise ResourceNotAvailableError(f"No GPU instances found with at least {min_mem}GB")
            candidates.sort(key=lambda e: float(e.get("price_per_hour", 0.0) or 0.0))
            chosen = candidates[0]
            inst = chosen.get("instance_type") or chosen.get("name")
            if isinstance(inst, str) and inst:
                task = task.model_copy(update={"instance_type": inst})
                try:
                    logger.info(
                        f"Auto-selected {inst} (${float(chosen.get('price_per_hour') or 0.0):.1f}/hour)"
                    )
                except Exception:
                    pass

        # Normalize task into TaskConfig
        provider = self._ensure_provider()
        cfg: TaskConfig
        if isinstance(task, TaskConfig):
            cfg = task
        elif isinstance(task, (str, Path)):
            from pathlib import Path as _Path

            path = _Path(task)
            if not path.exists():
                raise FileNotFoundError(f"Task config file not found: {path}")
            import yaml as _yaml  # local import

            with open(path, encoding="utf-8") as f:
                data = _yaml.safe_load(f) or {}
            cfg = TaskConfig(**data)
        else:
            raise TypeError("task must be TaskConfig, str path, or Path")

        # Optional mounts override
        if mounts:
            from flow.core.data.mounts import normalize_mounts_param  # local import

            cfg = cfg.model_copy(update={"data_mounts": normalize_mounts_param(mounts)})

        # Submit via provider port
        instance = cfg.instance_type or "auto"
        task_obj = provider.submit_task(instance, cfg)

        try:
            logger.info(f"Task submitted successfully: {task_obj.task_id}")
        except Exception:
            pass

        if wait:
            try:
                task_obj.wait()
            except Exception:
                # Fall back to simple poll if wait() is not supported on Task implementation
                while True:
                    status = provider.get_task_status(task_obj.task_id)
                    if str(getattr(status, "value", status)).lower() in {
                        "completed",
                        "failed",
                        "cancelled",
                    }:
                        break
                    time.sleep(2)

        return task_obj

    def status(self, task_id: str) -> str:
        """Return the task status string (pending, running, completed, failed, cancelled)."""
        provider = self._ensure_provider()
        status = provider.get_task_status(task_id)
        return status.value.lower()

    def cancel(self, task_id: str) -> None:
        """Request cancellation of a running or pending task."""
        provider = self._ensure_provider()
        success = provider.stop_task(task_id)
        if not success:
            raise FlowError(f"Failed to cancel task {task_id}")
        logger.info(f"Task {task_id} cancelled successfully")

    def logs(
        self,
        task_id: str,
        follow: bool = False,
        tail: int = 100,
        stderr: bool = False,
        *,
        source: str | None = None,
        stream: str | None = None,
    ) -> str | Iterator[str]:
        """Return recent logs or stream them in real time.

        Args:
            task_id: The task to read logs from.
            follow: If True, stream logs until the task completes.
            tail: Number of trailing lines to fetch when `follow` is False.
            stderr: If True, select stderr (may be merged by some providers).

        Returns:
            str | Iterator[str]: A string (when `follow=False`) or an iterator of lines.

        Examples:
            Fetch and print the last 50 lines:
                >>> print(flow.logs(task_id, tail=50))

            Stream logs and stop after an error:
                >>> for line in flow.logs(task_id, follow=True):
                ...     if "ERROR" in line:
                ...         break
        """
        # Determine provider and facets first
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)

        # Map CLI-facing source/stream to provider log_type semantics.
        # Default to container stdout/stderr; enable richer types for providers that support them.
        prov_name = str(getattr(provider, "name", "")).lower()

        # Start with basic selection
        log_type = "stderr" if stderr else "stdout"

        # Normalize inputs
        src = (source or "").lower().strip() or None
        strm = (stream or "").lower().strip() or None

        # Only Mithril provider currently supports extended sources like host/startup/combined/auto
        supports_extended = prov_name == "mithril"

        if supports_extended:
            if src in {"host", "startup"}:
                log_type = src
            elif src in {"both", "all"} or strm == "combined":
                log_type = "combined"
            elif src == "auto":
                log_type = "auto"
            else:
                # Container source: allow stream override
                if strm == "stderr":
                    log_type = "stderr"
                elif strm == "combined":
                    log_type = "combined"
                else:
                    log_type = "stderr" if stderr else "stdout"
        else:
            # For non-extended providers, ignore source/stream beyond stderr flag
            log_type = "stderr" if stderr else "stdout"

        # Prefer facet when available; fall back to provider methods
        if facets and getattr(facets, "logs", None) is not None:
            if follow:
                return facets.logs.stream_task_logs(
                    task_id, log_type=log_type, follow=True, tail=tail
                )
            return facets.logs.get_task_logs(task_id, tail=tail, log_type=log_type)
        if follow:
            return provider.stream_task_logs(task_id, log_type=log_type, follow=True, tail=tail)
        return provider.get_task_logs(task_id, tail=tail, log_type=log_type)

    def shell(
        self,
        task_id: str,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
        record: bool = False,
    ) -> None:
        """Open an interactive shell or run a command on the task instance.

        Examples:
            Open a shell:
                >>> flow.shell(task_id)

            Run a one-off command:
                >>> flow.shell(task_id, command="nvidia-smi")
        """
        task = self.get_task(task_id)
        task.shell(command, node=node, progress_context=progress_context, record=record)

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List recent tasks, optionally filtered by status.

        Examples:
            List running tasks and print their names:
                >>> from flow.sdk.models import TaskStatus
                >>> for t in flow.list_tasks(status=TaskStatus.RUNNING):
                ...     print(t.name)
        """
        provider = self._ensure_provider()
        tasks = provider.list_tasks(status=status, limit=limit, force_refresh=force_refresh)
        try:
            if __import__("os").environ.get("FLOW_STATUS_DEBUG"):
                prov = provider.__class__.__name__
                stat = (
                    [getattr(s, "value", str(s)) for s in status]
                    if isinstance(status, list)
                    else getattr(status, "value", str(status)) if status is not None else None
                )
                logging.getLogger("flow.status.sdk").info(
                    f"sdk.list_tasks: provider={prov} status={stat} limit={limit} -> count={len(tasks) if tasks else 0}"
                )
        except Exception:
            pass
        return tasks

    # ------------------ Sub-clients (experimental stable facade) ------------------
    class TasksClient:
        """Task operations sub-client.

        Thin wrapper around `Flow` methods for clearer namespacing: `flow.tasks.list()`,
        `flow.tasks.get(id)`, `flow.tasks.logs(...)`, etc.
        """

        def __init__(self, flow: Flow) -> None:
            self._flow = flow

        def list(
            self,
            *,
            status: TaskStatus | list[TaskStatus] | None = None,
            limit: int = 10,
            force_refresh: bool = False,
        ) -> list[Task]:
            return self._flow.list_tasks(status=status, limit=limit, force_refresh=force_refresh)

        def get(self, task_id: str) -> Task:
            return self._flow.get_task(task_id)

        def status(self, task_id: str) -> str:
            return self._flow.status(task_id)

        def cancel(self, task_id: str) -> None:
            return self._flow.cancel(task_id)

        def logs(
            self,
            task_id: str,
            *,
            follow: bool = False,
            tail: int = 100,
            stderr: bool = False,
            source: str | None = None,
            stream: str | None = None,
        ) -> str | Iterator[str]:
            return self._flow.logs(
                task_id, follow=follow, tail=tail, stderr=stderr, source=source, stream=stream
            )

    class VolumesClient:
        """Volume operations sub-client.

        Use as `flow.volumes.list()`, `flow.volumes.create(...)`, etc.
        """

        def __init__(self, flow: Flow) -> None:
            self._flow = flow

        def list(self, *, limit: int = 100) -> list[Volume]:
            return self._flow.list_volumes(limit=limit)

        def create(
            self,
            size_gb: int,
            *,
            name: str | None = None,
            interface: Literal["block", "file"] = "block",
            region: str | None = None,
        ) -> Volume:
            return self._flow.create_volume(
                size_gb=size_gb, name=name, interface=interface, region=region
            )

        def delete(self, volume_id: str) -> None:
            return self._flow.delete_volume(volume_id)

        def mount(self, volume_id: str, task_id: str, *, mount_point: str | None = None) -> bool:
            return self._flow.mount_volume(volume_id, task_id, mount_point=mount_point)

    class ReservationsClient:
        """Reservations operations sub-client.

        Facet-first wrappers with provider fallback. Exposes:
          - list()
          - get(reservation_id)
          - availability(instance_type=..., region=..., earliest_start_time=..., latest_end_time=...)
        """

        def __init__(self, flow: Flow) -> None:
            self._flow = flow

        def list(self, params: dict[str, Any] | None = None) -> list[Any]:
            return self._flow.list_reservations(params)

        def get(self, reservation_id: str) -> Any | None:
            return self._flow.get_reservation(reservation_id)

        def availability(
            self,
            *,
            instance_type: str,
            region: str,
            earliest_start_time: str,
            latest_end_time: str,
            **kwargs: Any,
        ) -> list[dict[str, Any]]:
            params = {
                "instance_type": instance_type,
                "region": region,
                "earliest_start_time": earliest_start_time,
                "latest_end_time": latest_end_time,
            }
            params.update({k: v for k, v in kwargs.items() if v is not None})
            return self._flow.reservation_availability(params)

    @property
    def tasks(self) -> Flow.TasksClient:
        if not hasattr(self, "_tasks_client"):
            self._tasks_client = Flow.TasksClient(self)
        return self._tasks_client  # type: ignore[attr-defined]

    @property
    def volumes(self) -> Flow.VolumesClient:
        if not hasattr(self, "_volumes_client"):
            self._volumes_client = Flow.VolumesClient(self)
        return self._volumes_client  # type: ignore[attr-defined]

    @property
    def reservations(self) -> Flow.ReservationsClient:
        if not hasattr(self, "_reservations_client"):
            self._reservations_client = Flow.ReservationsClient(self)
        return self._reservations_client  # type: ignore[attr-defined]

    # Storage operations

    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: Literal["block", "file"] = "block",
        *,
        region: str | None = None,
    ) -> Volume:
        """Create a persistent volume.

        Args:
            size_gb: Capacity in GB.
            name: Optional display name (used in `volume://name`).
            interface: "block" (exclusive attach) or "file" (multi-attach).
            region: Optional region to create the volume in. When omitted, the
                provider's configured/default region is used.

        Returns:
            Volume.

        Examples:
            Create and attach volumes to a task:
                >>> data = flow.create_volume(500, name="datasets")
                >>> ckpt = flow.create_volume(100, name="checkpoints")
                >>> cfg = TaskConfig(
                ...     name="train",
                ...     instance_type="a100",
                ...     command="python train.py",
                ...     volumes=[
                ...         {"volume_id": data.volume_id, "mount_path": "/data"},
                ...         {"volume_id": ckpt.volume_id, "mount_path": "/ckpts"},
                ...     ],
                ... )
                >>> task = flow.run(cfg)
        """
        # Validate interface parameter
        if interface not in ["block", "file"]:
            raise ValueError(f"Invalid interface: {interface}. Must be 'block' or 'file'")

        # Prefer storage facet; fall back to provider
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        if facets and getattr(facets, "storage", None) is not None:
            volume = facets.storage.create_volume(
                size_gb, name=name, interface=interface, region=region
            )
        else:
            volume = provider.create_volume(size_gb, name=name, interface=interface, region=region)
        logger.info(f"Created {interface} volume {volume.volume_id} ({size_gb}GB)")
        return volume

    def delete_volume(self, volume_id: str) -> None:
        """Delete a volume permanently (no recovery).

        Example:
            >>> flow.delete_volume("vol_abc123")
        """
        # Prefer storage facet
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        if facets and getattr(facets, "storage", None) is not None:
            success = bool(facets.storage.delete_volume(volume_id))
        else:
            success = bool(provider.delete_volume(volume_id))
        if not success:
            raise VolumeError(
                f"Failed to delete volume {volume_id}",
                suggestions=[
                    "Check if volume is currently attached to a running task",
                    "Verify volume exists with 'flow volume list'",
                    "Ensure you have permission to delete this volume",
                ],
                error_code="VOLUME_002",
            )
        logger.info(f"Volume {volume_id} deleted successfully")

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes for the current project (newest first).

        Example:
            >>> for v in flow.list_volumes():
            ...     print(v.name, v.size_gb)
        """
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        if facets and getattr(facets, "storage", None) is not None:
            return facets.storage.list_volumes(limit=limit)
        return provider.list_volumes(limit=limit)

    def mount_volume(self, volume_id: str, task_id: str, mount_point: str | None = None) -> bool:
        """Attach a volume to a task's configuration at an optional mount point.

        Notes:
            - Default mount path is ``/volumes/{volume_name}`` when ``mount_point`` is not provided.
            - Providers may pause/resume the task briefly to update volume attachments.
            - If the instance has already booted, the mount may not take effect immediately; a
              manual mount or restart may be required for the path to become accessible.

        Examples:
            Mount by name to the default path:
                >>> flow.mount_volume("datasets", task_id)

            Mount by ID to a custom path:
                >>> flow.mount_volume("vol_abc123", task_id, mount_point="/volumes/inputs")
        """
        # Prefer storage facet; fall back to provider. Provider signature is
        # (task_id, volume_id, mount_path).
        # Use a stable default under /volumes when mount_point is not provided
        # to match CLI expectations and provider startup scripts.
        if mount_point:
            mount_path = mount_point
        else:
            try:
                from flow.utils.paths import default_volume_mount_path as _default_mount

                mount_path = _default_mount(volume_id=volume_id)
            except Exception:
                # Conservative fallback
                mount_path = "/volumes/volume"
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        if facets and getattr(facets, "storage", None) is not None:
            return bool(facets.storage.mount_volume(task_id, volume_id, mount_path))
        try:
            return bool(provider.mount_volume(task_id, volume_id, mount_path))
        except Exception:
            return False

    # ------------------ Reservations (experimental) ------------------
    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Any]:
        """List reservations if supported by the provider.

        Facet-first; falls back to provider method when available.
        Returns an empty list when unsupported.
        """
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        try:
            if facets and getattr(facets, "reservations", None) is not None:
                return list(facets.reservations.list_reservations(params))
        except Exception:
            pass
        if hasattr(provider, "list_reservations"):
            try:
                return list(provider.list_reservations(params))  # type: ignore[attr-defined]
            except Exception:
                return []
        return []

    def get_reservation(self, reservation_id: str) -> Any | None:
        """Get a reservation if supported by the provider.

        Returns None when unsupported.
        """
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        try:
            if facets and getattr(facets, "reservations", None) is not None:
                return facets.reservations.get_reservation(reservation_id)
        except Exception:
            pass
        if hasattr(provider, "get_reservation"):
            try:
                return provider.get_reservation(reservation_id)  # type: ignore[attr-defined]
            except Exception:
                return None
        return None

    def reservation_availability(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Return reservation availability if supported by the provider.

        Args:
            params: Keys include instance_type, region, earliest_start_time, latest_end_time

        Returns:
            A list of slots (as dicts). Empty list when unsupported or on error.
        """
        provider = self._ensure_provider()
        facets = self._get_facets_for_provider(provider)
        try:
            if facets and getattr(facets, "reservations", None) is not None:
                res = facets.reservations.get_reservation_availability(**params)  # type: ignore[arg-type]
                slots = res.get("data", res) if isinstance(res, dict) else res
                return [s for s in (slots or []) if isinstance(s, dict)]
        except Exception:
            pass
        if hasattr(provider, "get_reservation_availability"):
            try:
                res = provider.get_reservation_availability(**params)  # type: ignore[attr-defined]
                slots = res.get("data", res) if isinstance(res, dict) else res
                return [s for s in (slots or []) if isinstance(s, dict)]
            except Exception:
                return []
        return []

    # ------------------ Instance Planning (experimental) ------------------
    def normalize_instance_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize a GPU request to an instance_type and instance count.

        - Provider-first: attempts provider.normalize_instance_request().
          Accepts both legacy tuple shape ``(instance_type, num_instances, warning)``
          and dict shape ``{"instance_type": str, "num_instances": int, ...}``.
        - Robust fallback: uses a simple heuristic (2x/4x/8x) when unsupported
          or when provider returns an unexpected shape.
        """
        provider = self._ensure_provider()
        try:
            if hasattr(provider, "normalize_instance_request"):
                res = provider.normalize_instance_request(gpu_count, gpu_type)  # type: ignore[attr-defined]
                inst: str | None = None
                num: int | None = None
                warn: str | None = None

                # Tuple shapes: (inst, num) or (inst, num, warn)
                if isinstance(res, tuple):
                    if len(res) == 3:
                        inst, num, warn = res  # type: ignore[misc]
                    elif len(res) == 2:
                        inst, num = res  # type: ignore[misc]

                # Dict shapes from some providers/facets
                elif isinstance(res, dict):
                    inst = res.get("instance_type") or res.get("instance") or res.get("type")
                    warn = res.get("warning") or res.get("note")
                    # Prefer explicit num_instances if present
                    try:
                        num_val = res.get("num_instances")
                        num = int(num_val) if num_val is not None else None
                    except Exception:
                        num = None

                    # Derive from instance_type pattern like "8xa100" when needed
                    if inst and num is None:
                        try:
                            import re as _re

                            m = _re.match(r"^(\d+)x", str(inst).strip(), flags=_re.IGNORECASE)
                            if m:
                                per = int(m.group(1) or 0)
                                # Only trust common packaging sizes; otherwise fall back
                                if per in (2, 4, 8) and gpu_count % per == 0:
                                    num = gpu_count // per
                        except Exception:
                            pass

                if isinstance(inst, str) and isinstance(num, int) and num >= 1:
                    return (inst, num, warn)
        except Exception:
            # Fall through to heuristic
            pass

        # Heuristic fallback mirroring mock provider defaults
        gt = gpu_type or "a100"
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return (f"8x{gt}", gpu_count // 8, None)
        if gpu_count >= 4 and gpu_count % 4 == 0:
            return (f"4x{gt}", gpu_count // 4, None)
        if gpu_count >= 2 and gpu_count % 2 == 0:
            return (f"2x{gt}", gpu_count // 2, None)
        return (gt, gpu_count, None)

    # ------------------ User/Team (experimental) ------------------
    def get_user(self, user_id: str) -> Any | None:
        """Get user info if provider exposes it; otherwise None.

        Falls back to raw HTTP via provider.http when available.
        """
        provider = self._ensure_provider()
        try:
            if hasattr(provider, "get_user"):
                return provider.get_user(user_id)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Fallback via provider HTTP if present
        http = getattr(provider, "http", None)
        try:
            if http is not None:
                resp = http.request(method="GET", url=f"/users/{user_id}")
                return resp.get("data", resp) if isinstance(resp, dict) else resp
        except Exception:
            return None
        return None

    def get_user_teammates(self, user_id: str) -> Any:
        """Return teammates for a given user when supported; else []."""
        provider = self._ensure_provider()
        try:
            if hasattr(provider, "get_user_teammates"):
                return provider.get_user_teammates(user_id)  # type: ignore[attr-defined]
        except Exception:
            pass
        http = getattr(provider, "http", None)
        try:
            if http is not None:
                resp = http.request(method="GET", url=f"/users/{user_id}/teammates")
                return resp.get("data", resp) if isinstance(resp, dict) else []
        except Exception:
            return []
        return []

    # ------------------ SSH Keys (experimental) ------------------
    def ensure_default_ssh_key(self) -> str | None:
        """Ensure a default SSH key exists for the current project when supported.

        Returns the key id when created or already present; None when unsupported.
        """
        provider = self._ensure_provider()
        try:
            if hasattr(provider, "ensure_default_ssh_key"):
                return provider.ensure_default_ssh_key()  # type: ignore[attr-defined]
        except Exception:
            return None
        return None

    # ------------------ Code Upload (experimental) ------------------
    def upload_code_to_task(
        self,
        task_id: str,
        *,
        source_dir: Path | None = None,
        timeout: int = 600,
        console: object | None = None,
        target_dir: str = "/workspace",
        progress_reporter: object | None = None,
        git_incremental: bool | None = None,
    ) -> object:
        """Upload code to an existing task (facet/provider fallback).

        Prefers provider's richer upload (with progress). Falls back to storage facet
        `upload_directory` if available.
        """
        provider = self._ensure_provider()
        # Provider-first: richer progress and config support
        if hasattr(provider, "upload_code_to_task"):
            return provider.upload_code_to_task(  # type: ignore[attr-defined]
                task_id=task_id,
                source_dir=source_dir,
                timeout=timeout,
                console=console,
                target_dir=target_dir,
                progress_reporter=progress_reporter,
                git_incremental=git_incremental,
            )
        # Facet fallback: basic directory upload
        facets = self._get_facets_for_provider(provider)
        if facets and getattr(facets, "storage", None) is not None:
            from pathlib import Path as _Path

            src = source_dir or _Path.cwd()
            return facets.storage.upload_directory(task_id, src, target_dir)
        raise NotImplementedError("Code upload is not supported by this provider")

    def _get_facets_for_provider(self, provider: IProvider):
        """Return cached facets for a provider instance (or build once).

        Returns None if facets cannot be derived; call sites must handle fallback.
        """
        if self._provider_facets is not None:
            return self._provider_facets
        try:
            from flow.adapters.providers.registry import ProviderRegistry  # local import

            self._provider_facets = ProviderRegistry.facets_for_instance(provider)
            return self._provider_facets
        except Exception:
            return None

    def get_task(self, task_id: str) -> Task:
        """Return a `Task` handle for an existing job.

        Example:
            >>> t = flow.get_task(task_id)
            >>> print(t.status)
        """
        provider = self._ensure_provider()
        return provider.get_task(task_id)

    def find_instances(
        self,
        requirements: InstanceRequirements,
        limit: int = 10,
    ) -> list[AvailableInstance]:
        """Return available instances that match the given constraints.

        Example:
            >>> flow.find_instances({"gpu_type": "a100", "max_price": 8.0}, limit=5)
        """
        provider = self._ensure_provider()
        return provider.find_instances(requirements, limit=limit)

    def submit(
        self,
        command: str,
        *,
        gpu: str | None = None,
        mounts: str | dict[str, str] | None = None,
        instance_type: str | None = None,
        wait: bool = False,
    ) -> Task:
        """Submit a shell command with minimal configuration.

        Args:
            command: Passed to the container shell.
            gpu: e.g. "a100", "a100:4", or "gpu:40gb". Ignored if `instance_type` is set.
            mounts: Optional data mounts (string or mapping of target->source).
            instance_type: Explicit override of the instance type.
            wait: If True, block until the task completes.

        Returns:
            Task.

        Examples:
            Quick usage with GPU shorthand:
                >>> task = flow.submit("python train.py", gpu="a100")

            Multiple mounts:
                >>> task = flow.submit(
                ...     "torchrun --nproc_per_node=4 train.py",
                ...     gpu="a100:4",
                ...     mounts={
                ...         "/data": "volume://datasets",
                ...         "/models": "s3://bucket/pretrained/",
                ...     },
                ...     wait=True,
                ... )
        """
        # Build config dict first, then create TaskConfig
        config_dict = {
            "name": f"flow-submit-{int(time.time())}",
            "command": command,
            "image": "ubuntu:22.04",
            # Keep submit() names stable for tests and logs
            "unique_name": False,
        }

        # Select instance if needed
        if instance_type:
            config_dict["instance_type"] = instance_type
        elif gpu:
            from flow.core.resources.gpu_selection import (
                GPUSelectionService,
            )  # local import

            config_dict["instance_type"] = GPUSelectionService(
                self._ensure_provider()
            ).select_instance_type(gpu)
        else:
            config_dict["instance_type"] = "auto"

        # Defer mounts handling to run() via TaskConfig normalization
        if mounts:
            from flow.core.data.mounts import normalize_mounts_param  # local import

            config_dict["data_mounts"] = normalize_mounts_param(mounts)

        # Create TaskConfig with all fields set
        config = TaskConfig(**config_dict)

        # Use existing run method (single path)
        return self.run(config, wait=wait)

    def _load_instance_catalog(self) -> list[CatalogEntry]:
        """Return the cached instance catalog; refresh on TTL expiry."""
        # Check cache with 5-minute TTL to avoid stale pricing
        cache_ttl = 300  # 5 minutes
        now = time.time()

        if (
            hasattr(self, "_catalog_cache")
            and hasattr(self, "_catalog_cache_time")
            and now - self._catalog_cache_time < cache_ttl
        ):
            return self._catalog_cache

        # Load from provider
        provider = self._ensure_provider()
        instances = provider.find_instances({}, limit=1000)

        # Convert to dict format for matcher
        catalog = []
        for inst in instances:
            # Provider must parse its own format
            if not hasattr(provider, "parse_catalog_instance"):
                raise FlowError(
                    "Provider does not support catalog parsing",
                    suggestions=[
                        "Provider must implement parse_catalog_instance() method",
                        "Update to a newer version of the provider",
                        "Contact provider maintainer for support",
                    ],
                )
            catalog_entry = provider.parse_catalog_instance(inst)
            catalog.append(catalog_entry)

        # Cache with timestamp
        self._catalog_cache = catalog
        self._catalog_cache_time = now
        return catalog

    def _resolve_data_mounts(self, mounts: str | dict[str, str]) -> list[MountSpec]:
        """Normalize `mounts` into `MountSpec` entries with sensible defaults."""
        from flow.sdk.models import MountSpec

        # Convert single string to dict format
        if isinstance(mounts, str):
            # Centralized auto-target resolution
            from flow.core.mount_rules import auto_target_for_source

            mounts = {auto_target_for_source(mounts): mounts}

        # Create MountSpec for each entry
        mount_specs = []
        for target, source in mounts.items():
            # Determine mount type based on source
            if source.startswith("s3://"):
                mount_type = "s3fs"
            elif source.startswith("volume://"):
                mount_type = "volume"
            else:
                mount_type = "bind"

            mount_specs.append(MountSpec(source=source, target=target, mount_type=mount_type))

        return mount_specs

    def get_provider_init(self) -> IProviderInit:
        """Return the provider's initialization interface."""
        provider = self._ensure_provider()
        return provider.get_init_interface()

    def list_projects(self) -> list[dict[str, str]]:
        """List provider projects accessible to the current credentials."""
        init_interface = self.get_provider_init()
        return init_interface.list_projects()

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys (optionally filtered by project)."""
        init_interface = self.get_provider_init()
        return init_interface.list_ssh_keys(project_id)

    # ---- Provider-first SSH key management (simplified CLI surface) ----
    def list_platform_ssh_keys(self) -> list[dict[str, str]]:
        """List platform SSH keys via provider (preferred).

        Falls back to provider init interface if provider does not implement
        the SSH key methods. If the current provider lacks SSH key support
        (e.g., local), fall back to calling the Mithril API directly using
        the configured auth token and base URL. This keeps SSH key management
        available regardless of the active compute provider.
        """
        provider = self._ensure_provider()
        try:
            # Ensure provider-side SSHKeyManager is project-scoped before listing
            try:
                _ = self.get_ssh_key_manager()
            except Exception:
                _ = None
            raw = provider.get_ssh_keys()  # type: ignore[attr-defined]
            if isinstance(raw, list):
                return raw
        except Exception:
            pass
        # Fallback to init interface
        try:
            # Prefer scoping by project when available
            pid = getattr(provider, "project_id", None)
            init_interface = self.get_provider_init()
            keys = init_interface.list_ssh_keys(pid)
            if isinstance(keys, list) and keys:
                return keys
        except Exception:
            pass

        # Provider doesn't expose SSH key APIs or returned no data.
        # Attempt a direct Mithril API call using the configured auth token.
        try:
            # Prefer env override for API URL; default to production endpoint.
            import os as _os

            from flow.adapters.http.client import HttpClient  # local import
            from flow.adapters.providers.builtin.mithril.api.client import (
                MithrilApiClient,
            )  # local import

            base_url = (
                _os.getenv("MITHRIL_API_URL")
                or (
                    self.config.provider_config.get("api_url")
                    if isinstance(self.config.provider_config, dict)
                    else None
                )
                or "https://api.mithril.ai"
            )
            http = HttpClient(base_url=base_url, headers=self.config.get_headers())
            api = MithrilApiClient(http)
            pid = getattr(provider, "project_id", None)
            params = {"project": pid} if pid else {}
            raw = api.list_ssh_keys(params)
            # Normalize common shapes into a flat list
            if isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], list):
                return list(raw["data"])
            if isinstance(raw, list):
                return raw
        except Exception:
            pass
        return []

    def create_platform_ssh_key(self, name: str, public_key: str) -> dict[str, str]:
        """Create a platform SSH key via provider (preferred).

        Falls back to SSH key manager ensure path when available.
        """
        provider = self._ensure_provider()
        try:
            created = provider.create_ssh_key(name, public_key)  # type: ignore[attr-defined]
            if isinstance(created, dict):
                return created
        except Exception:
            pass
        # Fallback: use manager ensure_platform_keys
        try:
            mgr = self.get_ssh_key_manager()
            # ensure_platform_keys accepts file paths; emulate by saving to a temp file is heavy.
            # Instead, try provider-first only; if not available, return empty mapping.
            # Keeping fallback no-op to avoid writing files here.
            _ = mgr  # silence linter; legacy path intentionally skipped
        except Exception:
            pass
        return {}

    def delete_platform_ssh_key(self, key_id: str) -> bool:
        """Delete a platform SSH key via provider (preferred), else manager."""
        provider = self._ensure_provider()
        try:
            ok = provider.delete_ssh_key(key_id)  # type: ignore[attr-defined]
            return bool(ok)
        except Exception:
            pass
        try:
            mgr = self.get_ssh_key_manager()
            return bool(mgr.delete_key(key_id))
        except Exception:
            return False

    def get_ssh_key_manager(self):
        """Return the provider's SSH key manager interface."""
        provider = self._ensure_provider()
        if not hasattr(provider, "ssh_key_manager"):
            raise AttributeError(
                f"Provider {provider.__class__.__name__} doesn't support SSH key management"
            )
        # Ensure project scoping is applied so platform APIs that require
        # project context (e.g., SSH key creation) do not fail with
        # validation errors like "project: Field is required".
        manager = provider.ssh_key_manager
        try:
            # Only set if not already scoped to avoid unnecessary calls.
            if getattr(manager, "project_id", None) is None:
                # Provider exposes a project_id property that resolves lazily.
                manager.project_id = provider.project_id  # type: ignore[attr-defined]
        except Exception:
            # Do not hard-fail here; individual operations will surface errors
            # with richer context if scoping is still missing.
            pass

        return manager

    def close(self) -> None:
        """Release provider resources (idempotent)."""
        if self._provider and hasattr(self._provider, "close"):
            self._provider.close()

    def __enter__(self) -> Flow:
        """Enter context manager (returns self)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager and close resources; do not suppress exceptions."""
        self.close()
        # Do not suppress exceptions
        return False


# Clean SDK facade for Flow - simple for 90%, powerful for 10%


class Client:
    """Clean SDK facade for Flow - simple for 90%, powerful for 10%.

    This client provides a simplified interface to Flow's functionality,
    abstracting away complexity while maintaining power user access.

    Examples:
        Simple usage:
            >>> client = Client()
            >>> task = client.run("python train.py", gpu="a100")
            >>> status = client.status(task.id)

        Power user access:
            >>> provider = client.provider_port()  # Direct provider access
    """

    def __init__(self, provider: str = "local", **provider_kwargs):
        """Initialize Flow client with specified provider.

        Args:
            provider: Provider name (local, mithril, mock)
            **provider_kwargs: Provider-specific configuration
        """
        self._provider = self._resolve_provider(provider, **provider_kwargs)

        # Initialize use cases
        from flow.application.cancel_task import CancelTaskUseCase
        from flow.application.query_status import QueryStatusUseCase
        from flow.application.reserve_capacity import ReserveCapacityUseCase
        from flow.application.run_task import RunService

        self._run_service = RunService(self._provider)
        self._cancel_use_case = CancelTaskUseCase(self._provider)
        self._status_use_case = QueryStatusUseCase(self._provider)
        self._reserve_use_case = ReserveCapacityUseCase(self._provider)

    def run(
        self,
        command: str | list[str] | TaskSpec | TaskConfig,
        *,
        gpu: Optional[str] = None,
        cpus: Optional[int] = None,
        memory_gb: Optional[int] = None,
        wait: bool = False,
        **kwargs,
    ) -> Task:
        """Run a task with specified resources.

        Args:
            command: Command to run or task specification
            gpu: GPU type (e.g., "a100", "v100")
            cpus: Number of CPUs
            memory_gb: Memory in GB
            wait: Wait for task completion
            **kwargs: Additional task configuration

        Returns:
            Task handle for monitoring and management
        """
        from flow.application.run_task import RunRequest
        from flow.domain.ir.spec import ResourceSpec, TaskSpec

        # Convert to TaskSpec if needed
        if isinstance(command, str):
            # Interpret `gpu` as GPU type string; default to 1 GPU when provided
            gpus = 1 if gpu else 0
            spec = TaskSpec(
                command=[command],
                resources=ResourceSpec(
                    gpus=gpus, gpu_type=gpu, cpus=cpus or 4, memory_gb=memory_gb or 16
                ),
                **kwargs,
            )
        elif isinstance(command, TaskConfig):
            spec = command.to_spec()
        else:
            spec = command

        # Execute through use case
        request = RunRequest(spec=spec)
        response = self._run_service.run(request)

        task = Task(id=response.handle.task_id, status=TaskStatus.PENDING, handle=response.handle)

        if wait:
            task = self._wait_for_task(task)

        return task

    def status(self, task_id: Optional[str] = None) -> list[Task]:
        """Get status of task(s).

        Args:
            task_id: Specific task ID or None for all tasks

        Returns:
            List of tasks with current status
        """
        from flow.application.query_status import QueryStatusRequest

        request = QueryStatusRequest(task_id=task_id, all_tasks=task_id is None)
        response = self._status_use_case.execute(request)

        return [
            Task(
                id=info.task_id,
                status=info.status,
                instance_type=info.instance_type,
                instance_ip=info.instance_ip,
                created_at=info.created_at,
                updated_at=info.updated_at,
            )
            for info in response.tasks
        ]

    def cancel(self, task_id: str, force: bool = False) -> bool:
        """Cancel a running task.

        Args:
            task_id: Task to cancel
            force: Force termination

        Returns:
            True if cancelled successfully
        """
        from flow.application.cancel_task import CancelTaskRequest

        request = CancelTaskRequest(task_id=task_id, force=force)
        response = self._cancel_use_case.execute(request)
        return response.success

    def logs(self, task_id: str, follow: bool = False) -> Iterator[str]:
        """Stream task logs.

        Args:
            task_id: Task to get logs for
            follow: Follow log output

        Yields:
            Log lines
        """
        return self._provider.get_logs(task_id, follow=follow)

    def ssh(self, task_id: str) -> str:
        """Get SSH command for task.

        Args:
            task_id: Task to connect to

        Returns:
            SSH command string
        """
        task = self.status(task_id)[0]
        return self._provider.get_ssh_command(task)

    def reserve(self, gpu: str, duration_hours: int = 1, auto_renew: bool = False) -> str:
        """Reserve GPU capacity.

        Args:
            gpu: GPU type to reserve
            duration_hours: Reservation duration
            auto_renew: Auto-renew reservation

        Returns:
            Reservation ID
        """
        from flow.application.reserve_capacity import ReserveCapacityRequest
        from flow.domain.ir.spec import ResourceSpec as Resources

        request = ReserveCapacityRequest(
            resources=Resources(gpu=gpu), duration_hours=duration_hours, auto_renew=auto_renew
        )
        response = self._reserve_use_case.execute(request)

        if not response.success:
            raise RuntimeError(f"Reservation failed: {response.error_message}")

        return response.reservation.reservation_id

    def volumes(self) -> list[Volume]:
        """List available volumes.

        Returns:
            List of volumes
        """
        return self._provider.list_volumes()

    # Power user escape hatch
    def provider_port(self):
        """Get direct access to provider port (power users).

        Returns:
            Provider port for advanced operations
        """
        return self._provider

    def _resolve_provider(self, provider: str, **kwargs):
        """Resolve provider by name using entry points.

        Args:
            provider: Provider name
            **kwargs: Provider configuration

        Returns:
            Provider instance
        """
        import importlib.metadata

        # Discover providers via entry points
        entry_points = importlib.metadata.entry_points()
        provider_eps = entry_points.get("flow.providers", [])

        for ep in provider_eps:
            if ep.name == provider:
                provider_class = ep.load()
                return provider_class(**kwargs)

        # Fallback to factory
        from flow.adapters.providers.factory import create_provider

        return create_provider(provider, **kwargs)

    def _wait_for_task(self, task: Task, timeout: int = 3600) -> Task:
        """Wait for task to complete.

        Args:
            task: Task to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Updated task with final status
        """
        import time

        start = time.time()
        while time.time() - start < timeout:
            status = self.status(task.id)[0]
            if status.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return status
            time.sleep(5)

        raise TimeoutError(f"Task {task.id} did not complete within {timeout} seconds")
