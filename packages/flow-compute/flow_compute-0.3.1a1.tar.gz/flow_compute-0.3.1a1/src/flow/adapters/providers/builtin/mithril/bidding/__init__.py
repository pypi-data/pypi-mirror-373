"""Mithril auction and bidding subsystem.

This package implements the Mithril bidding system:
- Auction discovery and filtering
- Bid specification building
- Bid lifecycle management
"""

from flow.adapters.providers.builtin.mithril.bidding.builder import (
    BidBuilder,
    BidSpecification,
    BidValidationError,
)
from flow.adapters.providers.builtin.mithril.bidding.finder import (
    AuctionCatalogError,
    AuctionFinder,
    AuctionMatcher,
)
from flow.adapters.providers.builtin.mithril.bidding.manager import (
    BidManager,
    BidRequest,
    BidResult,
    BidSubmissionError,
)
from flow.protocols.bidding import AuctionCriteria

__all__ = [
    # Builder
    "BidBuilder",
    "BidSpecification",
    "BidValidationError",
    # Finder
    "AuctionFinder",
    "AuctionCriteria",
    "AuctionMatcher",
    "AuctionCatalogError",
    # Manager
    "BidManager",
    "BidRequest",
    "BidResult",
    "BidSubmissionError",
]
