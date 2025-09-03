from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flow.utils.paths import VOLUMES_ROOT
from flow.sdk.models.enums import StorageInterface


class VolumeSpec(BaseModel):
    """Persistent volume specification (create or attach)."""

    model_config = ConfigDict(extra="forbid")

    # Human-friendly name
    name: str | None = Field(
        None,
        description="Human-readable name (3-64 chars, lowercase alphanumeric with hyphens)",
        pattern="^[a-z0-9][a-z0-9-]*[a-z0-9]$",
        min_length=3,
        max_length=64,
    )

    # Core fields
    size_gb: int = Field(1, ge=1, le=15000, description="Size in GB")
    # Canonical field name is mount_path; accept 'target' as an alias via pre-validation below
    mount_path: str | None = Field(
        None, description="Mount path in container (default: /volumes/<name>)"
    )

    # Volume ID for existing volumes
    volume_id: str | None = Field(None, description="ID of existing volume to attach")

    # Advanced options
    interface: StorageInterface = Field(
        StorageInterface.BLOCK, description="Storage interface type"
    )
    iops: int | None = Field(None, ge=100, le=64000, description="Provisioned IOPS")
    throughput_mb_s: int | None = Field(None, ge=125, le=1000, description="Provisioned throughput")

    @model_validator(mode="after")
    def validate_volume_spec(self) -> VolumeSpec:
        """Validate volume specification."""
        if self.volume_id and (self.iops or self.throughput_mb_s):
            raise ValueError("Cannot specify IOPS/throughput for existing volumes")
        # Set sensible default mount path if not provided
        if not self.mount_path:
            # Prefer using provided name
            if self.name:
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/{self.name}")
            elif self.volume_id:
                # Derive a readable stable path from volume id suffix
                suffix = self.volume_id[-6:] if len(self.volume_id) >= 6 else self.volume_id
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/volume-{suffix}")
            else:
                # Fallback (should be rare for new unnamed volumes)
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/volume")
        return self

    @model_validator(mode="before")
    def _alias_target_to_mount_path(cls, data: Any):  # type: ignore[no-redef]  # noqa: N805
        """Allow 'target' as an alias for 'mount_path' in YAML/JSON."""
        if isinstance(data, dict) and ("mount_path" not in data and "target" in data):
            data = {**data, "mount_path": data.get("target")}
            data.pop("target", None)
        return data


class MountSpec(BaseModel):
    """Mount specification for volumes, S3, or bind mounts."""

    source: str = Field(..., description="Source URL or path")
    target: str = Field(..., description="Mount path in container")
    mount_type: Literal["bind", "volume", "s3fs"] = Field("bind", description="Type of mount")
    options: dict[str, Any] = Field(default_factory=dict, description="Provider-specific options")

    # Performance hints
    cache_key: str | None = Field(None, description="Key for caching mount metadata")
    size_estimate_gb: float | None = Field(None, ge=0, description="Estimated size for planning")


class Volume(BaseModel):
    """Unified Volume model supporting both persistent volumes and bind mounts.

    This model is used by startup script builder tests with fields
    `local`, `remote`, and `read_only` to represent bind mounts.
    """

    model_config = ConfigDict(extra="allow")

    # Bind mount fields (used by startup scripts)
    local: str | None = Field(default=None, description="Source path on host")
    remote: str | None = Field(default=None, description="Target path in container")
    read_only: bool | None = Field(default=None, description="Mount read-only")

    # Persistent volume fields (used by volume APIs)
    volume_id: str | None = Field(default=None, description="Volume ID")
    name: str | None = Field(default=None, description="Volume name")
    size_gb: int | None = Field(default=None, description="Capacity (GB)")
    region: str | None = Field(default=None, description="Storage region")
    interface: StorageInterface | None = Field(default=None, description="Storage interface type")
    attached_to: list[str] = Field(default_factory=list, description="Attached instance IDs")
    created_at: Any | None = Field(default=None, description="Creation timestamp")

    # Back-compat: `id` property aliasing to `volume_id` when present
    @property
    def id(self) -> str | None:  # type: ignore[override]
        return self.volume_id
