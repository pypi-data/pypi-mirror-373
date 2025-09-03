"""MithrilProvider - thin facade that delegates to domain facets.

This is the main provider class that implements IProvider interface.
All actual logic is delegated to specialized facets for clean separation of concerns.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from flow.adapters.providers.adapter import ProviderAdapter
from flow.adapters.providers.base import PricingModel, ProviderCapabilities
from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext
from flow.adapters.providers.builtin.mithril.provider.facets import (
    ComputeFacet,
    LogsFacet,
    MetaFacet,
    ReservationsFacet,
    SelectionFacet,
    SSHFacet,
    StorageFacet,
    TasksFacet,
)
from flow.application.config.config import Config
from flow.protocols.http import HttpClientProtocol
from flow.protocols.logging import LoggingProtocol
from flow.protocols.metrics import MetricsProtocol
from flow.protocols.remote_operations import RemoteOperationsProtocol as IRemoteOperations

# Legacy IProvider import removed - now using ProviderAdapter
from flow.sdk.models import (
    AvailableInstance,
    Instance,
    Reservation,
    Task,
    TaskConfig,
    TaskStatus,
    User,
    Volume,
)

# Prefer injected port; keep module logger for fallback
logger = logging.getLogger(__name__)


class MithrilProvider(ProviderAdapter):
    """Mithril provider - thin facade delegating to specialized facets.

    This class extends ProviderAdapter and provides a clean public API by
    delegating all operations to domain-specific facets. The provider itself
    contains no business logic, only delegation and interface compliance.
    """

    def __init__(
        self,
        config: Config,
        http_client: HttpClientProtocol | None = None,
        startup_script_builder: Any | None = None,
        *,
        logger: LoggingProtocol | None = None,
        metrics: MetricsProtocol | None = None,
    ):
        """Initialize provider with context and facets.

        Args:
            config: Provider configuration
            http_client: Optional HTTP client override
            startup_script_builder: Optional startup script builder override
        """
        # Define Mithril capabilities
        from flow.adapters.providers.builtin.mithril.core.constants import (
            SUPPORTED_REGIONS as _SUPPORTED_REGIONS,
        )

        capabilities = ProviderCapabilities(
            supports_spot_instances=True,
            supports_on_demand=True,
            supports_multi_node=True,
            supports_attached_storage=True,
            supports_shared_storage=False,
            storage_types=["volume", "block"],
            requires_ssh_keys=True,
            supports_console_access=False,
            pricing_model=PricingModel.MARKET,
            supports_reservations=True,
            supported_regions=list(_SUPPORTED_REGIONS),
            max_instances_per_task=256,
            max_storage_per_instance_gb=16384,
            supports_custom_images=True,
            supports_gpu_passthrough=True,
            supports_live_migration=False,
        )

        # Initialize parent class
        super().__init__(name="mithril", capabilities=capabilities)

        # Build context with all dependencies
        self.ctx = MithrilContext.build(
            config=config, http_client=http_client, startup_script_builder=startup_script_builder
        )

        # Initialize facets
        self.compute = ComputeFacet(self.ctx)
        self.selection = SelectionFacet(self.ctx)
        self.tasks = TasksFacet(self.ctx)
        self.ssh = SSHFacet(self.ctx)
        self.logs = LogsFacet(self.ctx, get_remote_ops=self.ssh.get_remote_operations)
        self.storage = StorageFacet(self.ctx)
        self.reservations = ReservationsFacet(self.ctx)
        self.meta = MetaFacet(self.ctx)

        # Ensure CodeUploadService is provider-backed (not context-backed)
        try:
            from flow.adapters.providers.builtin.mithril.domain.code_upload import (
                CodeUploadService as _CodeUploadService,
            )

            # Override the context-built service (constructed with context) to use provider
            self.ctx.code_upload = _CodeUploadService(self)  # type: ignore[assignment]
        except Exception:
            pass

        # Optional ports
        self._logger: LoggingProtocol | None = logger
        self._metrics: MetricsProtocol | None = metrics

    # Ports setters for factory injection
    def set_logger(self, logger: LoggingProtocol) -> None:
        self._logger = logger

    def set_metrics(self, metrics: MetricsProtocol) -> None:
        self._metrics = metrics

    # ========== Properties ==========

    @property
    def api_url(self) -> str:
        """Get API URL."""
        return self.ctx.mithril_config.api_url

    @property
    def project_id(self) -> str:
        """Get current project ID."""
        return self.ctx.get_project_id()

    # Back-compat for tests expecting provider.project_resolver attribute
    @property
    def project_resolver(self):  # type: ignore[override]
        return getattr(self.ctx, "project_resolver", None)

    @project_resolver.setter
    def project_resolver(self, value):  # type: ignore[override]
        self.ctx.project_resolver = value

    @project_resolver.deleter
    def project_resolver(self):  # type: ignore[override]
        if hasattr(self.ctx, "project_resolver"):
            delattr(self.ctx, "project_resolver")

    # ========== Factory Method ==========

    @classmethod
    def from_config(cls, config: Config) -> MithrilProvider:
        """Create provider from configuration.

        Args:
            config: Provider configuration

        Returns:
            Configured provider instance
        """
        return cls(config)

    # ========== Compute Operations ==========

    def normalize_instance_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize GPU request to a provider-ready shape.

        Returns a tuple of (instance_type, num_instances, warning).
        Backwards-compatible with facets returning dicts by converting them
        to the canonical tuple and applying simple packaging heuristics.
        """
        try:
            req = self.selection.normalize_instance_request(gpu_count, gpu_type)
        except Exception:
            req = None

        # Extract normalized GPU type when available
        gt: str | None = None
        if isinstance(req, dict):
            gt = (req.get("gpu_type") or gpu_type or "a100") if req is not None else None
        else:
            gt = gpu_type or "a100"

        # Packaging heuristic: prefer 8x, then 4x, then 2x
        gt = str(gt or "a100").lower()
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return (f"8x{gt}", gpu_count // 8, None)
        if gpu_count >= 4 and gpu_count % 4 == 0:
            return (f"4x{gt}", gpu_count // 4, None)
        if gpu_count >= 2 and gpu_count % 2 == 0:
            return (f"2x{gt}", gpu_count // 2, None)
        return (gt, gpu_count, None)

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Prepare task configuration with defaults."""
        return self.compute.prepare_task_config(config)

    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Task:
        """Submit a new task."""
        return self.compute.submit_task(
            instance_type, config, volume_ids, allow_partial_fulfillment, chunk_size
        )

    def find_optimal_auction(self, config: TaskConfig, use_catalog: bool = True) -> Any:
        """Find optimal auction for task configuration."""
        return self.compute.find_optimal_auction(config, use_catalog)

    def package_local_code(self, config: TaskConfig) -> TaskConfig:
        """Package local code for upload."""
        return self.compute.package_local_code(config)

    # ========== Task Operations ==========

    def get_task(self, task_id: str) -> Task:
        """Get task details."""
        return self.tasks.get_task(task_id)

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get task status."""
        return self.tasks.get_task_status(task_id)

    def list_tasks(
        self, status: str | None = None, limit: int = 100, force_refresh: bool = False
    ) -> list[Task]:
        """List tasks with optional filtering."""
        return self.tasks.list_tasks(status, limit, force_refresh)

    def list_active_tasks(self, limit: int = 100) -> list[Task]:
        """List active tasks."""
        return self.tasks.list_active_tasks(limit)

    def stop_task(self, task_id: str) -> bool:
        """Stop a running task."""
        return self.tasks.stop_task(task_id)

    def cancel_task(self, task_id: str) -> None:
        """Cancel a task."""
        return self.tasks.cancel_task(task_id)

    def get_task_instances(self, task_id: str) -> list[Instance]:
        """Get instances for a task."""
        return self.tasks.get_task_instances(task_id)

    # ========== Log Operations ==========

    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get recent logs for a task."""
        return self.logs.get_task_logs(task_id, tail, log_type)

    def stream_task_logs(
        self, task_id: str, log_type: str = "stdout", follow: bool = True, tail: int = 10
    ) -> Iterator[str]:
        """Stream logs from a task."""
        return self.logs.stream_task_logs(task_id, log_type, follow, tail)

    # ========== SSH Operations ==========

    def get_task_ssh_connection_info(self, task_id: str) -> tuple[Path | None, str]:
        """Get SSH connection info for a task."""
        return self.ssh.get_task_ssh_connection_info(task_id)

    def resolve_ssh_endpoint(self, task_id: str, node: int | None = None) -> tuple[str, int]:
        """Resolve SSH endpoint for a task."""
        return self.ssh.resolve_ssh_endpoint(task_id, node)

    def get_remote_operations(self) -> IRemoteOperations | None:
        """Get remote operations handler."""
        return self.ssh.get_remote_operations()

    def get_ssh_tunnel_manager(self):
        """Get SSH tunnel manager."""
        return self.ssh.get_ssh_tunnel_manager()

    def get_transport(self):
        """Get transport helper."""
        return self.ssh.get_transport()

    # Back-compat for tests expecting private attributes
    @property
    def _api_client(self):  # type: ignore[override]
        return getattr(self.ctx, "api", None)

    @_api_client.setter
    def _api_client(self, value):  # type: ignore[override]
        self.ctx.api = value

    @_api_client.deleter
    def _api_client(self):  # type: ignore[override]
        if hasattr(self.ctx, "api"):
            delattr(self.ctx, "api")

    @property
    def _task_service(self):  # type: ignore[override]
        return getattr(self.ctx, "task_service", None)

    @_task_service.setter
    def _task_service(self, value):  # type: ignore[override]
        self.ctx.task_service = value

    @_task_service.deleter
    def _task_service(self):  # type: ignore[override]
        if hasattr(self.ctx, "task_service"):
            delattr(self.ctx, "task_service")

    # ========== Capabilities / Console ==========
    def get_web_base_url(self) -> str | None:
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import MITHRIL_WEB_BASE_URL

            return MITHRIL_WEB_BASE_URL
        except Exception:
            return None

    # ========== Storage Operations ==========

    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume:
        """Create a new volume."""
        return self.storage.create_volume(size_gb, name, interface, region)

    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume."""
        return self.storage.delete_volume(volume_id)

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes in the project."""
        return self.storage.list_volumes(limit)

    def mount_volume(self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume") -> bool:
        """Mount a volume to a running task."""
        return self.storage.mount_volume(task_id, volume_id, mount_path)

    def is_volume_id(self, identifier: str) -> bool:
        """Check if a string is a volume ID."""
        return self.storage.is_volume_id(identifier)

    def upload_file(self, task_id: str, local_path: Path, remote_path: str = "~") -> bool:
        """Upload a file to a task."""
        return self.storage.upload_file(task_id, local_path, remote_path)

    def download_file(self, task_id: str, remote_path: str, local_path: Path) -> bool:
        """Download a file from a task."""
        return self.storage.download_file(task_id, remote_path, local_path)

    def upload_directory(
        self,
        task_id: str,
        local_dir: Path,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Upload a directory to a task."""
        return self.storage.upload_directory(task_id, local_dir, remote_dir, exclude_patterns)

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Path,
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Download a directory from a task."""
        return self.storage.download_directory(task_id, remote_dir, local_dir, exclude_patterns)

    # ========== Reservation Operations ==========

    def create_reservation(
        self, instance_type: str, config: TaskConfig, volume_ids: list[str] | None = None
    ) -> Reservation:
        """Create a new reservation."""
        return self.reservations.create_reservation(instance_type, config, volume_ids)

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        """List reservations."""
        return self.reservations.list_reservations(params)

    def get_reservation(self, reservation_id: str) -> Reservation:
        """Get a specific reservation."""
        return self.reservations.get_reservation(reservation_id)

    def get_reservation_availability(
        self,
        instance_type: str,
        num_nodes: int,
        duration_hours: float,
        *,
        region: str | None = None,
        earliest_start_time: str | None = None,
        latest_end_time: str | None = None,
        mode: str | None = None,
    ) -> list[dict[str, Any]]:
        """Check availability for a reservation."""
        return self.reservations.get_reservation_availability(
            instance_type,
            num_nodes,
            duration_hours,
            region=region,
            earliest_start_time=earliest_start_time,
            latest_end_time=latest_end_time,
            mode=mode,
        )

    # ========== Metadata Operations ==========

    def get_user(self, user_id: str) -> User:
        """Get user information."""
        return self.meta.get_user(user_id)

    def get_user_teammates(self, user_id: str) -> Any:
        """Get teammates for a user."""
        return self.meta.get_user_teammates(user_id)

    def get_projects(self) -> list[dict[str, Any]]:
        """Get list of projects."""
        return self.meta.get_projects()

    def get_instance_types(self, region: str | None = None) -> list[dict[str, Any]]:
        """Get available instance types."""
        return self.meta.get_instance_types(region)

    def resolve_instance_type(self, user_spec: str) -> str:
        """Resolve user-friendly instance spec to provider ID."""
        return self.meta.resolve_instance_type(user_spec)

    def get_ssh_keys(self) -> list[dict[str, Any]]:
        """Get SSH keys for the project."""
        return self.meta.get_ssh_keys()

    def create_ssh_key(self, name: str, public_key: str) -> dict[str, Any]:
        """Create a new SSH key."""
        return self.meta.create_ssh_key(name, public_key)

    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete an SSH key."""
        return self.meta.delete_ssh_key(key_id)

    def get_capabilities(self) -> dict[str, Any]:
        """Get provider capabilities."""
        return self.meta.get_capabilities()

    # ========== Convenience (CLI-facing) ==========
    def ensure_default_ssh_key(self) -> str | None:
        """Ensure a default SSH key exists; create one if needed.

        Returns the key_id when created, or None if already present or unavailable.
        """
        try:
            keys = self.get_ssh_keys()
            if isinstance(keys, list) and keys:
                return None
            # Create a key from local public key if available
            from pathlib import Path as _Path

            pub = None
            for candidate in [
                _Path.home() / ".ssh" / "id_ed25519.pub",
                _Path.home() / ".ssh" / "id_rsa.pub",
            ]:
                try:
                    if candidate.exists():
                        pub = candidate.read_text().strip()
                        break
                except Exception:
                    continue
            if not pub:
                return None
            created = self.create_ssh_key("flow-default", pub)
            if isinstance(created, dict):
                return created.get("id") or created.get("key_id")
            return None
        except Exception:
            return None

    # ========== Instance Discovery ==========

    def find_instances(
        self, requirements: dict[str, Any], limit: int = 10
    ) -> list[AvailableInstance]:
        """Find available instances matching requirements."""
        # Delegate to instance finder service
        from flow.adapters.providers.builtin.mithril.domain.instance_finder import (
            InstanceFinderService,
        )

        finder = InstanceFinderService(self.ctx.api)

        # Resolve instance type if provided
        if "instance_type" in requirements:
            instance_type = requirements["instance_type"]
            if instance_type and not instance_type.startswith("it_"):
                requirements = requirements.copy()
                requirements["instance_type"] = self.ctx.resolve_instance_type(instance_type)

        instances = finder.find_instances(requirements, limit)

        # Convert to AvailableInstance format
        available = []
        for inst in instances:
            if isinstance(inst, AvailableInstance):
                available.append(inst)
            else:
                try:
                    converted = self.tasks.convert_auction_to_available_instance(
                        inst.__dict__ if hasattr(inst, "__dict__") else inst
                    )
                    if converted:
                        available.append(converted)
                except Exception:
                    pass

        return available[:limit]

    def parse_catalog_instance(self, instance: Instance) -> dict[str, Any]:
        """Parse provider instance into catalog dict expected by SDK."""
        from flow.adapters.providers.builtin.mithril.domain.instance_operations import (
            InstanceOperations,
        )

        ops = InstanceOperations(self.ctx.instances, self.ctx.instance_types)
        return ops.parse_catalog_instance(instance)

    # ========== Code Upload Operations ==========

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
        """Upload code to a task with progress and timeout support.

        Delegates to the CodeUploadService to perform an rsync-based transfer
        with optional Rich progress reporting. Signature aligns with the Flow
        client and CLI expectations.
        """
        return self.ctx.code_upload.upload_code_to_task(
            task_id=task_id,
            source_dir=source_dir,
            timeout=timeout,
            console=console,
            target_dir=target_dir,
            progress_reporter=progress_reporter,
            git_incremental=git_incremental,
        )

    def start_background_code_upload(self, task: Task, source_dir: Path | None = None) -> Any:
        """Start background code upload to task.

        Uses the shared CodeTransferManager and configuration to perform a
        background rsync without CLI progress output.
        """
        from flow.adapters.transport.code_transfer import (
            CodeTransferConfig as _Cfg,
        )
        from flow.adapters.transport.code_transfer import (
            CodeTransferManager as _Mgr,
        )

        manager = _Mgr(provider=self, progress_reporter=None)
        cfg = _Cfg(source_dir=source_dir)
        return self.ctx.code_upload.start_background_upload(manager, task, cfg)

    def get_exclude_patterns(self, root: Path | None = None) -> list[str]:
        """Get file patterns to exclude from code upload."""
        return self.ctx.code_upload.build_exclude_patterns(root or Path.cwd())

    # ========== Interface Methods ==========

    def get_init_interface(self) -> Any:
        """Get provider initialization interface.

        Returns a dedicated MithrilInit implementation that conforms to
        ProviderInitProtocol, rather than the provider itself. This aligns
        with the Provider Migration Guide and ensures methods like
        list_projects()/list_ssh_keys() are available to callers such as
        Flow SDK helpers and CLI commands.
        """
        try:
            from flow.adapters.providers.builtin.mithril.init import MithrilInit  # lazy import

            # Pass the configured HTTP client so init operations can make API calls
            return MithrilInit(self.ctx.http)
        except Exception:
            # Fallback to self to avoid breaking callers in constrained envs
            return self

    def get_remote_interface(self) -> Any:
        """Get remote operations interface."""
        return self.ssh.get_remote_operations()

    def get_storage_interface(self) -> Any:
        """Get storage operations interface."""
        return self.storage

    # ========== Pricing Convenience ==========
    def get_market_price(self, instance_type: str, region: str | None = None) -> float | None:
        """Return current market price for a user-specified instance type.

        Args:
            instance_type: User-friendly spec (e.g., "a100", "8xa100")
            region: Optional region override; provider default used when None

        Returns:
            Current market price (USD/hour) or None if unavailable
        """
        try:
            it_id = self.resolve_instance_type(instance_type)
        except Exception:
            it_id = instance_type
        try:
            effective_region = region or getattr(self.ctx.mithril_config, "region", None)
        except Exception:
            effective_region = region or ""

        try:
            return self.ctx.pricing.get_current_market_price(it_id, effective_region)
        except Exception:
            return None

    def close(self) -> None:
        """Close provider and clean up resources."""
        if hasattr(self.ctx, "http") and hasattr(self.ctx.http, "close"):
            self.ctx.http.close()
