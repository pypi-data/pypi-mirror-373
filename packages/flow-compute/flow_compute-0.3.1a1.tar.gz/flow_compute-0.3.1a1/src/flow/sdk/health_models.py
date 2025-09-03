"""Typed models for GPU and system health monitoring (GPUd-compatible).

Examples:
    Build a snapshot and compute derived values:
        >>> from datetime import datetime
        >>> snap = NodeHealthSnapshot(
        ...     task_id="t1", task_name="train", instance_id="i1",
        ...     instance_type="a100", timestamp=datetime.utcnow(),
        ...     gpud_healthy=True,
        ... )
        >>> snap.gpu_count
        0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Overall health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentHealth(str, Enum):
    """Individual component health states."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class GPUProcess:
    """GPU process information."""

    pid: int
    name: str
    memory_mb: int
    gpu_index: int


@dataclass
class GPUMetric:
    """GPU metrics as reported by GPUd."""

    gpu_index: int
    uuid: str
    name: str
    temperature_c: float
    power_draw_w: float
    power_limit_w: float
    memory_used_mb: int
    memory_total_mb: int
    gpu_utilization_pct: float
    sm_occupancy_pct: float
    clock_mhz: int
    max_clock_mhz: int
    ecc_errors: int = 0
    xid_events: list[str] = field(default_factory=list)
    nvlink_status: str = "healthy"
    processes: list[GPUProcess] = field(default_factory=list)

    @property
    def memory_utilization_pct(self) -> float:
        """Memory utilization in percent."""
        if self.memory_total_mb == 0:
            return 0.0
        return (self.memory_used_mb / self.memory_total_mb) * 100

    @property
    def power_utilization_pct(self) -> float:
        """Power utilization in percent."""
        if self.power_limit_w == 0:
            return 0.0
        return (self.power_draw_w / self.power_limit_w) * 100

    @property
    def is_throttling(self) -> bool:
        """True if clock rate indicates throttling."""
        return self.clock_mhz < self.max_clock_mhz * 0.9


@dataclass
class SystemMetrics:
    """System-level metrics (CPU, memory, disk, network)."""

    cpu_usage_pct: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_pct: float
    network_rx_mbps: float = 0.0
    network_tx_mbps: float = 0.0
    open_file_descriptors: int = 0
    load_average: list[float] = field(default_factory=list)

    @property
    def memory_utilization_pct(self) -> float:
        """Memory utilization in percent."""
        if self.memory_total_gb == 0:
            return 0.0
        return (self.memory_used_gb / self.memory_total_gb) * 100


@dataclass
class HealthState:
    """Component health state."""

    component: str
    health: ComponentHealth
    message: str
    severity: str = "info"
    timestamp: datetime | None = None


@dataclass
class SystemEvent:
    """System event (error, warning, info)."""

    timestamp: datetime
    component: str
    level: str  # error, warning, info
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeHealthSnapshot:
    """Complete health snapshot for a node."""

    # Identity
    task_id: str
    task_name: str
    instance_id: str
    instance_type: str
    timestamp: datetime

    # GPUd status
    gpud_healthy: bool
    gpud_version: str | None = None

    # Machine info from GPUd /machine-info
    machine_info: dict[str, Any] = field(default_factory=dict)

    # Metrics
    gpu_metrics: list[GPUMetric] = field(default_factory=list)
    system_metrics: SystemMetrics | None = None

    # Health states from GPUd /v1/states
    health_states: list[HealthState] = field(default_factory=list)

    # Events from GPUd /v1/events
    events: list[SystemEvent] = field(default_factory=list)

    # Computed health
    health_score: float = 1.0
    health_status: HealthStatus = HealthStatus.UNKNOWN

    @property
    def gpu_count(self) -> int:
        """Number of GPUs on this node."""
        return len(self.gpu_metrics)

    @property
    def has_critical_events(self) -> bool:
        """True if any critical events are present."""
        return any(e.level == "error" for e in self.events)

    @property
    def unhealthy_components(self) -> list[str]:
        """List components that are degraded or unhealthy."""
        return [
            state.component
            for state in self.health_states
            if state.health in (ComponentHealth.UNHEALTHY, ComponentHealth.DEGRADED)
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dict."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "instance_id": self.instance_id,
            "instance_type": self.instance_type,
            "timestamp": self.timestamp.isoformat(),
            "gpud_healthy": self.gpud_healthy,
            "gpud_version": self.gpud_version,
            "machine_info": self.machine_info,
            "gpu_metrics": [
                {
                    "gpu_index": g.gpu_index,
                    "uuid": g.uuid,
                    "name": g.name,
                    "temperature_c": g.temperature_c,
                    "power_draw_w": g.power_draw_w,
                    "power_limit_w": g.power_limit_w,
                    "memory_used_mb": g.memory_used_mb,
                    "memory_total_mb": g.memory_total_mb,
                    "gpu_utilization_pct": g.gpu_utilization_pct,
                    "sm_occupancy_pct": g.sm_occupancy_pct,
                    "clock_mhz": g.clock_mhz,
                    "max_clock_mhz": g.max_clock_mhz,
                    "ecc_errors": g.ecc_errors,
                    "xid_events": g.xid_events,
                    "nvlink_status": g.nvlink_status,
                    "processes": [
                        {
                            "pid": p.pid,
                            "name": p.name,
                            "memory_mb": p.memory_mb,
                            "gpu_index": p.gpu_index,
                        }
                        for p in g.processes
                    ],
                }
                for g in self.gpu_metrics
            ],
            "system_metrics": (
                {
                    "cpu_usage_pct": self.system_metrics.cpu_usage_pct,
                    "memory_used_gb": self.system_metrics.memory_used_gb,
                    "memory_total_gb": self.system_metrics.memory_total_gb,
                    "disk_usage_pct": self.system_metrics.disk_usage_pct,
                    "network_rx_mbps": self.system_metrics.network_rx_mbps,
                    "network_tx_mbps": self.system_metrics.network_tx_mbps,
                    "open_file_descriptors": self.system_metrics.open_file_descriptors,
                    "load_average": self.system_metrics.load_average,
                }
                if self.system_metrics
                else None
            ),
            "health_states": [
                {
                    "component": s.component,
                    "health": s.health.value,
                    "message": s.message,
                    "severity": s.severity,
                    "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                }
                for s in self.health_states
            ],
            "events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "component": e.component,
                    "level": e.level,
                    "message": e.message,
                    "details": e.details,
                }
                for e in self.events
            ],
            "health_score": self.health_score,
            "health_status": self.health_status.value,
        }


@dataclass
class FleetHealthSummary:
    """Aggregate fleet health summary."""

    timestamp: datetime
    total_nodes: int
    healthy_nodes: int
    degraded_nodes: int
    critical_nodes: int

    # Aggregate metrics
    total_gpus: int
    healthy_gpus: int
    avg_gpu_temperature: float
    avg_gpu_utilization: float
    avg_gpu_memory_utilization: float

    # Top issues
    critical_issues: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    # Legacy nodes (without GPUd monitoring)
    legacy_nodes: int = 0

    @property
    def health_percentage(self) -> float:
        """Overall healthy-nodes percentage."""
        if self.total_nodes == 0:
            return 0.0
        return (self.healthy_nodes / self.total_nodes) * 100

    @property
    def has_critical_issues(self) -> bool:
        """True if any node is critical or critical issues exist."""
        return self.critical_nodes > 0 or len(self.critical_issues) > 0


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""

    component: str
    status: str  # pass, fail, warning
    message: str
    details: str | None = None
    suggestion: str | None = None
