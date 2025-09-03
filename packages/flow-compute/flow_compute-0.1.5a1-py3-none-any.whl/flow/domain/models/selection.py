"""Domain model for selection outcomes.

This module contains the SelectionOutcome model used across providers
to represent the result of region and instance selection operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SelectionOutcome:
    """Normalized outcome for region/instance selection.

    This domain model represents the result of a region and instance selection
    process, used by various provider implementations to communicate selection
    results in a consistent format.

    Attributes:
        region: Selected region identifier or None if selection failed
        auction: Selected auction object or None
        instance_type_id: Provider-specific instance type id (e.g., FID) or None
        candidate_regions: Regions considered during selection (may be empty)
        source: Selection method used (e.g., 'bids' or 'availability')
    """

    region: str | None
    auction: Any | None
    instance_type_id: str | None
    candidate_regions: list[str]
    source: str  # Common values: 'bids', 'availability'

    def is_successful(self) -> bool:
        """Check if selection was successful.

        Returns:
            True if a region was selected, False otherwise
        """
        return self.region is not None

    def has_auction(self) -> bool:
        """Check if selection includes auction data.

        Returns:
            True if auction data is present, False otherwise
        """
        return self.auction is not None
