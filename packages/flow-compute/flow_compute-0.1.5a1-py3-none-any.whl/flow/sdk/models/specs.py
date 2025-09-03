"""Hardware and resource specifications for Flow API models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class GPUSpec(BaseModel):
    """GPU hardware specifications."""

    model_config = {"extra": "forbid"}

    gpu_type: str = Field(..., description="GPU model (e.g., 'h100', 'a100')")
    gpu_count: int = Field(1, ge=1, le=8, description="Number of GPUs")
    gpu_memory_gb: int | None = Field(None, ge=1, description="GPU memory in GB")
    compute_capability: str | None = Field(None, description="CUDA compute capability")

    @field_validator("gpu_type")
    @classmethod
    def normalize_gpu_type(cls, v: str) -> str:
        """Normalize GPU type to lowercase."""
        return v.lower().strip()


class CPUSpec(BaseModel):
    """CPU hardware specifications."""

    model_config = {"extra": "forbid"}

    cpu_count: int = Field(..., ge=1, description="Number of CPU cores")
    cpu_type: str | None = Field(None, description="CPU model/architecture")
    cpu_freq_ghz: float | None = Field(None, gt=0, description="CPU frequency in GHz")


class MemorySpec(BaseModel):
    """Memory specifications."""

    model_config = {"extra": "forbid"}

    memory_gb: int = Field(..., ge=1, description="Memory in GB")
    memory_type: str | None = Field(None, description="Memory type (e.g., DDR4, DDR5)")


class StorageSpec(BaseModel):
    """Storage specifications."""

    model_config = {"extra": "forbid"}

    storage_gb: int = Field(..., ge=1, description="Storage capacity in GB")
    storage_type: str | None = Field(None, description="Storage type (e.g., SSD, NVMe)")
    iops: int | None = Field(None, ge=0, description="IOPS capacity")


class NetworkSpec(BaseModel):
    """Network specifications."""

    model_config = {"extra": "forbid"}

    bandwidth_gbps: float | None = Field(None, gt=0, description="Network bandwidth in Gbps")
    network_type: str | None = Field(None, description="Network type")
    public_ip: bool = Field(True, description="Whether instance has public IP")
    ports: list[int] | None = Field(None, description="Open ports")


class ReservationSpec(BaseModel):
    """Reservation request specifications."""

    model_config = {"extra": "allow"}

    instance_type: str = Field(..., description="Instance type to reserve")
    region: str | None = Field(None, description="Region for reservation")
    duration_hours: int = Field(24, ge=1, le=8760, description="Reservation duration in hours")
    auto_renew: bool = Field(False, description="Auto-renew reservation")
    tags: dict[str, str] = Field(default_factory=dict, description="Resource tags")

    @field_validator("instance_type")
    @classmethod
    def validate_instance_type(cls, v: str) -> str:
        """Validate instance type format."""
        if not v or not v.strip():
            raise ValueError("Instance type cannot be empty")
        return v.strip()
