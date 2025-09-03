"""Domain pricing service - provider-agnostic pricing logic.

This module contains the core pricing logic that can be used across
different providers without depending on specific implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class PriceInfo:
    """Domain model for price information."""

    amount: float
    currency: str = "USD"
    per_hour: bool = True

    def __str__(self) -> str:
        """Format price for display."""
        prefix = "$" if self.currency == "USD" else self.currency
        suffix = "/hr" if self.per_hour else ""
        return f"{prefix}{self.amount:.2f}{suffix}"


class PriceParser:
    """Utility for parsing price strings into structured data."""

    @staticmethod
    def parse(price_str: str | None) -> float:
        """Parse a price string like "$10.00" to a float.

        Args:
            price_str: Price string to parse (e.g., "$10.00", "10.00")

        Returns:
            Parsed price as float, or 0.0 for invalid input
        """
        if not price_str:
            return 0.0

        # Remove common currency symbols and formatting
        clean = price_str.strip()
        for symbol in ["$", "€", "£", "¥", ","]:
            clean = clean.replace(symbol, "")
        clean = clean.strip()

        try:
            return float(clean)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def parse_to_info(price_str: str | None) -> PriceInfo | None:
        """Parse a price string into a PriceInfo object.

        Args:
            price_str: Price string to parse

        Returns:
            PriceInfo object or None if parsing fails
        """
        amount = PriceParser.parse(price_str)
        if amount <= 0:
            return None
        return PriceInfo(amount=amount)


class PricingStrategy(ABC):
    """Abstract base for pricing strategies."""

    @abstractmethod
    def calculate_bid_price(
        self, market_price: float, max_price: float | None = None, margin: float = 0.1
    ) -> float:
        """Calculate optimal bid price based on market conditions.

        Args:
            market_price: Current market price
            max_price: Maximum price user is willing to pay
            margin: Margin above market price (0.1 = 10%)

        Returns:
            Calculated bid price
        """
        ...


class StandardPricingStrategy(PricingStrategy):
    """Standard pricing strategy with configurable margin."""

    def calculate_bid_price(
        self, market_price: float, max_price: float | None = None, margin: float = 0.1
    ) -> float:
        """Calculate bid price with margin above market.

        Uses a simple margin-based approach:
        - Add configured margin to market price
        - Respect user's limit price (max price) if specified
        - Ensure minimum viable price
        """
        # Calculate base bid with margin
        bid_price = market_price * (1 + margin)

        # Apply user's limit price (max price) if specified
        if max_price is not None and max_price > 0:
            bid_price = min(bid_price, max_price)

        # Ensure minimum viable price
        return max(bid_price, 0.01)


class AggressivePricingStrategy(PricingStrategy):
    """Aggressive pricing for high-priority workloads."""

    def calculate_bid_price(
        self, market_price: float, max_price: float | None = None, margin: float = 0.25
    ) -> float:
        """Calculate aggressive bid price for better availability.

        Uses higher margin to increase chances of winning bid:
        - Uses 25% margin by default (vs 10% for standard)
        - Minimum 2x market price for critical workloads
        """
        # Use higher margin for aggressive bidding
        bid_price = market_price * (1 + margin)

        # Ensure at least 2x market for critical workloads
        bid_price = max(bid_price, market_price * 2.0)

        # Apply limit price if specified
        if max_price is not None and max_price > 0:
            bid_price = min(bid_price, max_price)

        return max(bid_price, 0.01)


class PricingService:
    """Domain service for pricing operations.

    This service provides pricing logic without depending on
    specific provider implementations.
    """

    def __init__(self, strategy: PricingStrategy | None = None):
        """Initialize with optional pricing strategy.

        Args:
            strategy: Pricing strategy to use (defaults to StandardPricingStrategy)
        """
        self.strategy = strategy or StandardPricingStrategy()
        self.parser = PriceParser()

    def calculate_optimal_bid(
        self,
        market_price: float | str,
        max_price: float | str | None = None,
        aggressive: bool = False,
    ) -> float:
        """Calculate optimal bid price based on market conditions.

        Args:
            market_price: Current market price (float or string)
            max_price: Maximum price willing to pay
            aggressive: Use aggressive pricing strategy

        Returns:
            Optimal bid price
        """
        # Parse prices if strings
        if isinstance(market_price, str):
            market_price = self.parser.parse(market_price)
        if isinstance(max_price, str):
            max_price = self.parser.parse(max_price)

        # Switch strategy if aggressive mode requested
        strategy = self.strategy
        if aggressive:
            strategy = AggressivePricingStrategy()

        return strategy.calculate_bid_price(market_price, max_price)

    def validate_bid_price(
        self, bid_price: float, market_price: float, min_margin: float = 0.0
    ) -> tuple[bool, str | None]:
        """Validate if bid price is sufficient.

        Args:
            bid_price: Proposed bid price
            market_price: Current market price
            min_margin: Minimum required margin (0.0 = market price)

        Returns:
            Tuple of (is_valid, error_message)
        """
        min_required = market_price * (1 + min_margin)

        if bid_price < min_required:
            return False, f"Bid price ${bid_price:.2f} is below minimum ${min_required:.2f}"

        return True, None


# Protocol for price providers (adapters implement this)
class PriceProvider(Protocol):
    """Protocol for adapters that provide pricing data."""

    def get_market_price(self, instance_type: str, region: str) -> float | None:
        """Get current market price for instance type in region."""
        ...

    def get_price_history(
        self, instance_type: str, region: str, hours: int = 24
    ) -> list[PriceInfo]:
        """Get historical prices for analysis."""
        ...
