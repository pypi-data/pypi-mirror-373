"""Mithril-specific pricing adapter.

Adapts the domain pricing service to work with Mithril's API,
handling provider-specific details while delegating core logic
to the domain service.
"""

from __future__ import annotations

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.errors import InsufficientBidPriceError, ValidationAPIError


class PricingService:
    """Mithril-specific pricing adapter.

    Wraps domain pricing service and provides Mithril API integration.
    """

    def __init__(self, api: MithrilApiClient) -> None:
        self._api = api
        # Domain-free parser
        self._parser = _SimplePriceParser()

    def parse_price(self, price_str: str | None) -> float:
        """Parse a price string like "$10.00" to a float.

        Delegates to domain PriceParser for consistency.
        """
        return self._parser.parse(price_str)

    def get_current_market_price(self, instance_type_id: str, region: str) -> float | None:
        """Fetch current market price for an instance type in a region.

        Returns:
            The current market price or None if unavailable.
        """
        try:
            auctions = self._api.list_spot_availability(
                {"instance_type": instance_type_id, "region": region}
            )

            if auctions and isinstance(auctions, list):
                # Prefer exact match, otherwise first item
                match = None
                for a in auctions:
                    if a.get("instance_type") == instance_type_id and a.get("region") == region:
                        match = a
                        break
                candidate = match or auctions[0]
                return self.parse_price(candidate.get("last_instance_price", ""))
        except Exception:
            return None
        return None

    def is_price_validation_error(self, error: ValidationAPIError) -> bool:
        """Detect whether a ValidationAPIError is price-related."""
        if not getattr(error, "validation_errors", None):
            return False
        price_keywords = ["price", "bid", "limit_price", "minimum", "insufficient"]
        for item in error.validation_errors:
            msg = str(item.get("msg", "")).lower()
            loc = item.get("loc", [])
            if any("price" in str(f).lower() for f in loc):
                return True
            if any(k in msg for k in price_keywords):
                return True
        return False

    def enhance_price_error(
        self,
        error: ValidationAPIError,
        *,
        instance_type_id: str,
        region: str,
        attempted_price: float | None,
        instance_display_name: str,
    ) -> InsufficientBidPriceError:
        """Augment a price validation error with current pricing and advice."""
        try:
            auctions = self._api.list_spot_availability(
                {"instance_type": instance_type_id, "region": region}
            )
            if not auctions:
                raise error
            auction = None
            if len(auctions) == 1:
                auction = auctions[0]
            else:
                for a in auctions:
                    if a.get("region") == region and a.get("instance_type") == instance_type_id:
                        auction = a
                        break
            auction = auction or auctions[0]
            current_price = self.parse_price(auction.get("last_instance_price"))
            min_bid_price = self.parse_price(auction.get("min_bid_price"))
            effective = max(v for v in [current_price, min_bid_price] if v is not None)
            recommended = effective * 1.5
            message = (
                f"Bid price ${attempted_price:.2f}/hour is too low for {instance_display_name} "
                f"in {region}. Current spot price is ${effective:.2f}/hour."
            )
            return InsufficientBidPriceError(
                message=message,
                current_price=effective,
                min_bid_price=min_bid_price or None,
                recommended_price=recommended,
                instance_type=instance_display_name,
                region=region,
                response=getattr(error, "response", None),
            )
        except Exception:
            # On failure to enhance, re-raise original
            raise error


class _SimplePriceParser:
    """Minimal price parser for dollar-formatted strings like "$10.00"."""

    def parse(self, price_str: str | None) -> float:
        if price_str is None:
            raise ValueError("price is None")
        s = str(price_str).strip()
        if not s:
            raise ValueError("empty price")
        # Accept leading '$' and commas
        if s.startswith("$"):
            s = s[1:]
        s = s.replace(",", "")
        return float(s)
