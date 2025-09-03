"""Bid submission and selection facade.

Unifies region selection, instance type resolution, and bid submission behind a
single service used by the provider facade.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.bidding.builder import BidBuilder
from flow.adapters.providers.builtin.mithril.core.errors import MithrilAPIError
from flow.adapters.providers.builtin.mithril.domain.models import Auction
from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService
from flow.adapters.providers.builtin.mithril.domain.region import RegionSelector
from flow.errors import ResourceNotAvailableError
from flow.protocols.selection import SelectionOutcome
from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


class BidsService:
    def __init__(
        self,
        api: MithrilApiClient,
        region_selector: RegionSelector,
        pricing: PricingService,
        resolve_instance_type: callable,
        get_project_id: callable,
    ) -> None:
        self._api = api
        self._region_selector = region_selector
        self._pricing = pricing
        self._resolve_instance_type = resolve_instance_type
        self._get_project_id = get_project_id

    def select_region_and_instance(
        self, config: TaskConfig, instance_type: str
    ) -> tuple[str, str, Auction | None]:
        # Resolve candidate instance type IDs. For generic H100 requests, consider
        # both SXM and PCIe 8x variants to allow region-specific availability.
        candidate_type_ids: list[str] = []
        it_lower = (instance_type or "").lower()
        try:
            primary_id = self._resolve_instance_type(instance_type)  # Keep using passed resolver
            candidate_type_ids.append(primary_id)
        except Exception:
            # Continue; alternatives may still resolve
            pass

        try:
            if any(t in it_lower for t in ("h100", "xh100")):
                for alt in ("h100-80gb.sxm.8x", "h100-80gb.pcie.8x"):
                    try:
                        alt_id = self._resolve_instance_type(alt)  # Keep using passed resolver
                        if alt_id not in candidate_type_ids:
                            candidate_type_ids.append(alt_id)
                    except Exception:
                        pass
        except Exception:
            pass

        # Fallback: if nothing resolved, raise gracefully
        if not candidate_type_ids:
            raise ResourceNotAvailableError(
                f"Unsupported or unknown instance type: {instance_type}",
                suggestions=[
                    "Use 'flow catalog' to list available instance types",
                    "Try a specific size like '8xh100' or '4xa100'",
                ],
            )

        # Check availability for all candidate instance types and combine by cheapest per region
        combined: dict[str, Auction] = {}
        type_for_region: dict[str, str] = {}
        regions_seen: set[str] = set()
        for fid in candidate_type_ids:
            availability = self._region_selector.check_availability(fid)
            for region, auction in availability.items():
                regions_seen.add(region)
                try:
                    price = self._pricing.parse_price(auction.last_instance_price)
                except Exception:
                    price = float("inf")
                if region not in combined:
                    combined[region] = auction
                    type_for_region[region] = fid
                else:
                    try:
                        existing_price = self._pricing.parse_price(
                            combined[region].last_instance_price
                        )
                    except Exception:
                        existing_price = float("inf")
                    if price < existing_price:
                        combined[region] = auction
                        type_for_region[region] = fid

        # Select best region, honoring explicit preference when present
        selected_region = self._region_selector.select_best_region(combined, config.region)
        if not selected_region:
            regions_checked = sorted(regions_seen)
            raise ResourceNotAvailableError(
                f"No available regions for instance type {instance_type}",
                suggestions=[
                    f"Checked regions: {', '.join(regions_checked) if regions_checked else 'none'}",
                    "Try a different instance type",
                    "Increase your max price limit",
                    "Check back later for availability",
                ],
            )

        auction = combined.get(selected_region)
        instance_type_id = type_for_region.get(selected_region, candidate_type_ids[0])
        return selected_region, instance_type_id, auction

    def submit_bid(
        self,
        config: TaskConfig,
        *,
        region: str,
        instance_type_id: str,
        project_id: str | None = None,
        ssh_keys: list[str] | None = None,
        startup_script: str | None = None,
        volume_attachments: list[dict[str, Any]] | None = None,
        auction_id: str | None = None,
    ) -> Any:
        bid_spec = BidBuilder.build_specification(
            config=config,
            project_id=project_id or self._get_project_id(),
            region=region,
            auction_id=auction_id,
            instance_type_id=instance_type_id,
            ssh_keys=ssh_keys or [],
            startup_script=startup_script,
            volume_attachments=volume_attachments or [],
        )
        return self._api.create_bid(bid_spec.to_api_payload())

    @staticmethod
    def extract_bid_id(response: Any) -> str:
        """Extract bid ID from API response.

        Args:
            response: API response from bid creation

        Returns:
            Bid ID (FID)

        Raises:
            MithrilBidError: If bid ID cannot be extracted
        """
        from flow.adapters.providers.builtin.mithril.core.errors import MithrilBidError

        if isinstance(response, dict):
            # Accept multiple shapes:
            #  - {"fid": "bid_..."}
            #  - {"bid_id": "bid_..."}
            #  - {"bid": {"fid": "bid_..."}}
            bid_id = response.get("fid") or response.get("bid_id")
            if not bid_id and isinstance(response.get("bid"), dict):
                bid_id = response["bid"].get("fid") or response["bid"].get("bid_id")
            if bid_id:
                return bid_id
            raise MithrilBidError(f"No bid ID in response: {response}")

        # Fallback for non-dict responses
        bid_id = str(response)
        if not bid_id:
            raise MithrilBidError(f"Invalid bid response: {response}")
        return bid_id

    def select_region_and_instance_with_fallback(
        self,
        *,
        adjusted_config: TaskConfig,
        instance_type: str,
        instance_fid: str,
        region_selector: RegionSelector,
    ) -> SelectionOutcome:
        """Select region/instance via bids; fallback to availability.

        Args:
            adjusted_config: Task configuration
            instance_type: Instance type specification
            instance_fid: Instance type FID
            region_selector: Region selector for availability fallback

        Returns:
            SelectionOutcome with consistent fields for downstream logic
        """
        # Try bids-based selection first
        try:
            region, instance_type_id, auction = self.select_region_and_instance(
                adjusted_config, instance_type
            )
            if region:
                return SelectionOutcome(
                    region=region,
                    auction=auction,
                    instance_type_id=instance_type_id,
                    candidate_regions=[region],
                    source="bids",
                )
        except Exception:
            # Fall through to availability-based selection
            pass

        # Legacy availability-based selection
        availability = region_selector.check_availability(instance_fid)
        region = region_selector.select_best_region(availability, adjusted_config.region)
        candidate_regions = list(availability.keys()) if availability else []
        auction = availability[region] if region and availability else None
        instance_type_id = instance_fid if region else None

        return SelectionOutcome(
            region=region,
            auction=auction,
            instance_type_id=instance_type_id,
            candidate_regions=candidate_regions,
            source="availability",
        )

    # ================= Bid State Transitions =================
    def pause_bid(self, bid_id: str) -> None:
        """Pause a bid (idempotent operation).

        Args:
            bid_id: Bid ID to pause

        Raises:
            MithrilAPIError: If pause request fails with a non-idempotent error
        """
        try:
            self._api.patch_bid(bid_id, {"paused": True})
            logger.debug(f"Bid {bid_id} pause request succeeded (paused=True)")
        except Exception as e:
            # Try alternate pause shape for newer APIs
            try:
                self._api.patch_bid(bid_id, {"status": "paused"})
                logger.debug(f"Bid {bid_id} pause request succeeded (status=paused)")
            except Exception as e2:
                # Treat already-paused as success for idempotency
                if any(
                    k in str(e).lower() or k in str(e2).lower()
                    for k in ("already paused", "already_paused", "is paused")
                ):
                    logger.debug(f"Bid {bid_id} already paused")
                    return
                raise MithrilAPIError(f"Failed to pause bid: {e2}") from e2

        # Small delay to let state propagate before subsequent updates
        time.sleep(1.0)

    def unpause_bid(self, bid_id: str) -> None:
        """Unpause a bid (idempotent operation)."""
        try:
            self._api.patch_bid(bid_id, {"paused": False})
            logger.debug(f"Bid {bid_id} unpause request succeeded (paused=False)")
        except Exception as e:
            # Try alternate unpause shape for newer APIs
            try:
                self._api.patch_bid(bid_id, {"status": "running"})
                logger.debug(f"Bid {bid_id} unpause request succeeded (status=running)")
            except Exception as e2:
                # Treat not-paused/already-running as success for idempotency
                msg = (str(e) + " " + str(e2)).lower()
                if any(k in msg for k in ("not paused", "already running", "is running")):
                    logger.debug(f"Bid {bid_id} already unpaused")
                    return
                raise MithrilAPIError(f"Failed to unpause bid: {e2}") from e2

    def safe_unpause_bid(self, bid_id: str) -> None:
        """Attempt to unpause a bid and swallow errors for best-effort recovery."""
        try:
            self.unpause_bid(bid_id)
        except Exception:
            logger.warning(f"Failed to unpause bid {bid_id} during error recovery")

    def update_bid_volumes(self, bid_id: str, volumes: list[str]) -> None:
        """Update the volumes attached to a bid.

        The API has supported both top-level `volumes` and
        `launch_specification.volumes` in different revisions. To be
        resilient across versions, try the nested form first and fall
        back to the top-level field if the request fails.
        """
        try:
            self._api.patch_bid(bid_id, {"launch_specification": {"volumes": volumes}})
        except Exception as first_err:
            # Fallback to legacy/top-level update shape
            try:
                self._api.patch_bid(bid_id, {"volumes": volumes})
            except Exception:
                # Re-raise the original error for clearer diagnosis upstream
                raise first_err

    def update_bid_launch_spec(self, bid_id: str, launch_spec: dict[str, Any]) -> None:
        """Update the full launch_specification for a bid.

        Sends a PATCH with a merged launch_specification object to avoid
        inadvertently dropping fields on APIs that replace nested objects
        rather than deep-merge them.
        """
        # Try direct nested update first
        try:
            self._api.patch_bid(bid_id, {"launch_specification": launch_spec})
        except Exception as first_err:
            # No sensible legacy fallback for entire launch_spec; surface error
            raise MithrilAPIError(
                f"Failed to update launch_specification: {first_err}"
            ) from first_err
