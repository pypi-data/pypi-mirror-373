"""Domain-level region validation utilities.

This module provides provider-agnostic region validation.
Provider-specific validation should be handled by the respective adapters.
"""

from flow.domain.models.regions import suggest_region_correction


def validate_region(
    region: str | None, valid_regions: list[str] | None = None
) -> tuple[bool, str | None]:
    """Validate region and suggest correction for common mistakes.

    Args:
        region: Region string to validate
        valid_regions: List of valid regions (provider-specific)

    Returns:
        (is_valid, suggested_correction)
    """
    if not region:
        return True, None  # Region is optional

    if not valid_regions:
        # Without provider-specific regions, we can't validate
        return True, None

    if region in valid_regions:
        return True, None

    # Try to suggest a correction
    suggestion = suggest_region_correction(region, valid_regions)
    return False, suggestion


def list_regions(provider_regions: list[str] | None = None) -> list[str]:
    """Get list of valid regions.

    Args:
        provider_regions: Provider-specific regions

    Returns:
        List of valid regions
    """
    if provider_regions:
        return provider_regions.copy()

    # Return empty list if no provider regions specified
    # This forces explicit provider region handling
    return []
