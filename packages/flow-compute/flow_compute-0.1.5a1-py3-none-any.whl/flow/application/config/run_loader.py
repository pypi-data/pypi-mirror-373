"""Configuration loading for the run command.

This module handles loading and parsing of task configurations from
various sources (YAML, SLURM scripts) following single responsibility
and dependency injection principles.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from flow.sdk.models import TaskConfig
from flow.sdk.models.run_params import RunParameters

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration loading or parsing fails."""

    pass


class TaskConfigLoader:
    """Loads and parses task configurations from files.

    This class encapsulates all configuration loading logic that was
    previously embedded in the RunCommand._execute method (lines 680-806).
    """

    def load(self, params: RunParameters) -> tuple[TaskConfig | None, list[TaskConfig] | None]:
        """Load configuration based on parameters.

        Args:
            params: Run parameters including config file path and type hints.

        Returns:
            Tuple of (single_config, config_list) where one will be None.

        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded.
        """
        if not params.config_file:
            return self._create_interactive_config(params), None

        if self._is_slurm_file(params.config_file, params.is_slurm):
            return None, self._load_slurm_configs(params.config_file, params)

        return self._load_yaml_config(params.config_file, params), None

    def _is_slurm_file(self, path: Path, explicit_slurm: bool) -> bool:
        """Detect if a file is a SLURM script."""
        if explicit_slurm:
            return True

        # Check extension
        if path.suffix.lower() in (".slurm", ".sbatch"):
            return True

        # Check content for SLURM directives
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    head = f.read(4096)
                    if "#SBATCH" in head:
                        return True
            except (OSError, UnicodeDecodeError):
                logger.debug(f"Could not read {path} to detect SLURM format")

        return False

    def _load_yaml_config(self, path: Path, params: RunParameters) -> TaskConfig:
        """Load and parse a YAML configuration file.

        Args:
            path: Path to YAML file.
            params: Run parameters for applying overrides.

        Returns:
            Parsed TaskConfig with overrides applied.

        Raises:
            ConfigurationError: If YAML is invalid or file not found.
        """
        if not path.exists():
            raise ConfigurationError(f"Configuration file does not exist: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ConfigurationError("YAML must be a mapping of keys to values")

            # Apply naming policy
            self._apply_naming_policy(data, params)

            # Create base config
            config = TaskConfig(**data)

            # Apply overrides
            return self._apply_overrides(config, params)

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML: {e}")
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Invalid configuration: {e}")

    def _load_slurm_configs(self, path: Path, params: RunParameters) -> list[TaskConfig]:
        """Load and parse a SLURM script into task configs.

        Args:
            path: Path to SLURM script.
            params: Run parameters for applying overrides.

        Returns:
            List of TaskConfig objects (possibly array job).

        Raises:
            ConfigurationError: If SLURM script is invalid.
        """
        try:
            from flow.plugins.slurm.adapter import SlurmFrontendAdapter
            from flow.plugins.slurm.parser import parse_sbatch_script

            adapter = SlurmFrontendAdapter()

            # Build SLURM overrides from parameters
            slurm_overrides = self._build_slurm_overrides(params)

            # Check for array job
            slurm_cfg = parse_sbatch_script(str(path))
            if getattr(slurm_cfg, "array", None):
                configs = adapter.parse_array_job(str(path), **slurm_overrides)
            else:
                single = adapter.parse_and_convert(str(path), **slurm_overrides)
                configs = [single]

            # Apply overrides to each config
            return [self._apply_overrides(cfg, params) for cfg in configs]

        except ImportError as e:
            raise ConfigurationError(f"SLURM support not available: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to parse SLURM script: {e}")

    def _create_interactive_config(self, params: RunParameters) -> TaskConfig:
        """Create configuration for interactive instance.

        Args:
            params: Run parameters.

        Returns:
            TaskConfig for interactive session.
        """
        config_dict = {
            "name": params.execution.name or ("run" if params.execution.command else "interactive"),
            "unique_name": params.execution.unique_name,
            "instance_type": params.instance.instance_type,
            "image": params.execution.image,
            "env": params.execution.environment,
        }

        if params.instance.region:
            config_dict["region"] = params.instance.region

        if params.execution.command:
            config_dict["command"] = params.execution.command
        else:
            config_dict["command"] = ["sleep", "infinity"]

        if params.ssh.keys:
            config_dict["ssh_keys"] = list(params.ssh.keys)

        if params.instance.priority:
            config_dict["priority"] = params.instance.priority

        if params.instance.max_price_per_hour is not None:
            config_dict["max_price_per_hour"] = params.instance.max_price_per_hour

        if params.instance.num_instances != 1:
            config_dict["num_instances"] = params.instance.num_instances

        if params.instance.distributed_mode:
            config_dict["distributed_mode"] = params.instance.distributed_mode

        return TaskConfig(**config_dict)

    def _apply_naming_policy(self, data: dict, params: RunParameters) -> None:
        """Apply naming policy to configuration data.

        Modifies data dict in place to set unique_name appropriately.
        """
        if "unique_name" not in data:
            has_name = bool((data.get("name") or "").strip())
            data["unique_name"] = False if has_name else True

    def _apply_overrides(self, config: TaskConfig, params: RunParameters) -> TaskConfig:
        """Apply parameter overrides to a configuration.

        Args:
            config: Base configuration.
            params: Parameters containing overrides.

        Returns:
            New TaskConfig with overrides applied.
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

        # Upload overrides
        if params.upload.strategy != "auto":
            updates["upload_strategy"] = params.upload.strategy
            updates["upload_timeout"] = params.upload.timeout
        elif params.upload.timeout != 600:
            updates["upload_timeout"] = params.upload.timeout
        if params.upload.code_root:
            updates["code_root"] = str(params.upload.code_root)

        # Environment overrides
        if params.execution.environment:
            merged_env = dict(getattr(config, "env", {}) or {})
            merged_env.update(params.execution.environment)
            updates["env"] = merged_env

        # Port overrides
        if params.execution.ports:
            updates["ports"] = list(params.execution.ports)

        # Reservation overrides
        if params.allocation_mode:
            updates["allocation_mode"] = params.allocation_mode
        if params.reservation_id:
            updates["reservation_id"] = params.reservation_id
        if params.start_time:
            from datetime import datetime

            iso = params.start_time.replace("Z", "+00:00")
            updates["scheduled_start_time"] = datetime.fromisoformat(iso)
        if params.duration_hours is not None:
            updates["reserved_duration_hours"] = params.duration_hours

        return config.model_copy(update=updates) if updates else config

    def _build_slurm_overrides(self, params: RunParameters) -> dict:
        """Build override dictionary for SLURM adapter.

        Args:
            params: Run parameters.

        Returns:
            Dictionary of SLURM-specific overrides.
        """
        overrides = {}

        # Convert Flow instance type to SLURM GPU specification
        if params.instance.instance_type:
            instance_type = params.instance.instance_type.strip().lower()
            if "x" in instance_type:
                try:
                    count, gpu = instance_type.split("x", 1)
                    int(count)  # Validate it's a number
                    overrides["gpus"] = f"{gpu}:{count}"
                except (ValueError, AttributeError):
                    overrides["gpus"] = instance_type
            else:
                overrides["gpus"] = instance_type

        if params.instance.num_instances != 1:
            overrides["nodes"] = params.instance.num_instances

        return overrides
