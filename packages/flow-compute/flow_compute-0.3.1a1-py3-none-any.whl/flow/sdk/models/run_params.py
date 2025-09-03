"""Value objects and data structures for the run command.

This module defines clean, immutable data structures that encapsulate
the complex parameter sets used by the run command, following Google's
Python style guide and clean architecture principles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class InstanceConfig:
    """Configuration for instance specifications."""

    instance_type: str
    region: str | None = None
    priority: str | None = None
    max_price_per_hour: float | None = None
    num_instances: int = 1
    distributed_mode: str | None = None

    def validate(self) -> None:
        """Validate instance configuration."""
        if not self.instance_type.strip():
            raise ValueError("Instance type cannot be empty")

        if self.num_instances < 1:
            raise ValueError("Number of instances must be at least 1")

        if self.priority and self.priority not in ("low", "med", "high"):
            raise ValueError(f"Invalid priority: {self.priority}")

        if self.max_price_per_hour is not None and self.max_price_per_hour <= 0:
            raise ValueError("Max price per hour must be positive")


@dataclass(frozen=True)
class SSHConfig:
    """Configuration for SSH access."""

    keys: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        """Validate SSH configuration."""
        # SSH keys are optional but will be validated by provider
        pass

    def effective_keys(
        self, env_keys: list[str] | None = None, provider_keys: list[str] | None = None
    ) -> list[str]:
        """Compute effective SSH keys with fallback hierarchy."""
        if self.keys:
            return list(self.keys)
        if env_keys:
            return env_keys
        if provider_keys:
            return provider_keys
        return []


@dataclass(frozen=True)
class UploadConfig:
    """Configuration for code upload."""

    strategy: str = "auto"  # auto, embedded, scp, none
    timeout: int = 600
    code_root: Path | None = None
    on_failure: str = "continue"  # continue, fail

    def validate(self) -> None:
        """Validate upload configuration."""
        valid_strategies = {"auto", "embedded", "scp", "none"}
        if self.strategy not in valid_strategies:
            raise ValueError(f"Invalid upload strategy: {self.strategy}")

        if self.timeout <= 0:
            raise ValueError("Upload timeout must be positive")

        if self.on_failure not in ("continue", "fail"):
            raise ValueError(f"Invalid on_failure policy: {self.on_failure}")

    @property
    def is_cli_managed(self) -> bool:
        """Check if CLI should manage the upload directly."""
        return self.strategy == "scp"


@dataclass(frozen=True)
class ExecutionConfig:
    """Configuration for task execution behavior."""

    wait: bool = True
    watch: bool = False
    dry_run: bool = False
    output_json: bool = False

    name: str | None = None
    unique_name: bool = True
    name_conflict_policy: str = "error"  # error, suffix

    image: str = "nvidia/cuda:12.1.0-runtime-ubuntu22.04"
    command: str | None = None
    environment: dict[str, str] = field(default_factory=dict)
    ports: tuple[int, ...] = field(default_factory=tuple)
    mounts: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate execution configuration."""
        if self.name_conflict_policy not in ("error", "suffix"):
            raise ValueError(f"Invalid name conflict policy: {self.name_conflict_policy}")

        for port in self.ports:
            if not (1024 <= port <= 65535):
                raise ValueError(f"Invalid port {port}: must be in range 1024-65535")


@dataclass(frozen=True)
class DisplayConfig:
    """Configuration for output display."""

    show_pricing: bool = False
    compact: bool = False
    verbose: bool = False

    @property
    def should_show_timeline(self) -> bool:
        """Check if progress timeline should be displayed."""
        return not self.compact


@dataclass(frozen=True)
class RunParameters:
    """Complete parameter set for the run command.

    This immutable structure encapsulates all parameters needed for
    task submission, replacing the 34-parameter method signature.
    """

    config_file: Path | None = None
    is_slurm: bool = False

    instance: InstanceConfig = field(default_factory=lambda: InstanceConfig(instance_type="8xh100"))
    ssh: SSHConfig = field(default_factory=SSHConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)

    # Reservation support (future feature)
    allocation_mode: str | None = None
    reservation_id: str | None = None
    start_time: str | None = None
    duration_hours: int | None = None

    def validate(self) -> None:
        """Validate all parameter configurations."""
        self.instance.validate()
        self.ssh.validate()
        self.upload.validate()
        self.execution.validate()

        # Validate mutually exclusive options
        if self.config_file and self.execution.command:
            raise ValueError("Cannot specify both config file and command")

        # Validate reservation parameters when enabled
        if self.allocation_mode:
            if self.allocation_mode not in ("spot", "reserved", "auto"):
                raise ValueError(f"Invalid allocation mode: {self.allocation_mode}")

    @classmethod
    def from_click_params(cls, **kwargs) -> RunParameters:
        """Create RunParameters from Click command parameters.

        This factory method handles the translation from Click's flat
        parameter structure to our organized value objects.
        """
        # Extract instance configuration
        instance = InstanceConfig(
            instance_type=kwargs.get("instance_type") or DEFAULT_INSTANCE_TYPE,
            region=kwargs.get("region"),
            priority=kwargs.get("priority"),
            max_price_per_hour=kwargs.get("max_price_per_hour"),
            num_instances=kwargs.get("num_instances", 1),
            distributed_mode=kwargs.get("distributed"),
        )

        # Extract SSH configuration
        ssh = SSHConfig(keys=kwargs.get("ssh_keys", ()))

        # Extract upload configuration
        upload = UploadConfig(
            strategy=kwargs.get("upload_strategy", "auto"),
            timeout=kwargs.get("upload_timeout", DEFAULT_UPLOAD_TIMEOUT),
            code_root=Path(kwargs["code_root"]) if kwargs.get("code_root") else None,
            on_failure=kwargs.get("on_upload_failure", "continue"),
        )

        # Determine name conflict policy
        if kwargs.get("force_new"):
            conflict_policy = "suffix"
        elif kwargs.get("on_name_conflict"):
            conflict_policy = kwargs["on_name_conflict"]
        elif not kwargs.get("name"):
            conflict_policy = "suffix"
        else:
            conflict_policy = "error"

        # Extract execution configuration
        execution = ExecutionConfig(
            wait=kwargs.get("wait", True),
            watch=kwargs.get("watch", False),
            dry_run=kwargs.get("dry_run", False),
            output_json=kwargs.get("output_json", False),
            name=kwargs.get("name"),
            unique_name=not kwargs.get("no_unique", False),
            name_conflict_policy=conflict_policy,
            image=kwargs.get("image", DEFAULT_IMAGE),
            command=kwargs.get("command"),
            environment=dict(kwargs.get("env_items", ())),
            ports=kwargs.get("port", ()),
            mounts={},  # Will be populated separately
        )

        # Extract display configuration
        display = DisplayConfig(
            show_pricing=kwargs.get("pricing", False),
            compact=kwargs.get("compact", False),
            verbose=kwargs.get("verbose", False),
        )

        # Create parameters object
        config_path = Path(kwargs["config_file"]) if kwargs.get("config_file") else None

        return cls(
            config_file=config_path,
            is_slurm=kwargs.get("slurm", False),
            instance=instance,
            ssh=ssh,
            upload=upload,
            execution=execution,
            display=display,
            allocation_mode=kwargs.get("allocation"),
            reservation_id=kwargs.get("reservation_id"),
            start_time=kwargs.get("start_time"),
            duration_hours=kwargs.get("duration_hours"),
        )


# Module constants that were in run.py
DEFAULT_IMAGE = "nvidia/cuda:12.1.0-runtime-ubuntu22.04"
DEFAULT_INSTANCE_TYPE = "8xh100"
DEFAULT_UPLOAD_TIMEOUT = 600
DEFAULT_UPLOAD_STRATEGY = "auto"
DEFAULT_UPLOAD_FAILURE_POLICY = "continue"
MAX_PORT = 65535
MIN_HIGH_PORT = 1024
DEFAULT_PROVISION_TIMEOUT_MINUTES = 20
