"""Mithril domain models (merged from core.models)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class MithrilBid(BaseModel):
    fid: str = Field(...)
    name: str = Field(...)
    project: str = Field(...)
    created_by: str = Field(...)
    created_at: datetime = Field(...)
    deactivated_at: datetime | None = Field(None)
    status: str = Field(...)
    limit_price: str = Field(...)
    instance_quantity: int = Field(...)
    instance_type: str = Field(...)
    region: str = Field(...)
    instances: list[str] = Field(default_factory=list)
    launch_specification: dict[str, Any] = Field(default_factory=dict)
    auction_id: str | None = Field(None)


class MithrilInstance(BaseModel):
    fid: str = Field(...)
    bid_id: str = Field(...)
    status: str = Field(...)
    public_ip: str | None = Field(None)
    private_ip: str | None = Field(None)
    ssh_host: str | None = Field(None)
    ssh_port: int | None = Field(22)
    instance_type: str = Field(...)
    region: str = Field(...)
    created_at: datetime = Field(...)
    terminated_at: datetime | None = Field(None)


class MithrilAuction(BaseModel):
    fid: str = Field(...)
    instance_type: str = Field(...)
    region: str = Field(...)
    capacity: int = Field(...)
    last_instance_price: str = Field(...)
    created_at: datetime | None = Field(None)
    expires_at: datetime | None = Field(None)


class MithrilVolume(BaseModel):
    fid: str = Field(...)
    name: str = Field(...)
    size_gb: int = Field(...)
    region: str = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    attached_to: list[str] = Field(default_factory=list)
    mount_path: str | None = Field(None)
    disk_interface: str | None = Field(None)
    # New: expose relationships present in API (bids/reservations)
    bids: list[str] = Field(default_factory=list)
    reservations: list[str] = Field(default_factory=list)
    # Metadata: whether API exposed current attachments explicitly
    attachments_supported: bool | None = Field(default=None)


class MithrilProject(BaseModel):
    fid: str = Field(...)
    name: str = Field(...)
    created_at: datetime = Field(...)
    region: str | None = Field(None)
    organization_id: str | None = Field(None)


class Auction(BaseModel):
    auction_id: str | None = Field(None)
    fid: str | None = Field(None)
    instance_type_id: str | None = Field(None)
    instance_type: str | None = Field(None)
    gpu_type: str | None = Field(None)
    available_gpus: int | None = Field(None)
    capacity: int | None = Field(None)
    price_per_hour: float | None = Field(None, ge=0)
    last_instance_price: str | None = Field(None)
    region: str | None = Field(None)
    internode_interconnect: str | None = Field(None)
    intranode_interconnect: str | None = Field(None)

    @model_validator(mode="after")
    def _normalize_synonyms(self) -> "Auction":
        if self.auction_id and not self.fid:
            object.__setattr__(self, "fid", self.auction_id)
        if self.fid and not self.auction_id:
            object.__setattr__(self, "auction_id", self.fid)
        if self.instance_type_id and not self.instance_type:
            object.__setattr__(self, "instance_type", self.instance_type_id)
        if self.instance_type and not self.instance_type_id:
            object.__setattr__(self, "instance_type_id", self.instance_type)
        if self.available_gpus is not None and self.capacity is None:
            object.__setattr__(self, "capacity", int(self.available_gpus))
        if self.capacity is not None and self.available_gpus is None:
            object.__setattr__(self, "available_gpus", int(self.capacity))
        if self.price_per_hour is not None and self.last_instance_price is None:
            object.__setattr__(self, "last_instance_price", f"${self.price_per_hour:.2f}")
        if self.last_instance_price is not None and self.price_per_hour is None:
            try:
                normalized = self.last_instance_price.strip().lstrip("$")
                object.__setattr__(self, "price_per_hour", float(normalized))
            except Exception:
                pass
        return self
