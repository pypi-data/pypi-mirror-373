"""Auction-to-model adapters for Mithril provider.

Centralizes conversion of Mithril auction payloads into Flow models to
keep the provider facade slim and testable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flow.sdk.models import AvailableInstance


def convert_auction_to_available_instance(
    auction_data: dict[str, Any],
    *,
    pricing_service: Any,
    task_service: Any,
) -> AvailableInstance | None:
    """Convert Mithril auction data to ``AvailableInstance``.

    Args:
        auction_data: Raw auction data from Mithril API
        pricing_service: PricingService for parsing prices
        task_service: TaskService for resolving instance type names

    Returns:
        AvailableInstance or None if conversion fails
    """
    try:
        # Price per hour (robust parser via PricingService)
        price_str = auction_data.get("last_instance_price", auction_data.get("price", "$0"))
        price_per_hour = pricing_service.parse_price(price_str)

        # Resolve instance type name from ID
        instance_type_id = auction_data.get(
            "instance_type", auction_data.get("instance_type_id", "")
        )
        instance_type_name = task_service.get_instance_type_name(instance_type_id)

        # Derive per-instance GPU count when not present
        gpu_count_val = auction_data.get("gpu_count") or auction_data.get("num_gpus")
        if not gpu_count_val:
            try:
                it_lower = (instance_type_name or "").lower()
                # Match either prefix style '8xa100' or suffix style '.8x'
                import re as _re

                m = _re.search(r"(\d+)x", it_lower)
                if m:
                    gpu_count_val = int(m.group(1))
                else:
                    gpu_count_val = 1 if it_lower in ("a100", "h100") else None
            except Exception:
                gpu_count_val = None

        # Derive GPU family/type when not present
        gpu_type_val = auction_data.get("gpu_type")
        if not gpu_type_val:
            try:
                it_lower = (instance_type_name or "").lower()
                if "x" in it_lower:
                    _, suffix = it_lower.split("x", 1)
                    gpu_type_val = suffix
                else:
                    # 'a100' or 'h100' forms
                    gpu_type_val = it_lower if it_lower.endswith("100") else None
            except Exception:
                gpu_type_val = None

        # Convert capacity to available instances when possible
        capacity_val = (
            auction_data.get("available_gpus")
            or auction_data.get("inventory_quantity")
            or auction_data.get("capacity")
        )
        available_qty = None
        try:
            if capacity_val is not None and gpu_count_val and int(gpu_count_val) > 0:
                available_qty = int(int(capacity_val) // int(gpu_count_val))
            elif capacity_val is not None:
                available_qty = int(capacity_val)
        except Exception:
            available_qty = None

        return AvailableInstance(
            allocation_id=auction_data.get("fid", auction_data.get("auction_id", "")),
            instance_type=instance_type_name,
            region=auction_data.get("region", ""),
            price_per_hour=price_per_hour,
            gpu_type=gpu_type_val,
            gpu_count=gpu_count_val,
            cpu_count=auction_data.get("cpu_count"),
            memory_gb=auction_data.get("memory_gb"),
            available_quantity=available_qty,
            status=auction_data.get("status"),
            expires_at=(
                datetime.fromisoformat(auction_data["expires_at"])
                if auction_data.get("expires_at")
                else None
            ),
            internode_interconnect=auction_data.get("internode_interconnect"),
            intranode_interconnect=auction_data.get("intranode_interconnect"),
        )
    except Exception:
        return None
