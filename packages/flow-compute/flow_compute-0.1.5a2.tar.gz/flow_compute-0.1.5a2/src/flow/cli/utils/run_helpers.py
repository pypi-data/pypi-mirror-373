"""Helper functions for the run command.

This module contains focused helper functions extracted from the
monolithic _execute method to improve testability and maintainability.
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import suppress

from rich.console import Console

from flow.sdk.models import TaskConfig
from flow.sdk.models.run_params import RunParameters

logger = logging.getLogger(__name__)


class RunHelpers:
    """Collection of focused helper methods for run command."""

    @staticmethod
    def parse_positionals(
        config_file: str | None, extra_args: tuple[str, ...], command: str | None
    ) -> tuple[str | None, list[str] | None]:
        """Parse command from positional arguments.

        Returns:
            Tuple of (config_file, command_tokens)
        """
        inline_cmd_tokens = None

        if extra_args:
            # Reconstruct command when user passed '--' and Click captured tokens
            combined = []
            if config_file:
                if not RunHelpers.looks_like_config_file(config_file):
                    combined.append(config_file)
                    config_file = None
            combined.extend(list(extra_args))
            inline_cmd_tokens = combined or None
            if inline_cmd_tokens:
                config_file = None

        # Fallback: treat single token as command if it looks like one
        if not inline_cmd_tokens and config_file and not command:
            if not os.path.exists(config_file) and RunHelpers.looks_like_command(config_file):
                inline_cmd_tokens = config_file.split()
                config_file = None

        return config_file, inline_cmd_tokens

    @staticmethod
    def looks_like_config_file(path: str) -> bool:
        """Check if path looks like a config file."""
        lower = path.lower()
        return lower.endswith((".yaml", ".yml", ".slurm", ".sbatch")) or os.path.exists(path)

    @staticmethod
    def looks_like_command(text: str) -> bool:
        """Check if text looks like a command."""
        common_cmds = ("python", "bash", "sh", "./", "nvidia-smi", "echo", "env", "hostname")
        return " " in text or any(text.startswith(cmd) for cmd in common_cmds)

    @staticmethod
    def detect_slurm_from_path(path: str, explicit: bool = False) -> bool:
        """Detect if file is a SLURM script."""
        if explicit:
            return True

        lower = path.lower()
        if lower.endswith((".slurm", ".sbatch")):
            return True

        if os.path.exists(path):
            with suppress(IOError, UnicodeDecodeError):
                with open(path) as f:
                    head = f.read(4096)
                    if "#SBATCH" in head:
                        return True
        return False

    @staticmethod
    def apply_cli_overrides(config: TaskConfig, params: RunParameters) -> TaskConfig:
        """Apply CLI parameter overrides to configuration.

        Args:
            config: Base configuration
            params: Run parameters with overrides

        Returns:
            Updated configuration
        """
        updates = {}

        # Instance overrides
        if params.instance.region:
            updates["region"] = params.instance.region
        if params.instance.priority:
            updates["priority"] = params.instance.priority
        if params.instance.max_price_per_hour is not None:
            updates["max_price_per_hour"] = params.instance.max_price_per_hour
        if params.instance.num_instances != 1:
            updates["num_instances"] = params.instance.num_instances
        if params.instance.distributed_mode:
            updates["distributed_mode"] = params.instance.distributed_mode

        # Environment overrides
        if params.execution.environment:
            merged_env = dict(getattr(config, "env", {}) or {})
            merged_env.update(params.execution.environment)
            updates["env"] = merged_env
            # Back-compat: also set environment attribute
            with suppress(Exception):
                updates["environment"] = merged_env

        # Port overrides
        if params.execution.ports:
            updates["ports"] = list(params.execution.ports)

        return config.model_copy(update=updates) if updates else config

    @staticmethod
    def apply_upload_overrides(config: TaskConfig, params: RunParameters) -> TaskConfig:
        """Apply upload-related overrides to configuration.

        Args:
            config: Base configuration
            params: Run parameters with upload settings

        Returns:
            Updated configuration
        """
        updates = {}

        if params.upload.strategy != "auto":
            updates["upload_strategy"] = params.upload.strategy
            updates["upload_timeout"] = params.upload.timeout
        elif params.upload.timeout != 600:
            updates["upload_timeout"] = params.upload.timeout

        if params.upload.code_root:
            updates["code_root"] = str(params.upload.code_root)

        return config.model_copy(update=updates) if updates else config

    @staticmethod
    def display_configs_and_mounts(
        config: TaskConfig | None,
        configs: list[TaskConfig] | None,
        params: RunParameters,
        console: Console,
    ) -> None:
        """Display configuration and mount information.

        Args:
            config: Single task config
            configs: Array of configs (SLURM)
            params: Run parameters
            console: Rich console for output
        """
        if params.execution.output_json:
            return

        from flow.cli.commands.utils import display_config

        if configs and len(configs) > 1:
            # SLURM array
            console.print(f"[bold]SLURM array detected[/bold]: {len(configs)} tasks")
            display_config(
                {"template": True, **configs[0].model_dump()}, show_pricing=False, compact=True
            )
        elif config or (configs and len(configs) == 1):
            cfg = config if config else configs[0]
            display_config(
                cfg.model_dump(),
                show_pricing=params.display.show_pricing,
                compact=params.display.compact,
            )

        # Display mounts if present
        if params.execution.mounts:
            console.print("\n[bold]Mounts:[/bold]")
            for target, source in params.execution.mounts.items():
                console.print(f"  {target} → {source}")

    @staticmethod
    def emit_dry_run_output(
        config: TaskConfig | None,
        configs: list[TaskConfig] | None,
        params: RunParameters,
        console: Console,
    ) -> None:
        """Output dry run results.

        Args:
            config: Single task config
            configs: Array of configs
            params: Run parameters
            console: Rich console
        """
        if params.execution.output_json:
            result = {}
            if configs:
                result = {"status": "valid", "configs": [c.model_dump() for c in configs]}
            else:
                result = {"status": "valid", "config": config.model_dump()}
            if params.execution.mounts:
                result["mounts"] = params.execution.mounts
            console.print(json.dumps(result))
        else:
            from flow.cli.utils.theme_manager import theme_manager

            success_color = theme_manager.get_color("success")

            if configs and len(configs) > 1:
                msg = f"{len(configs)} configurations are valid"
            else:
                msg = "Configuration is valid"

            console.print(f"\n[{success_color}]✓[/{success_color}] {msg}")

    @staticmethod
    def preflight_ssh_keys(config: TaskConfig) -> list[str]:
        """Validate and return effective SSH keys.

        Args:
            config: Task configuration

        Returns:
            List of effective SSH keys

        Raises:
            ValueError: If no SSH keys are configured
        """
        effective_keys = []

        # Task-level keys have highest priority
        if getattr(config, "ssh_keys", None):
            effective_keys = list(config.ssh_keys)

        # Environment variable override
        if not effective_keys:
            env_keys = os.getenv("MITHRIL_SSH_KEYS")
            if env_keys:
                parsed = [k.strip() for k in env_keys.split(",") if k.strip()]
                if parsed:
                    effective_keys = parsed

        # Provider config fallback
        if not effective_keys:
            with suppress(ImportError, Exception):
                # Use the centralized config (env + ~/.flow/config.yaml)
                from flow.application.config.config import Config  # correct source

                cfg = Config.from_env(require_auth=True)
                provider_cfg = cfg.provider_config if isinstance(cfg.provider_config, dict) else {}
                cfg_keys = provider_cfg.get("ssh_keys") or []
                if isinstance(cfg_keys, list):
                    effective_keys = list(cfg_keys)

        # Missing keys are allowed (SSH/logs will be unavailable). Caller may warn.
        return effective_keys

    @staticmethod
    def real_provider_guard_values(
        config: TaskConfig | None, configs: list[TaskConfig] | None
    ) -> dict:
        """Extract values for real provider guard check.

        Args:
            config: Single config
            configs: Array of configs

        Returns:
            Dictionary with guard check values
        """
        if configs and len(configs) > 0:
            c = configs[0]
        else:
            c = config

        if not c:
            return {}

        return {
            "instance_type": getattr(c, "instance_type", None),
            "priority": getattr(c, "priority", None),
            "max_price_per_hour": getattr(c, "max_price_per_hour", None),
            "num_instances": int(getattr(c, "num_instances", 1) or 1),
        }

    @staticmethod
    def invalidate_caches() -> None:
        """Invalidate and refresh task caches after submission."""
        with suppress(ImportError, Exception):
            from flow.cli.utils.prefetch import (
                invalidate_cache_for_current_context,
                refresh_active_task_caches,
                refresh_all_tasks_cache,
            )

            invalidate_cache_for_current_context(["tasks_running", "tasks_pending", "tasks_all"])

            # Refresh in background
            import threading

            def refresh():
                with suppress(Exception):
                    refresh_active_task_caches()
                    refresh_all_tasks_cache()

            threading.Thread(target=refresh, daemon=True).start()
