from __future__ import annotations

from datetime import datetime, timezone
from uuid import NAMESPACE_DNS, UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GPUSpec(BaseModel):
    """Immutable GPU hardware specification used for matching."""

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="NVIDIA", description="GPU vendor")
    model: str = Field(..., description="GPU model (e.g., A100, H100)")
    memory_gb: int = Field(..., gt=0, description="GPU memory in GB")
    memory_type: str = Field(default="", description="Memory type (HBM2e, HBM3, GDDR6)")
    architecture: str = Field(default="", description="GPU architecture (Ampere, Hopper)")
    compute_capability: tuple[int, int] = Field(
        default=(0, 0), description="CUDA compute capability"
    )
    tflops_fp32: float = Field(default=0.0, ge=0, description="FP32 performance in TFLOPS")
    tflops_fp16: float = Field(default=0.0, ge=0, description="FP16 performance in TFLOPS")
    memory_bandwidth_gb_s: float = Field(default=0.0, ge=0, description="Memory bandwidth in GB/s")

    @property
    def canonical_name(self) -> str:
        """Canonical name like: nvidia-a100-80gb."""
        return f"{self.vendor}-{self.model}-{self.memory_gb}gb".lower()

    @property
    def display_name(self) -> str:
        """Human-friendly name like: NVIDIA A100 80GB."""
        return f"{self.vendor} {self.model.upper()} {self.memory_gb}GB"


class CPUSpec(BaseModel):
    """CPU specification."""

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="Intel", description="CPU vendor")
    model: str = Field(default="Xeon", description="CPU model")
    cores: int = Field(..., gt=0, description="Number of CPU cores")
    threads: int = Field(default=0, ge=0, description="Number of threads (0 = same as cores)")
    base_clock_ghz: float = Field(default=0.0, ge=0, description="Base clock speed in GHz")

    @model_validator(mode="after")
    def set_threads_default(self) -> CPUSpec:
        """Default `threads` to `cores` when not specified."""
        if self.threads == 0:
            object.__setattr__(self, "threads", self.cores)
        return self


class MemorySpec(BaseModel):
    """System memory specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., gt=0, description="Memory size in GB")
    type: str = Field(default="DDR4", description="Memory type")
    speed_mhz: int = Field(default=3200, gt=0, description="Memory speed in MHz")
    ecc: bool = Field(default=True, description="ECC memory support")


class StorageSpec(BaseModel):
    """Storage specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., ge=0, description="Storage size in GB")
    type: str = Field(default="NVMe", description="Storage type (NVMe, SSD, HDD)")
    iops: int | None = Field(default=None, ge=0, description="IOPS rating")
    bandwidth_mb_s: int | None = Field(default=None, ge=0, description="Bandwidth in MB/s")


class NetworkSpec(BaseModel):
    """Network specification."""

    model_config = ConfigDict(frozen=True)

    intranode: str = Field(default="", description="Intra-node interconnect (SXM4, SXM5, PCIe)")
    internode: str | None = Field(
        default=None, description="Inter-node network (InfiniBand, Ethernet)"
    )
    bandwidth_gbps: float | None = Field(
        default=None, ge=0, description="Network bandwidth in Gbps"
    )

    @property
    def has_high_speed_interconnect(self) -> bool:
        """True if a high-speed inter-node interconnect is present."""
        return self.internode in {"InfiniBand", "IB", "IB_1600", "IB_3200"}


class InstanceType(BaseModel):
    """Canonical instance type specification (immutable)."""

    model_config = ConfigDict(frozen=True)

    # Hardware specifications
    gpu: GPUSpec
    gpu_count: int = Field(..., gt=0, description="Number of GPUs")
    cpu: CPUSpec
    memory: MemorySpec
    storage: StorageSpec
    network: NetworkSpec

    # Identity and metadata
    id: UUID | None = Field(default=None, description="Unique instance type ID")
    aliases: set[str] = Field(default_factory=set, description="Alternative names")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def compute_id_and_aliases(self) -> InstanceType:
        """Compute a stable ID and default aliases."""
        content = self._canonical_string()
        if not self.id:
            object.__setattr__(self, "id", uuid5(NAMESPACE_DNS, content))
        if not self.aliases:
            object.__setattr__(self, "aliases", self._generate_aliases())
        return self

    def _canonical_string(self) -> str:
        parts = [
            f"gpu:{self.gpu.vendor}-{self.gpu.model}-{self.gpu.memory_gb}gb",
            f"count:{self.gpu_count}",
            f"cpu:{self.cpu.cores}",
            f"mem:{self.memory.size_gb}",
            f"net:{self.network.intranode}-{self.network.internode}",
        ]
        return "|".join(parts)

    def _generate_aliases(self) -> set[str]:
        aliases = set()
        api_style = f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"
        aliases.add(api_style)
        short_form = f"{self.gpu.model.lower()}-{self.gpu.memory_gb}gb"
        aliases.add(short_form)
        with_count = f"{self.gpu_count}x{self.gpu.model.lower()}"
        aliases.add(with_count)
        return aliases

    @property
    def canonical_name(self) -> str:
        return f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"

    @property
    def display_name(self) -> str:
        return f"{self.gpu_count}x {self.gpu.display_name}"

    @property
    def total_gpu_memory_gb(self) -> int:
        return self.gpu.memory_gb * self.gpu_count

    @property
    def total_tflops_fp32(self) -> float:
        return self.gpu.tflops_fp32 * self.gpu_count


class InstanceMatch(BaseModel):
    """Matched instance with price and availability."""

    instance: InstanceType
    region: str
    availability: int = Field(..., ge=0, description="Number of available instances")
    price_per_hour: float = Field(..., ge=0, description="Price in USD per hour")
    match_score: float = Field(default=1.0, ge=0, le=1.0, description="Match quality score")

    @property
    def price_performance(self) -> float:
        """TFLOPS per dollar."""
        if self.price_per_hour > 0:
            return self.instance.total_tflops_fp32 / self.price_per_hour
        return 0.0
