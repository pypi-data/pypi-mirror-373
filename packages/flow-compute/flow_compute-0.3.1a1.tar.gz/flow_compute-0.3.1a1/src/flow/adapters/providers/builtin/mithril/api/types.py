"""Type definitions for Mithril API responses.

Strong typing for all API responses based on the official Mithril spec.
These types ensure compile-time safety and self-documenting code.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectModel(BaseModel):
    """Project resource from /v2/projects."""

    fid: str
    name: str
    created_at: datetime


class SSHKeyModel(BaseModel):
    """SSH key resource from /v2/ssh-keys."""

    fid: str
    name: str
    project: str | None = None
    public_key: str
    created_at: datetime
    # Some projects mark keys as required for all new instances
    # The API may expose this as `required` (preferred) or `is_required` (legacy)
    required: bool | None = None

    @classmethod
    def from_api(cls, data: dict) -> "SSHKeyModel":
        """Construct model from API payload, normalizing legacy fields.

        API: NewSshKeyModel includes `required: bool` per
        `GET /v2/ssh-keys` and `PATCH /v2/ssh-keys/{fid}` in the spec.
        See: `https://api.mithril.ai` OpenAPI `NewSshKeyModel.required`.
        """
        normalized = dict(data)
        if "required" not in normalized and "is_required" in normalized:
            normalized["required"] = bool(normalized.get("is_required"))
        return cls(**normalized)


class GPUModel(BaseModel):
    """GPU specifications within an instance type."""

    name: str
    vram_gb: int
    count: int


class InstanceTypeModel(BaseModel):
    """Instance type resource from /v2/instance-types."""

    name: str
    fid: str
    cpu_cores: int | None = Field(None, alias="num_cpus")  # API uses num_cpus
    ram_gb: int | None = Field(None, alias="ram")  # API uses ram
    gpus: list[GPUModel] | None = None
    storage_gb: int | None = Field(None, alias="local_storage_gb")
    network_bandwidth_gbps: float | None = None

    model_config = ConfigDict(populate_by_name=True)  # Allow both field names and aliases


class AuctionModel(BaseModel):
    """Spot auction resource from /v2/spot/availability."""

    fid: str
    instance_type: str
    region: str
    capacity: int
    last_instance_price: str  # Dollar string format: "$25.60"
    min_bid_price: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BidModel(BaseModel):
    """Spot bid resource from /v2/spot/bids."""

    fid: str
    project: str
    region: str
    instance_type: str
    price: str  # Dollar string format
    status: Literal[
        "pending", "running", "completed", "failed", "cancelled", "won", "lost", "expired"
    ]
    created_at: datetime
    updated_at: datetime
    ssh_keys: list[str]
    startup_script: str | None = None
    volumes: list[str] | None = None
    allocation_id: str | None = None


class BidsResponse(BaseModel):
    """Paginated response from GET /v2/spot/bids."""

    data: list[BidModel]
    next_cursor: str | None = None


class VolumeModel(BaseModel):
    """Storage volume resource from /v2/volumes."""

    fid: str
    name: str
    project: str
    region: str
    capacity_gb: int
    interface: Literal["block", "file"]
    status: Literal["available", "attached", "deleting"]
    created_at: datetime
    updated_at: datetime
    mount_targets: list[dict] | None = None
    attached_to: list[str] | None = None

    # Back-compat convenience attribute used by some tests
    @property
    def size_gb(self) -> int:
        return self.capacity_gb


# Type aliases for API responses
ProjectsResponse = list[ProjectModel]
SSHKeysResponse = list[SSHKeyModel]
InstanceTypesResponse = list[InstanceTypeModel]
SpotAvailabilityResponse = list[AuctionModel]
VolumesResponse = list[VolumeModel]


# Request models
class CreateVolumeRequest(BaseModel):
    """Request to create a volume."""

    name: str
    project: str
    disk_interface: str
    region: str
    size_gb: int


class CreateBidRequest(BaseModel):
    """Request to create a spot bid."""

    project: str
    region: str
    instance_type: str
    price: str  # Dollar string format
    ssh_keys: list[str]
    startup_script: str | None = None
    volumes: list[str] | None = None


class UpdateBidRequest(BaseModel):
    """Request to update a spot bid."""

    price: str | None = None
    status: Literal["cancelled"] | None = None


# Response models
class UserModel(BaseModel):
    """User information from /v2/me."""

    fid: str
    email: str
    name: str | None = None
    created_at: datetime


class CreatedSshKey(BaseModel):
    """Response from creating an SSH key."""

    fid: str
    name: str
    project: str
    public_key: str
    created_at: datetime


class InstanceModel(BaseModel):
    """Instance resource."""

    fid: str
    bid: str
    status: Literal["pending", "running", "stopped", "terminated"]
    public_ip: str | None = None
    private_ip: str | None = None
    created_at: datetime
    terminated_at: datetime | None = None
