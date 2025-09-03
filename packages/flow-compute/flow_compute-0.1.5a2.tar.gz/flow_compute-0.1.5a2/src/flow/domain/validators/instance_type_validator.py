"""Instance type validation utilities.

Helpers to validate and normalize instance type names across providers,
preventing mismatches between user input and provider-specific formats.
"""

import logging
import re

logger = logging.getLogger(__name__)


class InstanceTypeValidator:
    """Validates and normalizes instance type names."""

    # Common GPU instance patterns
    GPU_PATTERNS = {
        # NVIDIA GPUs
        "a100": ["a100", "a100-40gb", "a100-80gb", "a100.40gb", "a100.80gb"],
        "h100": ["h100", "h100-80gb", "h100.80gb", "h100-pcie", "h100-sxm"],
        "v100": ["v100", "v100-16gb", "v100-32gb", "v100.16gb", "v100.32gb"],
        "t4": ["t4", "t4-16gb", "nvidia-t4", "gpu.nvidia.t4"],
        "l4": ["l4", "l4-24gb", "nvidia-l4", "gpu.nvidia.l4"],
        # Multi-GPU variants
        "2xa100": ["2xa100", "2x-a100", "a100x2", "a100.2x"],
        "4xa100": ["4xa100", "4x-a100", "a100x4", "a100.4x"],
        "8xa100": ["8xa100", "8x-a100", "a100x8", "a100.8x"],
        "8xh100": ["8xh100", "8x-h100", "h100x8", "h100.8x", "h100-80gb.sxm.8x"],
    }

    # CPU instance patterns
    CPU_PATTERNS = {
        "small": ["small", "cpu.small", "cpu-small"],
        "medium": ["medium", "cpu.medium", "cpu-medium"],
        "large": ["large", "cpu.large", "cpu-large"],
        "xlarge": ["xlarge", "cpu.xlarge", "cpu-xlarge"],
        "2xlarge": ["2xlarge", "cpu.2xlarge", "cpu-2xlarge"],
    }

    # Provider-specific mappings
    PROVIDER_MAPPINGS = {
        "mithril": {
            # Mithril uses simplified names
            "a100": "a100",
            "2xa100": "2xa100",
            "4xa100": "4xa100",
            "8xa100": "8xa100",
            "h100": "h100",
            "8xh100": "8xh100",
            "h100-80gb.sxm.8x": "8xh100",  # Normalize to simplified form
        },
        "aws": {
            # AWS uses instance family names
            "a100": "p4d.24xlarge",
            "8xa100": "p4de.24xlarge",
            "v100": "p3.2xlarge",
        },
        "gcp": {
            # GCP uses machine type names
            "a100": "a2-highgpu-1g",
            "v100": "n1-highmem-8",
            "t4": "n1-standard-4",
        },
    }

    @classmethod
    def normalize_instance_type(cls, instance_type: str, provider: str | None = None) -> str:
        """Normalize instance type to canonical form.

        Args:
            instance_type: User-provided instance type
            provider: Optional provider name for provider-specific normalization

        Returns:
            Normalized instance type string
        """
        if not instance_type:
            raise ValueError("Instance type cannot be empty")

        # Convert to lowercase for comparison
        normalized = instance_type.lower().strip()

        # Check GPU patterns
        for canonical, variants in cls.GPU_PATTERNS.items():
            if normalized in variants:
                # If provider specified, use provider mapping
                if provider and provider in cls.PROVIDER_MAPPINGS:
                    return cls.PROVIDER_MAPPINGS[provider].get(canonical, canonical)
                return canonical

        # Check CPU patterns
        for canonical, variants in cls.CPU_PATTERNS.items():
            if normalized in variants:
                return canonical

        # Check provider-specific direct mappings
        if provider and provider in cls.PROVIDER_MAPPINGS:
            mappings = cls.PROVIDER_MAPPINGS[provider]
            if normalized in mappings:
                return mappings[normalized]

        # Return as-is if no mapping found
        logger.warning(f"Unknown instance type: {instance_type}")
        return instance_type

    @classmethod
    def validate_instance_type(
        cls, instance_type: str, provider: str | None = None
    ) -> tuple[bool, str | None]:
        """Validate if instance type is recognized.

        Args:
            instance_type: Instance type to validate
            provider: Optional provider name

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not instance_type:
            return False, "Instance type cannot be empty"

        normalized = instance_type.lower().strip()

        # Check if it's in any known pattern
        all_known_types = set()

        # Add GPU types
        for variants in cls.GPU_PATTERNS.values():
            all_known_types.update(variants)

        # Add CPU types
        for variants in cls.CPU_PATTERNS.values():
            all_known_types.update(variants)

        # Add provider-specific types
        for mappings in cls.PROVIDER_MAPPINGS.values():
            all_known_types.update(mappings.keys())
            all_known_types.update(mappings.values())

        if normalized in all_known_types:
            return True, None

        # Try to provide helpful suggestion
        suggestion = cls._suggest_instance_type(normalized, all_known_types)
        if suggestion:
            return False, f"Unknown instance type '{instance_type}'. Did you mean '{suggestion}'?"
        else:
            return False, f"Unknown instance type '{instance_type}'"

    @classmethod
    def _suggest_instance_type(cls, user_input: str, known_types: set[str]) -> str | None:
        """Suggest a similar instance type based on user input."""
        # Simple Levenshtein distance for suggestions
        from difflib import get_close_matches

        matches = get_close_matches(user_input, known_types, n=1, cutoff=0.6)
        return matches[0] if matches else None

    @classmethod
    def is_gpu_instance(cls, instance_type: str) -> bool:
        """Check if instance type is a GPU instance."""
        normalized = instance_type.lower().strip()

        # Check direct GPU patterns
        for variants in cls.GPU_PATTERNS.values():
            if normalized in variants:
                return True

        # Check common GPU indicators
        gpu_indicators = ["gpu", "a100", "h100", "v100", "t4", "l4", "a10", "a40"]
        return any(indicator in normalized for indicator in gpu_indicators)

    @classmethod
    def get_gpu_count(cls, instance_type: str) -> int:
        """Get the number of GPUs for an instance type.

        Returns:
            Number of GPUs, or 0 for CPU instances
        """
        normalized = instance_type.lower().strip()

        # Check for multi-GPU patterns
        multi_gpu_pattern = re.match(r"(\d+)x[a-z]\d+", normalized)
        if multi_gpu_pattern:
            return int(multi_gpu_pattern.group(1))

        # Check reverse pattern (e.g., "a100x2")
        reverse_pattern = re.match(r"[a-z]\d+x(\d+)", normalized)
        if reverse_pattern:
            return int(reverse_pattern.group(1))

        # Single GPU instance
        if cls.is_gpu_instance(normalized):
            return 1

        return 0

    @classmethod
    def get_all_valid_types(cls, provider: str | None = None) -> set[str]:
        """Get all valid instance types for a provider."""
        valid_types = set()

        if provider and provider in cls.PROVIDER_MAPPINGS:
            # Return provider-specific types
            mappings = cls.PROVIDER_MAPPINGS[provider]
            valid_types.update(mappings.values())
        else:
            # Return all canonical types
            valid_types.update(cls.GPU_PATTERNS.keys())
            valid_types.update(cls.CPU_PATTERNS.keys())

        return valid_types
