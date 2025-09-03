"""Domain service for bidding strategies and bid management.

This module consolidates bidding logic from adapters into the domain layer,
providing clean separation between business logic and infrastructure concerns.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from flow.domain.services.auctions import Auction, AuctionService
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class BidStatus(Enum):
    """Status of a bid submission."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FULFILLED = "fulfilled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class BidSubmissionError(FlowError):
    """Error during bid submission."""

    pass


class BidValidationError(FlowError):
    """Error validating bid parameters."""

    pass


@dataclass
class BidRequest:
    """Request for submitting a bid."""

    auction_id: str
    instance_type_id: str
    quantity: int
    max_price_per_hour: float
    task_name: str
    ssh_keys: list[str]
    startup_script: str
    disk_attachments: list[dict[str, Any]] | None = None

    # Partial fulfillment options
    allow_partial: bool = False
    min_quantity: int = 1
    chunk_size: int | None = None

    def __post_init__(self):
        """Validate request after initialization."""
        if self.quantity < 1:
            raise BidValidationError("Quantity must be at least 1")
        if self.max_price_per_hour < 0:
            raise BidValidationError("Max price must be non-negative")
        if self.min_quantity < 1 or self.min_quantity > self.quantity:
            raise BidValidationError("Min quantity must be between 1 and quantity")
        if self.chunk_size is not None and self.chunk_size < 1:
            raise BidValidationError("Chunk size must be at least 1")
        if not self.task_name:
            raise BidValidationError("Task name is required")

        # Set defaults
        if self.disk_attachments is None:
            self.disk_attachments = []


@dataclass
class BidResult:
    """Result of a bid submission."""

    bid_id: str
    quantity_fulfilled: int
    instances: list[str]
    status: BidStatus = BidStatus.PENDING

    @property
    def is_fully_fulfilled(self) -> bool:
        """Check if all requested instances were fulfilled."""
        return len(self.instances) == self.quantity_fulfilled

    @property
    def is_successful(self) -> bool:
        """Check if bid was successful (fully or partially)."""
        return self.status in [BidStatus.FULFILLED, BidStatus.PARTIAL]


@dataclass
class AuctionCriteria:
    """Criteria for matching auctions."""

    gpu_type: str | None = None
    num_gpus: int | None = None
    min_gpu_count: int | None = None
    region: str | None = None
    max_price_per_hour: float | None = None
    instance_type: str | None = None
    internode_interconnect: str | None = None
    intranode_interconnect: str | None = None

    def __post_init__(self):
        """Set min_gpu_count from num_gpus if not specified."""
        if self.min_gpu_count is None and self.num_gpus is not None:
            self.min_gpu_count = self.num_gpus


class ChunkedBiddingStrategy:
    """Strategy for handling partial fulfillment through chunked bidding."""

    def __init__(self, default_chunk_size: int = 4):
        """Initialize chunked bidding strategy.

        Args:
            default_chunk_size: Default size for chunks when not specified
        """
        self.default_chunk_size = default_chunk_size

    def calculate_chunks(
        self, total_quantity: int, chunk_size: int | None = None, min_quantity: int = 1
    ) -> list[int]:
        """Calculate optimal chunk sizes for a request.

        Args:
            total_quantity: Total instances requested
            chunk_size: Preferred chunk size (uses default if None)
            min_quantity: Minimum acceptable quantity

        Returns:
            List of chunk sizes
        """
        if chunk_size is None:
            chunk_size = self.default_chunk_size

        chunks = []
        remaining = total_quantity

        while remaining > 0:
            current_chunk = min(chunk_size, remaining)
            if current_chunk >= min_quantity:
                chunks.append(current_chunk)
                remaining -= current_chunk
            else:
                # Merge small remainder with last chunk if possible
                if chunks:
                    chunks[-1] += remaining
                else:
                    chunks.append(remaining)
                break

        return chunks

    def customize_startup_script(
        self,
        base_script: str,
        chunk_index: int,
        total_chunks: int,
        customizer: Callable[[int, str], str] | None = None,
    ) -> str:
        """Customize startup script for a specific chunk.

        Args:
            base_script: Base startup script
            chunk_index: Index of this chunk (0-based)
            total_chunks: Total number of chunks
            customizer: Optional custom function for script modification

        Returns:
            Customized startup script
        """
        if customizer:
            return customizer(chunk_index, base_script)

        # Default: add chunk metadata as environment variables
        chunk_vars = f"""export CHUNK_INDEX={chunk_index}
export TOTAL_CHUNKS={total_chunks}
export CHUNK_ID="chunk-{chunk_index}"
"""
        return chunk_vars + base_script


class BiddingService:
    """Domain service for bid management and strategy execution."""

    def __init__(
        self,
        auction_service: AuctionService | None = None,
        chunked_strategy: ChunkedBiddingStrategy | None = None,
    ):
        """Initialize bidding service.

        Args:
            auction_service: Service for auction operations
            chunked_strategy: Strategy for chunked bidding
        """
        self.auction_service = auction_service or AuctionService()
        self.chunked_strategy = chunked_strategy or ChunkedBiddingStrategy()

    def evaluate_bid_request(
        self, request: BidRequest, available_auctions: list[Auction]
    ) -> tuple[bool, str]:
        """Evaluate if a bid request can be fulfilled.

        Args:
            request: Bid request to evaluate
            available_auctions: Available auctions to consider

        Returns:
            Tuple of (can_fulfill, reason)
        """
        if not available_auctions:
            return False, "No auctions available"

        # Find suitable auction
        suitable_auction = None
        for auction in available_auctions:
            if auction.instance_type == request.instance_type_id:
                should_bid, _ = self.auction_service.evaluate_auction(
                    auction, request.max_price_per_hour, request.quantity
                )
                if should_bid:
                    suitable_auction = auction
                    break

        if not suitable_auction:
            return False, "No suitable auctions found within price constraints"

        return True, f"Can bid on auction {suitable_auction.id}"

    def plan_bidding_strategy(self, request: BidRequest) -> dict[str, Any]:
        """Plan the optimal bidding strategy for a request.

        Args:
            request: Bid request to plan for

        Returns:
            Strategy plan with execution details
        """
        plan = {
            "strategy_type": "single" if not request.allow_partial else "chunked",
            "total_quantity": request.quantity,
            "chunks": [],
            "estimated_cost": 0.0,
        }

        if request.allow_partial and request.chunk_size:
            # Plan chunked strategy
            chunks = self.chunked_strategy.calculate_chunks(
                request.quantity, request.chunk_size, request.min_quantity
            )

            for i, chunk_size in enumerate(chunks):
                chunk_plan = {
                    "index": i,
                    "quantity": chunk_size,
                    "task_name": f"{request.task_name}-chunk-{i}",
                    "estimated_cost": chunk_size * request.max_price_per_hour,
                }
                plan["chunks"].append(chunk_plan)
                plan["estimated_cost"] += chunk_plan["estimated_cost"]
        else:
            # Single bid strategy
            plan["chunks"] = [
                {
                    "index": 0,
                    "quantity": request.quantity,
                    "task_name": request.task_name,
                    "estimated_cost": request.quantity * request.max_price_per_hour,
                }
            ]
            plan["estimated_cost"] = request.quantity * request.max_price_per_hour

        return plan

    def create_chunk_requests(
        self,
        base_request: BidRequest,
        startup_script_customizer: Callable[[int, str], str] | None = None,
    ) -> list[BidRequest]:
        """Create individual bid requests for chunked bidding.

        Args:
            base_request: Base request to chunk
            startup_script_customizer: Optional function to customize scripts

        Returns:
            List of individual bid requests
        """
        if not base_request.allow_partial or not base_request.chunk_size:
            return [base_request]

        chunks = self.chunked_strategy.calculate_chunks(
            base_request.quantity, base_request.chunk_size, base_request.min_quantity
        )

        chunk_requests = []
        for i, chunk_size in enumerate(chunks):
            # Customize startup script for this chunk
            chunk_script = self.chunked_strategy.customize_startup_script(
                base_request.startup_script, i, len(chunks), startup_script_customizer
            )

            # Create chunk request
            chunk_request = BidRequest(
                auction_id=base_request.auction_id,
                instance_type_id=base_request.instance_type_id,
                quantity=chunk_size,
                max_price_per_hour=base_request.max_price_per_hour,
                task_name=f"{base_request.task_name}-chunk-{i}",
                ssh_keys=base_request.ssh_keys.copy(),
                startup_script=chunk_script,
                disk_attachments=(
                    base_request.disk_attachments.copy() if base_request.disk_attachments else None
                ),
                allow_partial=False,  # Individual chunks are all-or-nothing
                min_quantity=1,
            )
            chunk_requests.append(chunk_request)

        return chunk_requests

    def validate_bid_specification(
        self,
        project_id: str,
        region: str,
        name: str,
        instance_quantity: int,
        limit_price: str,
        auction_id: str | None = None,
        instance_type: str | None = None,
    ) -> tuple[bool, str]:
        """Validate bid specification parameters.

        Args:
            project_id: Project identifier
            region: Target region
            name: Bid name
            instance_quantity: Number of instances
            limit_price: Price limit in dollar format
            auction_id: Optional auction ID
            instance_type: Optional instance type

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required fields
        if not project_id:
            return False, "project_id is required"
        if not region:
            return False, "region is required"
        if not name:
            return False, "name is required"
        if instance_quantity < 1:
            return False, "instance_quantity must be at least 1"

        # Price validation
        if not limit_price or not limit_price.startswith("$"):
            return False, "limit_price must be in dollar format (e.g., '$25.60')"

        try:
            price_value = float(limit_price[1:])
            if price_value < 0:
                return False, "limit_price must be non-negative"
        except ValueError:
            return False, "limit_price must be a valid dollar amount"

        # Instance targeting validation
        if auction_id and not instance_type:
            return False, "When auction_id is provided, instance_type is also required"
        if not auction_id and not instance_type:
            return (
                False,
                "Must specify instance_type (and optionally auction_id for spot instances)",
            )

        return True, "Valid specification"

    def calculate_total_cost_estimate(
        self, request: BidRequest, duration_hours: float = 1.0
    ) -> dict[str, float]:
        """Calculate cost estimates for a bid request.

        Args:
            request: Bid request to estimate
            duration_hours: Expected duration in hours

        Returns:
            Cost breakdown dictionary
        """
        base_cost = request.quantity * request.max_price_per_hour * duration_hours

        estimates = {
            "base_cost": base_cost,
            "max_cost": base_cost,  # Same as base for now
            "min_cost": request.min_quantity * request.max_price_per_hour * duration_hours,
            "per_instance_hour": request.max_price_per_hour,
            "duration_hours": duration_hours,
        }

        # Add chunking overhead estimate if applicable
        if request.allow_partial and request.chunk_size:
            chunks = self.chunked_strategy.calculate_chunks(
                request.quantity, request.chunk_size, request.min_quantity
            )
            # Small overhead for managing multiple chunks
            overhead_factor = 1.0 + (len(chunks) - 1) * 0.01  # 1% per additional chunk
            estimates["chunking_overhead"] = estimates["base_cost"] * (overhead_factor - 1.0)
            estimates["max_cost"] = estimates["base_cost"] * overhead_factor

        return estimates


# Protocol for bid submission (adapters implement this)
class BidSubmissionProvider(Protocol):
    """Protocol for adapters that handle bid submission."""

    def submit_single_bid(self, request: BidRequest) -> BidResult:
        """Submit a single bid."""
        ...

    def cancel_bid(self, bid_id: str) -> bool:
        """Cancel a bid if possible."""
        ...

    def get_bid_status(self, bid_id: str) -> BidStatus:
        """Get current status of a bid."""
        ...
