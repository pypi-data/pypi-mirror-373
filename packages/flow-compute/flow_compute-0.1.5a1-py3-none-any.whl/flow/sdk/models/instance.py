from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from flow.sdk.models.enums import InstanceStatus


class AvailableInstance(BaseModel):
    """Available compute resource."""

    allocation_id: str = Field(..., description="Resource allocation ID")
    instance_type: str = Field(..., description="Instance type identifier")
    region: str = Field(..., description="Availability region")
    price_per_hour: float = Field(..., description="Hourly price (USD)")

    # Hardware specs
    gpu_type: str | None = Field(None, description="GPU type")
    gpu_count: int | None = Field(None, description="Number of GPUs")
    cpu_count: int | None = Field(None, description="Number of CPUs")
    memory_gb: int | None = Field(None, description="Memory in GB")

    # Availability info
    available_quantity: int | None = Field(None, description="Number available")
    status: str | None = Field(None, description="Allocation status")
    expires_at: datetime | None = Field(None, description="Expiration time")

    # Topology
    internode_interconnect: str | None = Field(
        None, description="Inter-node network (e.g., InfiniBand, IB_3200, Ethernet)"
    )
    intranode_interconnect: str | None = Field(
        None, description="Intra-node interconnect (e.g., SXM5, PCIe)"
    )


class Instance(BaseModel):
    """Compute instance entity."""

    instance_id: str = Field(..., description="Instance UUID")
    task_id: str = Field(..., description="Parent task ID")
    status: InstanceStatus = Field(..., description="Instance state")

    # Connection info
    ssh_host: str | None = Field(None, description="Public hostname/IP")
    private_ip: str | None = Field(None, description="VPC-internal IP")

    # Timestamps
    created_at: datetime
    terminated_at: datetime | None = None
