"""Base provider adapter implementing the provider protocol.

This module provides a base class that all provider adapters should extend
to ensure consistent behavior and reduce code duplication.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from flow.adapters.providers.base import ProviderCapabilities, ProviderInfo
from flow.sdk.models import (
    AvailableInstance,
    Instance,
    Reservation,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
)

logger = logging.getLogger(__name__)


class ProviderAdapter(ABC):
    """Abstract base class for provider adapters.

    This class implements the ProviderProtocol and provides common
    functionality that all providers can use. Specific providers should
    extend this class and implement the abstract methods.
    """

    def __init__(self, name: str, capabilities: ProviderCapabilities | None = None):
        """Initialize the provider adapter.

        Args:
            name: Provider name (e.g., "mithril", "local")
            capabilities: Provider capabilities (defaults to basic capabilities)
        """
        self.name = name
        self.capabilities = capabilities or ProviderCapabilities()
        self._logger = logging.getLogger(f"{__name__}.{name}")

    @property
    def provider_info(self) -> ProviderInfo:
        """Get provider information."""
        return ProviderInfo(
            name=self.name,
            display_name=self.name.title(),
            description=f"{self.name.title()} provider adapter",
            capabilities=self.capabilities,
        )

    # ---- Abstract methods that providers must implement ----

    @abstractmethod
    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Task:
        """Submit a task for execution."""
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        """Get task details by ID."""
        ...

    @abstractmethod
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current task status."""
        ...

    @abstractmethod
    def list_tasks(
        self,
        status: str | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List tasks with optional filtering."""
        ...

    @abstractmethod
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task."""
        ...

    @abstractmethod
    def cancel_task(self, task_id: str) -> None:
        """Cancel a task."""
        ...

    @abstractmethod
    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get task logs."""
        ...

    @abstractmethod
    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
        follow: bool = True,
        tail: int = 10,
    ) -> Iterable[str]:
        """Stream task logs."""
        ...

    @abstractmethod
    def find_instances(
        self, requirements: dict[str, Any], limit: int = 10
    ) -> list[AvailableInstance]:
        """Find available instances matching requirements."""
        ...

    @abstractmethod
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str = "block",
        region: str | None = None,
    ) -> Volume:
        """Create a new volume."""
        ...

    @abstractmethod
    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume."""
        ...

    @abstractmethod
    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes."""
        ...

    # ---- Default implementations (can be overridden) ----

    def parse_catalog_instance(self, instance: Instance) -> dict[str, Any]:
        """Parse instance catalog data.

        Default implementation returns basic instance info.
        Providers can override for custom parsing logic.
        """
        return {
            "id": instance.id,
            "name": instance.name,
            "status": instance.status,
            "instance_type": getattr(instance, "instance_type", "unknown"),
            "region": getattr(instance, "region", "unknown"),
        }

    def is_volume_id(self, identifier: str) -> bool:
        """Check if identifier is a volume ID.

        Default implementation checks for common volume ID patterns.
        Providers should override with provider-specific logic.
        """
        # Common patterns: vol_*, volume-*, starts with vol
        volume_patterns = ["vol_", "vol-", "volume-", "volume_"]
        return any(identifier.startswith(pattern) for pattern in volume_patterns)

    def mount_volume(self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume") -> bool:
        """Mount a volume to a task.

        Default implementation returns False (not supported).
        Providers should override if they support volume mounting.
        """
        self._logger.warning(f"Volume mounting not implemented for {self.name} provider")
        return False

    def upload_file(self, task_id: str, local_path: Any, remote_path: str = "~") -> bool:
        """Upload a file to a task.

        Default implementation returns False (not supported).
        Providers should override if they support file upload.
        """
        self._logger.warning(f"File upload not implemented for {self.name} provider")
        return False

    def upload_directory(
        self,
        task_id: str,
        local_dir: Any,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Upload a directory to a task.

        Default implementation returns False (not supported).
        Providers should override if they support directory upload.
        """
        self._logger.warning(f"Directory upload not implemented for {self.name} provider")
        return False

    def download_file(self, task_id: str, remote_path: str, local_path: Any) -> bool:
        """Download a file from a task.

        Default implementation returns False (not supported).
        Providers should override if they support file download.
        """
        self._logger.warning(f"File download not implemented for {self.name} provider")
        return False

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Any,
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Download a directory from a task.

        Default implementation returns False (not supported).
        Providers should override if they support directory download.
        """
        self._logger.warning(f"Directory download not implemented for {self.name} provider")
        return False

    def create_reservation(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
    ) -> Reservation:
        """Create a reservation.

        Default implementation raises NotImplementedError.
        Providers should override if they support reservations.
        """
        raise NotImplementedError(f"Reservations not supported by {self.name} provider")

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        """List reservations.

        Default implementation returns empty list.
        Providers should override if they support reservations.
        """
        if self.capabilities.supports_reservations:
            self._logger.warning(f"Reservation listing not implemented for {self.name} provider")
        return []

    def get_reservation(self, reservation_id: str) -> Reservation:
        """Get reservation details.

        Default implementation raises NotImplementedError.
        Providers should override if they support reservations.
        """
        raise NotImplementedError(f"Reservations not supported by {self.name} provider")

    # ---- Utility methods ----

    def validate_task_config(self, config: TaskConfig) -> tuple[bool, str]:
        """Validate task configuration against provider capabilities.

        Args:
            config: Task configuration to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check instance count limits
        if (
            self.capabilities.max_instances_per_task
            and config.num_instances > self.capabilities.max_instances_per_task
        ):
            return False, (
                f"Too many instances requested: {config.num_instances} > "
                f"{self.capabilities.max_instances_per_task}"
            )

        # Check SSH key requirements
        if self.capabilities.requires_ssh_keys and not config.ssh_keys:
            return False, "SSH keys are required for this provider"

        # Check multi-node support
        if config.num_instances > 1 and not self.capabilities.supports_multi_node:
            return False, "Multi-node tasks not supported by this provider"

        return True, ""

    def log_operation(self, operation: str, **kwargs):
        """Log provider operations for debugging.

        Args:
            operation: Operation name
            **kwargs: Additional context to log
        """
        context = " ".join(f"{k}={v}" for k, v in kwargs.items())
        self._logger.debug(f"[{self.name}] {operation} {context}")


class ProviderAdapterError(Exception):
    """Base exception for provider adapter errors."""

    def __init__(self, message: str, provider: str | None = None):
        super().__init__(message)
        self.provider = provider


class ProviderNotSupportedError(ProviderAdapterError):
    """Raised when a provider doesn't support a requested operation."""

    pass


class ProviderConfigurationError(ProviderAdapterError):
    """Raised when provider configuration is invalid."""

    pass
