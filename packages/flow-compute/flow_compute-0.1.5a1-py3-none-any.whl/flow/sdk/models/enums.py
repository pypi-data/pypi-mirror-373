"""Enumerations for Flow API models (backwards compatible)."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    PREEMPTING = "preempting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstanceStatus(str, Enum):
    """Status of a compute instance."""

    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"


class ReservationStatus(str, Enum):
    """Reservation lifecycle states."""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EXPIRED = "expired"
    FAILED = "failed"


class StorageInterface(str, Enum):
    """Storage interface type."""

    BLOCK = "block"
    FILE = "file"
