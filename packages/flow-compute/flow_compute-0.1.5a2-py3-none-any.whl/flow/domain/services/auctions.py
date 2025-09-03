"""Domain service for auction-based resource allocation.

This module provides the core auction logic for providers that use
bidding mechanisms for resource allocation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol


class AuctionStatus(Enum):
    """Status of an auction."""

    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class Auction:
    """Domain model for a resource auction."""

    id: str
    instance_type: str
    region: str
    status: AuctionStatus
    current_price: float
    minimum_price: float
    created_at: datetime
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = None

    def is_active(self) -> bool:
        """Check if auction is currently active."""
        if self.status != AuctionStatus.OPEN:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

    def time_remaining(self) -> timedelta | None:
        """Get time remaining in auction."""
        if not self.expires_at:
            return None
        remaining = self.expires_at - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


@dataclass
class Bid:
    """Domain model for a bid in an auction."""

    id: str
    auction_id: str
    price: float
    quantity: int = 1
    created_at: datetime | None = None
    status: str = "pending"
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AuctionResult:
    """Result of an auction evaluation."""

    auction_id: str
    winning_bid: Bid | None
    final_price: float
    allocated_quantity: int
    status: str  # "won", "lost", "partial"

    @property
    def is_successful(self) -> bool:
        return self.status in ["won", "partial"]


class BiddingStrategy(Protocol):
    """Protocol for bidding strategies."""

    def calculate_bid(
        self,
        auction: Auction,
        max_price: float | None = None,
        historical_prices: list[float] | None = None,
    ) -> float:
        """Calculate optimal bid for an auction."""
        ...


class SimpleBiddingStrategy:
    """Simple bidding strategy based on margins."""

    def __init__(self, margin: float = 0.1):
        """Initialize with margin above current price.

        Args:
            margin: Margin to bid above current price (0.1 = 10%)
        """
        self.margin = margin

    def calculate_bid(
        self,
        auction: Auction,
        max_price: float | None = None,
        historical_prices: list[float] | None = None,
    ) -> float:
        """Calculate bid as current price plus margin."""
        bid = auction.current_price * (1 + self.margin)

        # Respect limit price (max price) if specified
        if max_price is not None:
            bid = min(bid, max_price)

        # Ensure at least minimum price
        return max(bid, auction.minimum_price)


class AdaptiveBiddingStrategy:
    """Adaptive bidding based on historical data and competition."""

    def calculate_bid(
        self,
        auction: Auction,
        max_price: float | None = None,
        historical_prices: list[float] | None = None,
    ) -> float:
        """Calculate bid based on historical patterns.

        Uses historical price data to predict optimal bid:
        - If prices trending up, bid more aggressively
        - If prices stable, bid at average + small margin
        - If prices trending down, bid conservatively
        """
        # Start with current price
        base_bid = auction.current_price

        if historical_prices and len(historical_prices) >= 3:
            # Calculate trend
            recent_avg = sum(historical_prices[-3:]) / 3
            older_avg = (
                sum(historical_prices[:-3]) / len(historical_prices[:-3])
                if len(historical_prices) > 3
                else recent_avg
            )

            if recent_avg > older_avg * 1.05:
                # Prices trending up, bid aggressively
                base_bid = recent_avg * 1.15
            elif recent_avg < older_avg * 0.95:
                # Prices trending down, bid conservatively
                base_bid = recent_avg * 1.05
            else:
                # Stable prices, bid at average + margin
                base_bid = recent_avg * 1.10
        else:
            # No history, use simple margin
            base_bid = auction.current_price * 1.10

        # Apply constraints
        if max_price is not None:
            base_bid = min(base_bid, max_price)

        return max(base_bid, auction.minimum_price)


class AuctionService:
    """Domain service for auction operations."""

    def __init__(self, strategy: BiddingStrategy | None = None):
        """Initialize with optional bidding strategy.

        Args:
            strategy: Bidding strategy to use (defaults to SimpleBiddingStrategy)
        """
        self.strategy = strategy or SimpleBiddingStrategy()

    def evaluate_auction(
        self, auction: Auction, max_price: float | None = None, required_quantity: int = 1
    ) -> tuple[bool, float]:
        """Evaluate whether to participate in an auction.

        Args:
            auction: Auction to evaluate
            max_price: Maximum price willing to pay
            required_quantity: Quantity needed

        Returns:
            Tuple of (should_bid, recommended_price)
        """
        # Check if auction is active
        if not auction.is_active():
            return False, 0.0

        # Calculate recommended bid
        recommended = self.strategy.calculate_bid(auction, max_price)

        # Check if price is acceptable
        if max_price is not None and recommended > max_price:
            return False, recommended

        return True, recommended

    def select_best_auction(
        self, auctions: list[Auction], max_price: float | None = None
    ) -> Auction | None:
        """Select best auction from available options.

        Args:
            auctions: List of available auctions
            max_price: Maximum price constraint

        Returns:
            Best auction to bid on, or None if none suitable
        """
        valid_auctions = []

        for auction in auctions:
            should_bid, price = self.evaluate_auction(auction, max_price)
            if should_bid:
                valid_auctions.append((auction, price))

        if not valid_auctions:
            return None

        # Sort by price (lowest first)
        valid_auctions.sort(key=lambda x: x[1])
        return valid_auctions[0][0]

    def create_bid(
        self,
        auction: Auction,
        max_price: float | None = None,
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> Bid | None:
        """Create a bid for an auction.

        Args:
            auction: Auction to bid on
            max_price: Maximum price constraint
            quantity: Quantity to bid for
            metadata: Additional bid metadata

        Returns:
            Bid object or None if auction not suitable
        """
        should_bid, price = self.evaluate_auction(auction, max_price, quantity)

        if not should_bid:
            return None

        import uuid

        return Bid(
            id=f"bid_{uuid.uuid4().hex[:8]}",
            auction_id=auction.id,
            price=price,
            quantity=quantity,
            metadata=metadata,
        )


# Protocol for auction providers (adapters implement this)
class AuctionProvider(Protocol):
    """Protocol for adapters that provide auction functionality."""

    def list_auctions(self, instance_type: str, region: str | None = None) -> list[Auction]:
        """List available auctions."""
        ...

    def submit_bid(self, bid: Bid) -> AuctionResult:
        """Submit a bid to an auction."""
        ...

    def get_auction_history(self, instance_type: str, region: str, days: int = 7) -> list[Auction]:
        """Get historical auction data."""
        ...
