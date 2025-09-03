"""Domain-level region models and constants.

This module provides provider-agnostic region handling for the Flow SDK.
Provider-specific region mappings should be handled in their respective adapters.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Region:
    """Domain model for a compute region."""

    id: str
    name: str
    display_name: str
    provider: str | None = None
    available: bool = True

    def __str__(self) -> str:
        return self.id


class RegionProvider(Protocol):
    """Protocol for region providers."""

    def list_regions(self) -> list[Region]:
        """List available regions."""
        ...

    def validate_region(self, region_id: str) -> bool:
        """Validate if a region is available."""
        ...


# Common region patterns that many providers use
COMMON_REGION_PATTERNS = [
    "us-east-1",
    "us-west-1",
    "us-west-2",
    "eu-west-1",
    "eu-central-1",
    "ap-southeast-1",
    "ap-northeast-1",
]


def normalize_region_id(region_id: str) -> str:
    """Normalize region ID to a standard format.

    Args:
        region_id: Raw region identifier

    Returns:
        Normalized region identifier
    """
    if not region_id:
        return ""

    # Convert to lowercase and strip whitespace
    normalized = region_id.lower().strip()

    # Handle common variations
    replacements = {
        "_": "-",  # Convert underscores to hyphens
        " ": "-",  # Convert spaces to hyphens
    }

    for old, new in replacements.items():
        normalized = normalized.replace(old, new)

    return normalized


def suggest_region_correction(invalid_region: str, valid_regions: list[str]) -> str | None:
    """Suggest a correction for an invalid region.

    Args:
        invalid_region: The invalid region string
        valid_regions: List of valid region identifiers

    Returns:
        Suggested correction or None if no good match found
    """
    if not invalid_region or not valid_regions:
        return None

    normalized_invalid = normalize_region_id(invalid_region)

    # Check for exact match after normalization
    for valid in valid_regions:
        if normalize_region_id(valid) == normalized_invalid:
            return valid

    # Check for partial matches (e.g., "us-central1" -> "us-central1-a")
    for valid in valid_regions:
        if normalized_invalid in normalize_region_id(valid):
            return valid
        if normalize_region_id(valid).startswith(normalized_invalid):
            return valid

    # Check for common patterns
    if normalized_invalid in ["us-central1", "eu-central1"]:
        suffix_candidate = f"{normalized_invalid}-a"
        for valid in valid_regions:
            if normalize_region_id(valid) == suffix_candidate:
                return valid

    return None
