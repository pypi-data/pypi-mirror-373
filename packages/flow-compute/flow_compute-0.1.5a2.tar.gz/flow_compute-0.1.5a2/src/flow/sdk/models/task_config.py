from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flow.core.docker import DockerConfig
from flow.utils.paths import WORKSPACE_DIR
from flow.sdk.models.enums import StorageInterface
from flow.sdk.models.retry import Retries
from flow.sdk.models.volume import MountSpec, VolumeSpec


class TaskConfig(BaseModel):
    """Complete task specification used by `Flow.run()`.

    One obvious way to express requirements; fails fast with clear validation.
    """

    model_config = ConfigDict(extra="allow")

    # Basic configuration
    name: str = Field(
        "flow-task",
        description="Task identifier",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
    )
    unique_name: bool = Field(True, description="Append unique suffix to name to ensure uniqueness")

    # Instance specification - either explicit type or capability-based
    instance_type: str | None = Field(None, description="Explicit instance type")
    min_gpu_memory_gb: int | None = Field(
        None, ge=1, le=640, description="Minimum GPU memory requirement"
    )

    # Command specification - accepts string, list, or multi-line script
    command: str | list[str] | None = Field(
        None, description="Command to execute (string, list, or script)"
    )

    # Environment
    image: str = Field("nvidia/cuda:12.1.0-runtime-ubuntu22.04", description="Container image")
    env: dict[str, str] = Field(default_factory=dict, description="Environment")

    @property
    def environment(self) -> dict[str, str]:
        """Alias for `env` (backward compatibility)."""
        return self.env

    working_dir: str = Field("/workspace", description="Container working directory")

    # Resources
    volumes: list[VolumeSpec | dict[str, Any]] = Field(default_factory=list)
    data_mounts: list[MountSpec] = Field(default_factory=list, description="Data to mount")

    # Networking
    ports: list[int] = Field(
        default_factory=list,
        description="Container/instance ports to expose. High ports only (>=1024).",
    )
    # Advanced: allow Docker data-root cache when explicitly enabled (single-node only)
    allow_docker_cache: bool = Field(
        False,
        description=(
            "Allow mounting a volume at /var/lib/docker to persist Docker image layers. "
            "Single-node tasks only; use with caution."
        ),
    )

    # Execution options
    retries: Retries | None = Field(
        default=None, description="Advanced retry configuration for task submission/execution"
    )
    max_price_per_hour: float | None = Field(None, gt=0, description="Maximum hourly price (USD)")
    max_run_time_hours: float | None = Field(
        None, description="Maximum runtime hours; 0 or None disables runtime monitoring"
    )
    min_run_time_hours: float | None = Field(
        None, gt=0, description="Minimum guaranteed runtime hours"
    )
    deadline_hours: float | None = Field(
        None, gt=0, le=168, description="Hours from submission until deadline"
    )

    # SSH and access
    ssh_keys: list[str] = Field(default_factory=list, description="Authorized SSH key IDs")

    # Advanced options
    allocation_mode: Literal["spot", "reserved", "auto"] = Field(
        "spot",
        description=(
            "Allocation strategy: 'spot' (default, preemptible), 'reserved' (scheduled capacity), or 'auto'."
        ),
    )
    reservation_id: str | None = Field(
        None, description="Target an existing reservation (advanced)."
    )
    scheduled_start_time: str | None = Field(
        None, description="When allocation_mode='reserved', schedule start (UTC)."
    )
    reserved_duration_hours: int | None = Field(
        None,
        ge=3,
        le=336,
        description="When allocation_mode='reserved', reservation duration in hours (3-336).",
    )
    region: str | None = Field(None, description="Target region")
    num_instances: int = Field(1, ge=1, le=100, description="Instance count")
    priority: Literal["low", "med", "high"] = Field(
        "med", description="Task priority tier affecting limit price"
    )
    # Distributed execution mode: None => provider decides (auto for multi-node)
    distributed_mode: Literal["auto", "manual"] | None = Field(
        None,
        description=(
            "Distributed rendezvous mode when num_instances > 1: "
            "'auto' lets Flow assign rank and leader IP; 'manual' expects user-set FLOW_* envs."
        ),
    )
    # Topology preferences
    internode_interconnect: str | None = Field(
        None,
        description="Preferred inter-node network (e.g., InfiniBand, IB_3200, Ethernet)",
    )
    intranode_interconnect: str | None = Field(
        None, description="Preferred intra-node interconnect (e.g., SXM5, PCIe)"
    )
    upload_code: bool = Field(True, description="Upload current directory code to job")
    upload_strategy: Literal["auto", "embedded", "scp", "none"] = Field(
        "auto",
        description=(
            "Strategy for uploading code to instances:\n"
            "  - auto: Use SCP for large (>8KB), embedded for small\n"
            "  - embedded: Include in startup script (10KB limit)\n"
            "  - scp: Transfer after instance starts (no size limit)\n"
            "  - none: No code upload"
        ),
    )
    upload_timeout: int = Field(
        600, ge=60, le=3600, description="Maximum seconds to wait for code upload (60-3600)"
    )
    # Local code root selection
    code_root: str | Path | None = Field(
        default=None,
        description=(
            "Local project directory to upload when upload_code=True. "
            "Defaults to the current working directory when not set."
        ),
    )

    @field_validator("code_root", mode="before")
    def _normalize_code_root(cls, v: Any) -> str | None:  # noqa: N805 - pydantic class validator
        if v is None or v == "":
            return None
        try:
            return str(Path(v).expanduser())
        except Exception:
            return str(v)

    @field_validator("command", mode="before")
    def normalize_command(cls, v: Any) -> str | list[str]:  # noqa: N805 - pydantic class validator
        if isinstance(v, str | list):
            return v
        return v

    @field_validator("volumes", mode="before")
    def normalize_volumes(cls, v: Any) -> list[VolumeSpec]:  # noqa: N805 - pydantic class validator
        result: list[VolumeSpec] = []
        for vol in v:
            if isinstance(vol, dict):
                result.append(VolumeSpec(**vol))
            elif (
                isinstance(vol, BaseModel | object)
                and getattr(vol, "__class__", None)
                and vol.__class__.__name__ == "Volume"
            ):
                local = getattr(vol, "local", None)
                remote = getattr(vol, "remote", None)
                if local and remote:
                    result.append(
                        VolumeSpec(
                            size_gb=1,
                            mount_path=remote,
                            name=(getattr(vol, "name", None) or None),
                        )
                    )
                else:
                    sz = int(getattr(vol, "size_gb", 1) or 1)
                    result.append(
                        VolumeSpec(
                            size_gb=max(1, sz),
                            mount_path=f"/volumes/{getattr(vol, 'name', 'volume')}",
                            name=getattr(vol, "name", "volume"),
                        )
                    )
            else:
                result.append(vol)
        return result

    @model_validator(mode="after")
    def validate_config(self) -> TaskConfig:
        if not self.command:
            self.command = "sleep infinity"

        if self.unique_name:
            import uuid

            if not re.search(r"-[0-9a-f]{6}$", self.name, flags=re.IGNORECASE):
                suffix = uuid.uuid4().hex[:6]
                self.name = f"{self.name}-{suffix}"

        if self.instance_type and self.min_gpu_memory_gb:
            raise ValueError(
                "Cannot specify both instance_type and min_gpu_memory_gb. Choose one:\n"
                "  instance_type='a100' (specific GPU)\n"
                "  min_gpu_memory_gb=40 (any GPU with 40GB+)"
            )
        if not self.instance_type and not self.min_gpu_memory_gb:
            raise ValueError(
                "Must specify either instance_type or min_gpu_memory_gb:\n"
                "  instance_type='a100' or '4xa100' or 'h100'\n"
                "  min_gpu_memory_gb=24, 40, or 80"
            )

        if self.max_run_time_hours == 0:
            self.max_run_time_hours = None
        if self.min_run_time_hours == 0:
            self.min_run_time_hours = None

        if self.max_run_time_hours is not None:
            try:
                val = float(self.max_run_time_hours)
            except Exception as err:
                raise ValueError("max_run_time_hours must be a number") from err
            if val < 0 or not (val <= 168):
                raise ValueError("max_run_time_hours must be within 0..168 hours (0 disables)")
        if self.min_run_time_hours is not None:
            try:
                val_min = float(self.min_run_time_hours)
            except Exception as err:
                raise ValueError("min_run_time_hours must be a number") from err
            if val_min < 0 or not (val_min <= 168):
                raise ValueError("min_run_time_hours must be within 0..168 hours")

        if (
            self.min_run_time_hours
            and self.max_run_time_hours
            and (self.min_run_time_hours > self.max_run_time_hours)
        ):
            raise ValueError(
                f"min_run_time_hours ({self.min_run_time_hours}) cannot exceed "
                f"max_run_time_hours ({self.max_run_time_hours})"
            )

        if (
            self.deadline_hours
            and self.max_run_time_hours
            and (self.deadline_hours < self.max_run_time_hours)
        ):
            raise ValueError(
                f"deadline_hours ({self.deadline_hours}) should be >= "
                f"max_run_time_hours ({self.max_run_time_hours})"
            )

        restricted_paths = set(DockerConfig.RESTRICTED_MOUNT_PATHS)
        user_targets: list[str] = []
        for vol in self.volumes:
            v = vol if isinstance(vol, VolumeSpec) else VolumeSpec(**vol)  # type: ignore[arg-type]
            if v.mount_path:
                user_targets.append(v.mount_path)
        for m in self.data_mounts:
            if m.target:
                user_targets.append(m.target)

        internal_targets: list[str] = []
        if self.upload_code:
            internal_targets.append(WORKSPACE_DIR)

        for t in user_targets:
            if t in restricted_paths and not (
                t == "/var/lib/docker"
                and getattr(self, "allow_docker_cache", False)
                and (getattr(self, "num_instances", 1) == 1)
            ):
                raise ValueError(
                    f"Mount target {t} is restricted. Choose a different path (e.g., under /volumes or /data)."
                )

        if self.upload_code and any(t == WORKSPACE_DIR for t in user_targets):
            raise ValueError(
                f"Cannot mount a user volume at {WORKSPACE_DIR} while upload_code=True. "
                "Either set upload_code=False and use a workspace volume, or mount the volume elsewhere."
            )

        if getattr(self, "ports", None):
            sanitized_ports: list[int] = []
            seen_ports: set[int] = set()
            for p in self.ports:
                try:
                    port_int = int(p)
                except Exception as err:
                    raise ValueError(f"Invalid port value: {p}") from err
                if port_int < 1024 or port_int > 65535:
                    raise ValueError(
                        f"Port {port_int} out of allowed range (1024-65535). Lower ports are not supported."
                    )
                if port_int not in seen_ports:
                    seen_ports.add(port_int)
                    sanitized_ports.append(port_int)
            object.__setattr__(self, "ports", sanitized_ports)

        all_targets = user_targets + internal_targets
        seen = set()
        for t in all_targets:
            if t in seen:
                continue
            seen.add(t)

        def is_nested(a: str, b: str) -> bool:
            if a == b:
                return False
            a_norm = a.rstrip("/")
            b_norm = b.rstrip("/")
            return a_norm.startswith(b_norm + "/") or b_norm.startswith(a_norm + "/")

        for i, a in enumerate(all_targets):
            for j, b in enumerate(all_targets):
                if i < j and is_nested(a, b):
                    raise ValueError(
                        f"Conflicting mount targets: '{a}' and '{b}' overlap. Use distinct, non-nested paths."
                    )

        if self.num_instances and self.num_instances > 1 and self.volumes:
            for vol in self.volumes:
                v = vol if isinstance(vol, VolumeSpec) else VolumeSpec(**vol)  # type: ignore[arg-type]
                if v.interface == StorageInterface.BLOCK:
                    raise ValueError(
                        "Block storage volumes cannot be attached to multi-instance tasks.\n"
                        "Solutions:\n"
                        "  • Use interface: file (file share) for multi-attach (region- and quota-dependent)\n"
                        "  • Reduce num_instances to 1 to use block storage\n"
                        "  • For read-only datasets, prefer data_mounts (e.g., s3://...) shared across nodes"
                    )

        return self

    @classmethod
    def from_yaml(cls, path: str | Path) -> TaskConfig:
        from flow.errors import ConfigParserError

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigParserError(
                        f"Task configuration must be a YAML dictionary, got {type(data).__name__}",
                        suggestions=[
                            "Ensure your YAML file contains key: value pairs",
                            "Example: instance_type: 'A100-40GB'",
                            f"Check the structure of {path}",
                        ],
                        error_code="CONFIG_003",
                    )
        except yaml.YAMLError as e:
            raise ConfigParserError(
                f"Invalid YAML syntax in task configuration {path}: {e!s}",
                suggestions=[
                    "Check YAML indentation (use spaces, not tabs)",
                    "Ensure all GPU types are quoted (e.g., 'A100-40GB')",
                    "Validate syntax at yamllint.com",
                ],
                error_code="CONFIG_001",
            ) from e

        return cls(**data)

    def to_yaml(self, path: str | Path) -> None:
        with open(path, "w") as f:
            yaml.dump(self.model_dump(exclude_none=True), f, sort_keys=False)
