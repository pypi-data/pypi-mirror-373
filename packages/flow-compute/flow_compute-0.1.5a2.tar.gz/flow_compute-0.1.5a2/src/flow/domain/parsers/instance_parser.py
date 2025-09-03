"""Instance type parsing utilities.

Utilities for parsing and canonicalizing instance type specifications across
the SDK.
"""

import re
from dataclasses import dataclass, field

from flow.domain.models.constants import GPU_SPECS, get_default_gpu_memory
from flow.errors import FlowError


def is_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


class InstanceTypeError(FlowError):
    """Base exception for instance type errors."""

    pass


class InstanceTypeNotFoundError(InstanceTypeError):
    """Raised when an instance type cannot be found."""

    def __init__(self, instance_type: str, available_types: list | None = None):
        self.instance_type = instance_type
        self.available_types = available_types
        message = f"Instance type '{instance_type}' not found"
        if available_types:
            message += f". Available types: {', '.join(available_types[:5])}"
            if len(available_types) > 5:
                message += f" and {len(available_types) - 5} more"
        super().__init__(message)


@dataclass
class InstanceComponents:
    """Parsed components of an instance type specification."""

    gpu_type: str
    gpu_count: int = 1
    memory_gb: int | None = None
    interconnect: str | None = None
    additional_specs: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Normalize components after initialization."""
        self.gpu_type = self.gpu_type.lower()
        if self.interconnect:
            self.interconnect = self.interconnect.lower()


class InstanceParser:
    """Parses and canonicalizes instance type specifications.

    Handles various formats:
    - API format: "a100.80gb.sxm"
    - Multiplier format: "8xa100"
    - Reverse multiplier format: "a100x8"
    - Memory-specific: "h100-80gb"
    - Display format: "8x NVIDIA H100 80GB SXM5"
    """

    # Regex patterns for different formats (order matters - more specific first)
    PATTERNS = {
        # Multiplier format: NxGPU (e.g., "8xa100", "4xh100")
        "multiplier": re.compile(
            r"^(?P<count>\d+)x(?P<gpu>[a-z0-9-]+)"
            r"(?:[-.](?P<memory>\d+)gb)?"
            r"(?:[-.](?P<interconnect>sxm\d?|pcie|nvlink))?$",
            re.IGNORECASE,
        ),
        # Reverse multiplier format: GPUxN (e.g., "a100x8", "h100x4")
        "reverse_multiplier": re.compile(
            r"^(?P<gpu>[a-z0-9-]+)x(?P<count>\d+)"
            r"(?:[-.](?P<memory>\d+)gb)?"
            r"(?:[-.](?P<interconnect>sxm\d?|pcie|nvlink))?$",
            re.IGNORECASE,
        ),
        # API format: gpu.memory.interconnect (e.g., "a100.80gb.sxm")
        "api": re.compile(
            r"^(?P<gpu>[a-z0-9-]+)"
            r"(?:\.(?P<memory>\d+)gb)?"
            r"(?:\.(?P<interconnect>sxm\d?|pcie|nvlink))?$",
            re.IGNORECASE,
        ),
        # Memory-specific format: gpu-memory (e.g., "a100-80gb")
        "memory": re.compile(
            r"^(?P<gpu>[a-z0-9-]+)-(?P<memory>\d+)gb"
            r"(?:[-.](?P<interconnect>sxm\d?|pcie|nvlink))?$",
            re.IGNORECASE,
        ),
        # Display format: "8x NVIDIA H100 80GB SXM5"
        "display": re.compile(
            r"^(?:(?P<count>\d+)x\s+)?"
            r"(?:NVIDIA\s+)?"
            r"(?P<gpu>[A-Z0-9-]+)"
            r"(?:\s+(?P<memory>\d+)GB)?"
            r"(?:\s+(?P<interconnect>SXM\d?|PCIe|NVLink))?$",
            re.IGNORECASE,
        ),
        # Mithril API format: gpu-memory.interconnect.countx (e.g., "a100-80gb.sxm.2x")
        "mithril_api": re.compile(
            r"^(?P<gpu>[a-z0-9]+)-(?P<memory>\d+)gb"
            r"(?:\.(?P<interconnect>sxm|pcie|nvlink))?"
            r"(?:\.(?P<count>\d+)x)?$",
            re.IGNORECASE,
        ),
    }

    @classmethod
    def parse(cls, instance_spec: str) -> InstanceComponents:
        """Parse instance specification into components.

        Args:
            instance_spec: Instance type string in any supported format

        Returns:
            InstanceComponents with parsed values

        Raises:
            InstanceTypeError: If format cannot be parsed
        """
        if not instance_spec:
            raise InstanceTypeError("Instance specification cannot be empty")

        # Clean input
        spec = instance_spec.strip()

        # Try each pattern
        for format_name, pattern in cls.PATTERNS.items():
            match = pattern.match(spec)
            if match:
                groups = match.groupdict()

                # Extract components
                gpu_type = groups.get("gpu", "").lower()
                gpu_count = int(groups.get("count", 1))
                memory_str = groups.get("memory")
                memory_gb = int(memory_str) if memory_str else None
                interconnect = (
                    groups.get("interconnect", "").lower() if groups.get("interconnect") else None
                )

                # Validate GPU type
                if not cls._is_valid_gpu(gpu_type):
                    raise InstanceTypeError(f"Unknown GPU type: {gpu_type}")

                # Get default memory if not specified
                if memory_gb is None:
                    memory_gb = get_default_gpu_memory(gpu_type)

                return InstanceComponents(
                    gpu_type=gpu_type,
                    gpu_count=gpu_count,
                    memory_gb=memory_gb,
                    interconnect=interconnect,
                )

        # No pattern matched
        raise InstanceTypeError(
            f"Invalid instance specification format: '{instance_spec}'. "
            f"Expected formats: 'a100.80gb.sxm', '8xa100', 'h100-80gb', etc."
        )

    @classmethod
    def canonicalize(cls, instance_spec: str) -> str:
        """Convert instance specification to canonical format.

        Args:
            instance_spec: Instance type in any format

        Returns:
            Canonical format (e.g., "8xa100.80gb.sxm")
        """
        components = cls.parse(instance_spec)
        return cls.to_canonical(components)

    @staticmethod
    def to_canonical(components: InstanceComponents) -> str:
        """Convert components to canonical format."""
        parts = []

        # Add count prefix if > 1
        if components.gpu_count > 1:
            parts.append(f"{components.gpu_count}x{components.gpu_type}")
        else:
            parts.append(components.gpu_type)

        # Add memory if not default
        default_memory = get_default_gpu_memory(components.gpu_type)
        if components.memory_gb and components.memory_gb != default_memory:
            parts.append(f"{components.memory_gb}gb")

        # Add interconnect if specified
        if components.interconnect:
            parts.append(components.interconnect)

        return ".".join(parts)

    @staticmethod
    def _is_valid_gpu(gpu_type: str) -> bool:
        """Check if GPU type is valid."""
        return gpu_type.lower() in GPU_SPECS


# Export convenience functions
def parse_instance_type(instance_spec: str) -> InstanceComponents:
    """Parse instance type specification."""
    return InstanceParser.parse(instance_spec)


def canonicalize_instance_type(instance_spec: str) -> str:
    """Get canonical form of instance type."""
    return InstanceParser.canonicalize(instance_spec)


def infer_gpu_family_from_name(name: str) -> str | None:
    """Infer a GPU family token from a provider instance type display name.

    Keeps logic minimal and centralized. Returns a normalized family token
    such as "h100" or "a100" when recognized; otherwise None.
    """
    try:
        s = (name or "").lower()
    except Exception:
        return None
    for token in ("h100", "a100"):
        if token in s:
            return token
    return None
