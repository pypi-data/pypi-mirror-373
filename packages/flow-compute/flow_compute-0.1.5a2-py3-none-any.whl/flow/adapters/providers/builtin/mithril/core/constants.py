"""Mithril-specific constants and configuration values.

Centralizes provider constants for maintainability and easier updates.
"""

import os
from enum import Enum
from typing import Any

# ==================== Regions ====================
# Verified from Mithril API /v2/spot/availability endpoint
# Valid regions; allow expansion via env for tests or pre-release regions
_EXTRA_REGIONS = os.getenv("MITHRIL_EXTRA_REGIONS", "").strip()
# Keep list in sync with API; prefer primary zones ("-a") when available
VALID_REGIONS: list[str] = [
    "us-central1-a",
    "us-central1-b",
    "us-central2-a",
    "eu-central1-a",
    "eu-central1-b",
]
if _EXTRA_REGIONS:
    for r in [s.strip() for s in _EXTRA_REGIONS.split(",") if s.strip()]:
        if r not in VALID_REGIONS:
            VALID_REGIONS.append(r)

# Startup Script Limits
# Mithril has a 10,000 character limit for uncompressed startup scripts
# Source: https://docs.mithril.ai/compute-and-storage/startup-scripts
STARTUP_SCRIPT_MAX_SIZE = 10 * 1000  # 10,000 characters

# Log Locations
# Mithril expects logs at specific locations for compatibility
MITHRIL_LOG_DIR = os.getenv("MITHRIL_LOG_DIR", "/var/log/foundry")
MITHRIL_STARTUP_LOG = f"{MITHRIL_LOG_DIR}/startup_script.log"
V1_USERS_TEAMMATES_PATH_TEMPLATE = "/users/{user_id}/teammates"


# Flow's internal log locations
FLOW_LOG_DIR = os.getenv("FLOW_LOG_DIR", "/var/log/flow")

# ==================== Storage ====================
# Disk interface types from Mithril API
# Note: UI shows "File share" but API expects "File"
DISK_INTERFACE_BLOCK = "Block"
DISK_INTERFACE_FILE = "File"

VALID_DISK_INTERFACES = [DISK_INTERFACE_BLOCK, DISK_INTERFACE_FILE]


# ==================== Instance Status ====================
class InstanceStatus(str, Enum):
    """Instance lifecycle statuses from API."""

    PENDING = "STATUS_PENDING"
    NEW = "STATUS_NEW"
    CONFIRMED = "STATUS_CONFIRMED"
    SCHEDULED = "STATUS_SCHEDULED"
    INITIALIZING = "STATUS_INITIALIZING"
    STARTING = "STATUS_STARTING"
    RUNNING = "STATUS_RUNNING"
    STOPPING = "STATUS_STOPPING"
    STOPPED = "STATUS_STOPPED"
    TERMINATED = "STATUS_TERMINATED"
    RELOCATING = "STATUS_RELOCATING"
    PREEMPTING = "STATUS_PREEMPTING"
    PREEMPTED = "STATUS_PREEMPTED"
    REPLACED = "STATUS_REPLACED"


# ==================== Bid Status ====================
class BidStatus(str, Enum):
    """Bid/Task statuses from API."""

    OPEN = "Open"
    ALLOCATED = "Allocated"
    PREEMPTING = "Preempting"
    TERMINATED = "Terminated"
    PAUSED = "Paused"
    REPLACED = "Replaced"


# ==================== Order Types ====================
class OrderType(str, Enum):
    """Types of orders in Mithril."""

    BID = "Bid"
    RESERVATION = "Reservation"


# ==================== Sort Options ====================
class SortDirection(str, Enum):
    """Sort directions for API queries."""

    ASC = "asc"
    DESC = "desc"


# Instance Type Mappings
# Verified from Mithril API /v2/instance-types endpoint (2025-07-20)
INSTANCE_TYPE_MAPPINGS = {
    # A100 mappings
    "a100": "it_MsIRhxj3ccyVWGfP",  # Default to 1x
    "1xa100": "it_MsIRhxj3ccyVWGfP",
    "2xa100": "it_5M6aGxGovNeX5ltT",
    "4xa100": "it_fK7Cx6TVhOK5ZfXT",
    "8xa100": "it_J7OyNf9idfImLIFo",
    # Mithril format also supported
    "a100-80gb.sxm.1x": "it_MsIRhxj3ccyVWGfP",
    "a100-80gb.sxm.2x": "it_5M6aGxGovNeX5ltT",
    "a100-80gb.sxm.4x": "it_fK7Cx6TVhOK5ZfXT",
    "a100-80gb.sxm.8x": "it_J7OyNf9idfImLIFo",
    # H100 mappings
    "h100": "it_5ECSoHQjLBzrp5YM",  # Default to 8x
    "8xh100": "it_5ECSoHQjLBzrp5YM",
    # Accept common shorthand variants for H100; normalize to 8x
    "1xh100": "it_5ECSoHQjLBzrp5YM",
    "2xh100": "it_5ECSoHQjLBzrp5YM",
    "4xh100": "it_5ECSoHQjLBzrp5YM",
    "h100-80gb.sxm.8x": "it_5ECSoHQjLBzrp5YM",
    # Note: it_XqgKWbhZ5gznAYsG also maps to h100-80gb.sxm.8x in API
}

# Reverse mapping for display purposes
# Verified from Mithril API /v2/instance-types endpoint (2025-07-20)
INSTANCE_TYPE_NAMES = {
    "it_MsIRhxj3ccyVWGfP": "a100-80gb.sxm.1x",
    "it_5M6aGxGovNeX5ltT": "a100-80gb.sxm.2x",
    "it_fK7Cx6TVhOK5ZfXT": "a100-80gb.sxm.4x",
    "it_J7OyNf9idfImLIFo": "a100-80gb.sxm.8x",
    "it_5ECSoHQjLBzrp5YM": "h100-80gb.sxm.8x",
    "it_XqgKWbhZ5gznAYsG": "h100-80gb.sxm.8x",  # Another H100 variant
}

# API Endpoints
import os

MITHRIL_API_BASE_URL = os.getenv("MITHRIL_API_URL", "https://api.mithril.ai")
MITHRIL_API_VERSION = "v2"
MITHRIL_WEB_BASE_URL = os.getenv("MITHRIL_WEB_URL", "https://app.mithril.ai")
MITHRIL_DOCS_URL = os.getenv("MITHRIL_DOCS_URL", "https://docs.mithril.ai")
MITHRIL_STATUS_URL = os.getenv("MITHRIL_STATUS_URL", "https://status.mithril.ai")
# Marketing site base URL for public pages (e.g., pricing)
MITHRIL_MARKETING_URL = os.getenv("MITHRIL_MARKETING_URL", "https://mithril.ai")

# Resource Limits
MAX_VOLUMES_PER_INSTANCE = 20  # AWS limit that Mithril inherits
MAX_INSTANCES_PER_TASK = 256
MAX_VOLUME_SIZE_GB = 16384  # 16TB

# Timeouts
DEFAULT_HTTP_TIMEOUT = 30  # seconds
VOLUME_DELETE_TIMEOUT = 120  # seconds, volume deletion can be slow

# ==================== Instance Provisioning Times ====================
# Mithril instances can take significant time to provision and become ready
# These constants centralize timing assumptions for better maintainability

# Time for instance to get allocated and receive an IP address
INSTANCE_IP_WAIT_SECONDS = 300  # 5 minutes max to get IP
INSTANCE_IP_CHECK_INTERVAL = 5  # Check every 5 seconds

# Time for SSH to become available after IP is assigned
SSH_READY_WAIT_SECONDS = 600  # 10 minutes max for SSH readiness
SSH_CHECK_INTERVAL = 2  # Check every 2 seconds

# Total expected provisioning time (for user messages)
EXPECTED_PROVISION_MINUTES = 20  # Mithril instances typically take up to 20 minutes

# Quick SSH retry for commands (logs, etc)
SSH_QUICK_RETRY_ATTEMPTS = 5
SSH_QUICK_RETRY_MAX_SECONDS = 30  # 30 seconds total for quick retries

# User Cache
USER_CACHE_TTL = 3600  # 1 hour TTL for user information cache

# SSH Configuration
DEFAULT_SSH_USER = os.getenv("MITHRIL_SSH_USER", "ubuntu")
DEFAULT_SSH_PORT = int(os.getenv("MITHRIL_SSH_PORT", "22"))

# Volume Configuration
VOLUME_ID_PREFIX = "vol_"

# Status Mappings
# Map Mithril status strings to TaskStatus enum values
STATUS_MAPPINGS = {
    # Queueing/starting states
    "pending": "PENDING",
    "open": "PENDING",  # Mithril uses "Open" for pending bids
    "provisioning": "PENDING",  # Waiting for allocation
    "scheduled": "PENDING",  # Occasionally returned for instances
    # Active states
    "allocated": "RUNNING",  # Mithril uses "Allocated" for running
    "running": "RUNNING",
    # Transitional/administrative states
    "paused": "PAUSED",
    "preempting": "PREEMPTING",
    # Terminal states
    "completed": "COMPLETED",
    "failed": "FAILED",
    "cancelled": "CANCELLED",
    # Mithril returns "Terminated" for ended bids. Unit tests expect COMPLETED at list time.
    "terminated": "COMPLETED",
    "replaced": "CANCELLED",
}

# Supported Regions
# Use VALID_REGIONS directly
SUPPORTED_REGIONS = VALID_REGIONS

# Default Region (canonical env var only)
DEFAULT_REGION = os.getenv("MITHRIL_REGION", "us-central1-a")

# ==================== Instance Types ====================
# Note: These should be fetched dynamically from /v2/instance-types
# This is just for reference/examples
EXAMPLE_INSTANCE_TYPES = [
    "h100.80gb.sxm",
    "a100.80gb.sxm",
    "a40.48gb.pcie",
]

# ==================== GPU Instance Detection ====================
# Patterns for detecting GPU instances based on instance type names
# Used for determining when to add --gpus flag and install nvidia-container-toolkit
GPU_INSTANCE_PATTERNS = [
    # Common GPU instance identifiers
    "a100",
    "a10",
    "h100",
    "v100",
    "t4",
    "l4",
    "a40",
    "p100",
    "k80",
    "m60",
    "rtx",
    "tesla",
    "h200",
    "b200",
    "gb200",
]

# ==================== API Defaults ====================
DEFAULT_DISK_INTERFACE = DISK_INTERFACE_BLOCK

# ==================== Validation Messages ====================
# Centralized validation help messages
VALIDATION_MESSAGES = {
    "region": {
        "help": "Valid regions",
        "examples": VALID_REGIONS,
        "note": "Additional regions may be available. Check Mithril documentation.",
    },
    "disk_interface": {
        "help": "Valid disk interfaces",
        "examples": [
            f"{DISK_INTERFACE_BLOCK} (high-performance block storage)",
            f"{DISK_INTERFACE_FILE} (shared file storage)",
        ],
    },
    "instance_type": {
        "help": "Example instance types",
        "examples": [
            "a100-80gb.sxm.4x (4x A100 GPUs)",
            "h100-80gb.sxm.8x (8x H100 GPUs)",
            "t4-16gb.pcie.1x (1x T4 GPU)",
        ],
        "note": "Run 'flow instances' to see all available types",
    },
}


def get_validation_help(field: str) -> dict[str, Any]:
    """Get validation help message for a field.

    Args:
        field: Field name to get help for

    Returns:
        Dictionary with help, examples, and optional note
    """
    return VALIDATION_MESSAGES.get(field, {})


def format_validation_help(field: str) -> list[str]:
    """Format validation help as list of strings for error messages.

    Args:
        field: Field name to format help for

    Returns:
        List of formatted help strings
    """
    help_info = get_validation_help(field)
    if not help_info:
        return []

    lines = []

    if help_info.get("help"):
        lines.append(f"{help_info['help']}:")

    for example in help_info.get("examples", []):
        lines.append(f"  - {example}")

    if help_info.get("note"):
        if lines:
            lines.append("")
        lines.append(help_info["note"])

    return lines
