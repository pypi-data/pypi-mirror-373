"""Local provider initialization and configuration implementation."""

import os
from pathlib import Path

from flow.adapters.providers.base import ConfigField
from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit


class LocalInit(IProviderInit):
    """Local provider initialization interface implementation.

    Handles configuration for running tasks locally, primarily
    used for development and testing.
    """

    def __init__(self):
        """Initialize local provider init.

        Local provider doesn't need HTTP client since it runs locally.
        """
        pass

    def get_config_fields(self) -> dict[str, ConfigField]:
        """Return local provider configuration field definitions.

        Local provider configuration:
        - Working directory for task execution
        - Maximum parallel tasks
        - Optional resource limits
        """
        default_work_dir = os.path.expanduser("~/.flow/local-tasks")

        return {
            "working_directory": ConfigField(
                description="Working directory for tasks", default=default_work_dir
            ),
            "max_parallel_tasks": ConfigField(description="Maximum parallel tasks", default="4"),
            "enable_gpu": ConfigField(
                description="Enable GPU passthrough (requires local GPU)",
                choices=["true", "false"],
                default="false",
            ),
        }

    def validate_config(self, config: dict[str, str]) -> list[str]:
        """Validate local provider configuration.

        Checks:
        - Working directory exists or can be created
        - Max parallel tasks is a valid number
        - GPU configuration is valid

        Args:
            config: User-provided configuration values

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate working directory
        work_dir = config.get("working_directory", "").strip()
        if not work_dir:
            errors.append("Working directory is required")
        else:
            work_path = Path(work_dir).expanduser()
            if work_path.exists() and not work_path.is_dir():
                errors.append(f"Working directory exists but is not a directory: {work_dir}")
            # Note: We don't error if directory doesn't exist since we can create it

        # Validate max parallel tasks
        max_tasks_str = config.get("max_parallel_tasks", "4").strip()
        try:
            max_tasks = int(max_tasks_str)
            if max_tasks < 1:
                errors.append("Maximum parallel tasks must be at least 1")
            elif max_tasks > 100:
                errors.append("Maximum parallel tasks should not exceed 100")
        except ValueError:
            errors.append(f"Maximum parallel tasks must be a number, got: {max_tasks_str}")

        # Validate GPU setting
        enable_gpu = config.get("enable_gpu", "false").strip().lower()
        if enable_gpu not in ["true", "false"]:
            errors.append("Enable GPU must be 'true' or 'false'")

        return errors

    def list_projects(self) -> list[dict[str, str]]:
        """List projects for local provider.

        Local provider doesn't have projects concept, returns empty list.

        Returns:
            Empty list - projects not applicable for local execution
        """
        return []

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys for local provider.

        Local provider doesn't use SSH keys since tasks run locally.

        Args:
            project_id: Ignored for local provider

        Returns:
            Empty list - SSH keys not applicable for local execution
        """
        return []
