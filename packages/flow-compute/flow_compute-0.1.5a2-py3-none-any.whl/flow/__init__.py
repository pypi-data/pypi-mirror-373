"""Flow SDK - GPU compute made simple.

This module exposes a small, stable facade and lazily imports heavier
submodules on first attribute access to keep cold import time low.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

# Version (single source of truth)
from flow._version import __version__

VERSION = __version__

# Provider-agnostic constants
DEFAULT_REGION = "us-central1-b"  # Default region (Mithril default)
DEFAULT_PROVISION_MINUTES = 20  # Typical provision time for GPU instances
# Default estimated duration shown in CLI progress for code uploads.
# Keep this central so UI estimates can be tuned in one place.
# Note: expressed in minutes; 0.333… min = 20 seconds.
DEFAULT_UPLOAD_ESTIMATED_MINUTES = 20 / 60
# Estimated time shown for instance allocation steps
DEFAULT_ALLOCATION_ESTIMATED_SECONDS = 120

_EXPORTS: dict[str, tuple[str, str]] = {
    # Main API - New clean facade
    "Client": ("flow.sdk.client", "Flow"),
    # Legacy symbols removed; use flow.sdk directly
    # Models
    "TaskConfig": ("flow.sdk.models", "TaskConfig"),
    "TaskSpec": ("flow.sdk.models", "TaskSpec"),
    "Task": ("flow.sdk.models", "Task"),
    "Resources": ("flow.sdk.models", "Resources"),
    "RunParams": ("flow.sdk.models", "RunParams"),
    "Volume": ("flow.sdk.models", "Volume"),
    "VolumeSpec": ("flow.sdk.models", "VolumeSpec"),
    "TaskStatus": ("flow.sdk.models", "TaskStatus"),
    "InstanceType": ("flow.sdk.models", "InstanceType"),
    "User": ("flow.sdk.models", "User"),
    "Retries": ("flow.sdk.models", "Retries"),
    # Decorators
    "decorators": ("flow.sdk", "decorators"),
    # Secrets
    "Secret": ("flow.sdk.secrets", "Secret"),
    # Errors
    "FlowError": ("flow.errors", "FlowError"),
    "AuthenticationError": ("flow.errors", "AuthenticationError"),
    "ResourceNotFoundError": ("flow.errors", "ResourceNotFoundError"),
    "TaskNotFoundError": ("flow.errors", "TaskNotFoundError"),
    "ValidationError": ("flow.errors", "ValidationError"),
    "APIError": ("flow.errors", "APIError"),
    "ValidationAPIError": ("flow.errors", "ValidationAPIError"),
    "InsufficientBidPriceError": ("flow.errors", "InsufficientBidPriceError"),
    "NetworkError": ("flow.errors", "NetworkError"),
    "TimeoutError": ("flow.errors", "TimeoutError"),
    "ProviderError": ("flow.errors", "ProviderError"),
    "ConfigParserError": ("flow.errors", "ConfigParserError"),
    "ResourceNotAvailableError": ("flow.errors", "ResourceNotAvailableError"),
    "QuotaExceededError": ("flow.errors", "QuotaExceededError"),
    "VolumeError": ("flow.errors", "VolumeError"),
    "TaskExecutionError": ("flow.errors", "TaskExecutionError"),
    "RemoteExecutionError": ("flow.errors", "RemoteExecutionError"),
    "FlowOperationError": ("flow.errors", "FlowOperationError"),
    "InstanceNotReadyError": ("flow.errors", "InstanceNotReadyError"),
    "NameConflictError": ("flow.errors", "NameConflictError"),
}


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError(name)
    module_name, attr = target
    module = import_module(module_name)
    value = getattr(module, attr)
    globals()[name] = value  # cache for future accesses
    return value


def __dir__() -> list[str]:
    return sorted(list(_EXPORTS.keys()) + [k for k in globals() if not k.startswith("_")])


# Convenience functions
def run(task_or_command, **kwargs):
    """Submit task to GPU infrastructure using default Flow client.

    This is a convenience wrapper that creates a Flow instance internally.
    For advanced usage requiring multiple operations, use `with Flow() as flow:`.

    Args:
        task_or_command: TaskConfig, path to YAML file, or command string
        **kwargs: When task_or_command is a string command:
            - instance_type: GPU instance type (e.g., "a100", "8xh100")
            - image: Docker image to use
            - wait: Whether to wait for task to start
            - mounts: Data sources to mount
            - Any other TaskConfig field

    Returns:
        Task: The submitted task object

    Examples:
        >>> import flow
        >>> # Simple command with instance type
        >>> task = flow.run("python train.py", instance_type="a100")
        >>>
        >>> # With Docker image
        >>> task = flow.run("python train.py",
        ...                 instance_type="a100",
        ...                 image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8")
        >>>
        >>> # From TaskConfig
        >>> config = flow.TaskConfig(name="training", instance_type="8xh100",
        ...                          command="python train.py")
        >>> task = flow.run(config)
    """
    from flow.sdk.client import Flow
    from flow.sdk.models import TaskConfig

    # Extract Flow.run() specific args
    wait = kwargs.pop("wait", False)
    mounts = kwargs.pop("mounts", None)

    # If task_or_command is a string and not a file path, treat it as a command
    if isinstance(task_or_command, str) and not task_or_command.endswith((".yaml", ".yml")):
        # Check if it looks like a file path
        from pathlib import Path

        if not Path(task_or_command).exists():
            # It's a command string, create TaskConfig with it
            config = TaskConfig(command=task_or_command, **kwargs)
            with Flow() as client:
                return client.run(config, wait=wait, mounts=mounts)

    # Otherwise, pass through as-is (TaskConfig or YAML path)
    with Flow() as client:
        return client.run(task_or_command, wait=wait, mounts=mounts)


__all__ = sorted(
    [
        *_EXPORTS.keys(),
        "run",
        "DEFAULT_REGION",
        "DEFAULT_PROVISION_MINUTES",
        "DEFAULT_UPLOAD_ESTIMATED_MINUTES",
        "DEFAULT_ALLOCATION_ESTIMATED_SECONDS",
        "__version__",
    ]
)
