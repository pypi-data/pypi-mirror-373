"""Bid management adapter for Mithril provider.

This adapter handles the infrastructure concerns of bid submission,
delegating business logic to domain services.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.domain.pricing.calculator import calculate_instance_price, get_pricing_table
from flow.errors import FlowError
from flow.resources import get_gpu_pricing as get_pricing_data
from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


class BidSubmissionError(FlowError):
    pass


class BidStatus(Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"


@dataclass
class BidRequest:
    auction_id: str
    instance_type_id: str
    quantity: int
    max_price_per_hour: float
    task_name: str
    ssh_keys: list[str]
    startup_script: str
    disk_attachments: list[dict[str, Any]] | None = None
    allow_partial: bool = False
    min_quantity: int = 1
    chunk_size: int | None = None


@dataclass
class BidResult:
    bid_id: str
    quantity_fulfilled: int
    instances: list[str]
    status: BidStatus = BidStatus.PENDING


class BidManager:
    """Adapter for bid submission using domain services."""

    def __init__(self, api_client: MithrilApiClient):
        """Initialize bid manager.

        Args:
            api_client: HTTP client for API requests
            bidding_service: Domain service for bidding logic
        """
        self._api: MithrilApiClient = api_client

    def submit_bid(
        self,
        request: BidRequest,
        startup_script_customizer: Callable[[int, str], str] | None = None,
    ) -> list[BidResult]:
        """Submit bid with optional partial fulfillment.

        Args:
            request: Bid request parameters
            startup_script_customizer: Optional function to customize startup script per chunk

        Returns:
            List of bid results (one per chunk if using partial fulfillment)
        """
        # Create chunk requests locally if partial allowed; otherwise single request
        chunk_requests: list[BidRequest] = []
        if request.allow_partial and request.chunk_size:
            chunks = self._calculate_chunks(
                request.quantity, request.chunk_size, request.min_quantity
            )
            total = len(chunks)
            for idx, qty in enumerate(chunks):
                startup_script = self._customize_startup_script(
                    request.startup_script, idx, total, startup_script_customizer
                )
                chunk_requests.append(
                    BidRequest(
                        auction_id=request.auction_id,
                        instance_type_id=request.instance_type_id,
                        quantity=qty,
                        max_price_per_hour=request.max_price_per_hour,
                        task_name=request.task_name,
                        ssh_keys=request.ssh_keys,
                        startup_script=startup_script,
                        disk_attachments=request.disk_attachments or [],
                        allow_partial=False,
                    )
                )
        else:
            chunk_requests = [request]

        results = []
        for chunk_request in chunk_requests:
            try:
                result = self._submit_single_bid(chunk_request)
                results.append(result)

                # Stop if we got less than requested (partial fulfillment)
                if result.quantity_fulfilled < chunk_request.quantity:
                    logger.warning(
                        f"Chunk only fulfilled {result.quantity_fulfilled} "
                        f"out of {chunk_request.quantity} requested"
                    )
                    break

            except Exception as e:
                logger.error(f"Failed to submit chunk: {e}")
                # Stop on error if we have some successful bids
                if results:
                    break
                # Re-raise if this was the first chunk
                raise

        # Log summary for chunked bids
        if len(chunk_requests) > 1:
            total_fulfilled = sum(r.quantity_fulfilled for r in results)
            logger.info(
                f"Partial fulfillment complete: {total_fulfilled}/{request.quantity} instances "
                f"across {len(results)} bids"
            )

        return results

    def _submit_single_bid(self, request: BidRequest) -> BidResult:
        """Submit a single bid via API."""
        payload = {
            "auction_id": request.auction_id,
            "instance_type": request.instance_type_id,
            "quantity": request.quantity,
            "max_price": int(request.max_price_per_hour * 100),  # Convert to cents
            "task_name": request.task_name,
            "ssh_keys": request.ssh_keys,
            "startup_script": request.startup_script,
            "disk_attachments": request.disk_attachments or [],
        }

        try:
            response = self._api.create_legacy_bid(payload)

            bid_id = response.get("bid_id", response.get("fid"))
            instances = response.get("instances", [])

            return BidResult(
                bid_id=bid_id,
                quantity_fulfilled=len(instances),
                instances=[inst.get("fid") for inst in instances],
                status=BidStatus.FULFILLED if instances else BidStatus.PENDING,
            )

        except Exception as e:
            raise BidSubmissionError(f"Failed to submit bid: {e}") from e

    @staticmethod
    def _calculate_chunks(total_quantity: int, chunk_size: int, min_quantity: int) -> list[int]:
        chunks: list[int] = []
        remaining = total_quantity
        while remaining > 0:
            current = min(chunk_size, remaining)
            if current >= min_quantity:
                chunks.append(current)
                remaining -= current
            else:
                if chunks:
                    chunks[-1] += remaining
                else:
                    chunks.append(remaining)
                break
        return chunks

    @staticmethod
    def _customize_startup_script(
        base_script: str, chunk_index: int, total_chunks: int, customizer
    ) -> str:
        if customizer:
            try:
                return customizer(chunk_index, base_script)
            except Exception:
                pass
        meta = f"export CHUNK_INDEX={chunk_index}\nexport TOTAL_CHUNKS={total_chunks}\nexport CHUNK_ID=chunk-{chunk_index}\n"
        return meta + (base_script or "")

    def cancel_bid(self, bid_id: str) -> bool:
        """Cancel a bid if possible.

        Args:
            bid_id: ID of the bid to cancel

        Returns:
            True if cancelled successfully
        """
        try:
            self._api.delete_bid(bid_id)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel bid {bid_id}: {e}")
            return False

    def create_request_from_config(
        self,
        config: TaskConfig,
        auction_id: str,
        instance_type_id: str,
        startup_script: str,
        disk_attachments: list[dict[str, Any]],
        allow_partial: bool = False,
        chunk_size: int | None = None,
    ) -> BidRequest:
        """Create bid request from task configuration.

        Args:
            config: Task configuration
            auction_id: Auction to bid on
            instance_type_id: Resolved instance type ID
            startup_script: Complete startup script
            disk_attachments: Volume attachments
            allow_partial: Whether to allow partial fulfillment
            chunk_size: Size of chunks for partial fulfillment

        Returns:
            BidRequest object
        """
        # Determine per-instance max price: explicit > derived from pricing.json > conservative fallback
        try:
            if config.max_price_per_hour is not None:
                max_pph = float(config.max_price_per_hour)
            else:
                prio = (getattr(config, "priority", None) or "med").lower()
                inst = getattr(config, "instance_type", None) or ""
                table = get_pricing_table(overrides=get_pricing_data().get("gpu_pricing", {}))
                derived = calculate_instance_price(inst, priority=prio, pricing_table=table)
                max_pph = (
                    float(derived) if isinstance(derived, (int, float)) and derived > 0 else 100.0
                )
        except Exception:
            max_pph = 100.0

        return BidRequest(
            auction_id=auction_id,
            instance_type_id=instance_type_id,
            quantity=config.num_instances,
            max_price_per_hour=max_pph,
            task_name=config.name,
            ssh_keys=config.ssh_keys,
            startup_script=startup_script,
            disk_attachments=disk_attachments,
            allow_partial=allow_partial,
            min_quantity=1,
            chunk_size=chunk_size,
        )
