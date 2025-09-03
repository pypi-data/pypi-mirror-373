"""Task assembly service for Mithril provider.

This module encapsulates the logic for constructing Flow ``Task`` objects from
Mithril bid data, including status mapping, instance-type name resolution,
SSH destination parsing, price parsing, and optional enrichment with market
pricing. Extracted from the provider facade for testability and clarity.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

from flow.adapters.providers.builtin.mithril.core.constants import (
    DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_SSH_USER,
    INSTANCE_TYPE_MAPPINGS,
    STATUS_MAPPINGS,
)
from flow.adapters.providers.builtin.mithril.domain.instances import InstanceService
from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService
from flow.adapters.providers.builtin.mithril.resources import get_default_gpu_memory
from flow.protocols.http import HttpClientProtocol
from flow.sdk.models import Reservation, Task, TaskConfig, TaskStatus
from flow.utils.instance_spec import parse as parse_instance_spec


class TaskService:
    """Builds ``Task`` objects from Mithril bid dictionaries."""

    def __init__(
        self,
        http: HttpClientProtocol,
        pricing: PricingService,
        instances: InstanceService,
        *,
        default_region: str = DEFAULT_REGION,
        default_ssh_user: str = DEFAULT_SSH_USER,
        default_ssh_port: int = DEFAULT_SSH_PORT,
        ssh_resolver: object | None = None,
    ) -> None:
        self._http = http
        self._pricing = pricing
        self._instances = instances
        self._default_region = default_region
        self._default_ssh_user = default_ssh_user
        self._default_ssh_port = default_ssh_port
        # Optional centralized SSH resolver (provider-level)
        self._ssh_resolver = ssh_resolver

    def set_ssh_resolver(self, resolver: object | None) -> None:
        self._ssh_resolver = resolver

    def build_task(
        self,
        bid_data: dict[str, Any],
        *,
        config: TaskConfig | None = None,
        fetch_instance_details: bool = False,
    ) -> Task:
        task_id = bid_data.get("fid", "")
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:
            debug = os.environ.get("FLOW_SSH_DEBUG") == "1"

        # Name resolution
        bid_name = bid_data.get("name", "")
        if bid_name:
            name = bid_name
        elif config and config.name:
            name = config.name
        else:
            name = f"task-{task_id[:8]}" if len(task_id) > 8 else f"task-{task_id}"

        # Map Mithril bid status to TaskStatus; accept common variants
        # Mithril may return bid.status in various forms, e.g. "Allocated", "Terminated",
        # or instance-like constants such as "STATUS_TERMINATED". Normalize aggressively.
        raw_status = str(bid_data.get("status", "pending")).strip().lower()
        # Normalize known prefixes (handle API variants like STATUS_TERMINATED)
        if raw_status.startswith("status_"):
            raw_status = raw_status.replace("status_", "")
        # Some APIs return past-tense; normalize to our canonical set
        if raw_status == "terminating":
            raw_status = "preempting"
        if raw_status == "terminated":
            raw_status = "cancelled"
        status = self._map_mithril_status_to_enum(raw_status)
        if debug:
            print(
                f"[build_task] bid={task_id} status_raw={bid_data.get('status')} normalized={raw_status} mapped={status.value}"
            )

        # Timestamps
        # created_at may be datetime or ISO string; handle both
        if bid_data.get("created_at"):
            try:
                if isinstance(bid_data["created_at"], datetime):
                    created_at = bid_data["created_at"]
                else:
                    created_at = datetime.fromisoformat(
                        str(bid_data["created_at"]).replace("Z", "+00:00")
                    )
            except Exception:
                created_at = datetime.now(timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)
        started_at = None
        if bid_data.get("started_at"):
            try:
                started_at = (
                    bid_data["started_at"]
                    if isinstance(bid_data["started_at"], datetime)
                    else datetime.fromisoformat(str(bid_data["started_at"]).replace("Z", "+00:00"))
                )
            except Exception:
                started_at = None
        completed_at = None
        if bid_data.get("completed_at"):
            try:
                completed_at = (
                    bid_data["completed_at"]
                    if isinstance(bid_data["completed_at"], datetime)
                    else datetime.fromisoformat(
                        str(bid_data["completed_at"]).replace("Z", "+00:00")
                    )
                )
            except Exception:
                completed_at = None

        # Instance type
        instance_type_id = bid_data.get("instance_type", "")
        if instance_type_id:
            instance_type = self._get_instance_type_name(instance_type_id)
        elif config and config.instance_type:
            instance_type = config.instance_type
        else:
            instance_type = "unknown"

        # Instances count and region
        num_instances = bid_data.get(
            "instance_quantity",
            bid_data.get("num_instances", config.num_instances if config else 1),
        )
        region = bid_data.get("region", config.region if config else self._default_region)

        # Cost per hour
        cost_per_hour = self._determine_cost_per_hour(
            bid_data, status, instance_type_id, region, fetch_instance_details
        )

        # Total cost
        total_cost = None
        if started_at and (completed_at or status == TaskStatus.RUNNING):
            duration_hours = (
                (completed_at or datetime.now(timezone.utc)) - started_at
            ).total_seconds() / 3600
            try:
                cost_value = float(cost_per_hour.strip("$"))
            except Exception:
                cost_value = 0.0
            try:
                total_cost = f"${duration_hours * cost_value * (num_instances or 1):.2f}"
            except Exception:
                total_cost = None

        # SSH info
        ssh_host = None
        ssh_port = self._default_ssh_port
        ssh_command = None
        instances = bid_data.get("instances", [])
        instance_created_at = None

        # Prefer centralized resolver when available to avoid stale endpoints.
        if self._ssh_resolver and fetch_instance_details:
            try:
                try:
                    from flow.application.config.runtime import (
                        settings as _settings,  # local import
                    )

                    debug = bool((_settings.ssh or {}).get("debug", False))
                except Exception:
                    debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
                host, port = self._ssh_resolver.resolve(task_id, tcp_probe=False, debug=debug)  # type: ignore[attr-defined]
                if host:
                    ssh_host = host
                    try:
                        ssh_port = int(port or self._default_ssh_port)
                    except Exception:
                        ssh_port = self._default_ssh_port
            except Exception:
                # Fall back to legacy logic below
                pass

        if not ssh_host and instances and isinstance(instances, list):
            chosen: dict | str | None = None

            # Prefer dict instances; otherwise resolve strings (optionally with details)
            dict_instances = [inst for inst in instances if isinstance(inst, dict)]
            if dict_instances:
                # Choose most recent non-terminated/cancelled, else last
                for inst in reversed(dict_instances):
                    inst_status = str(inst.get("status", "")).lower()
                    if debug:
                        print(
                            f"[build_task] bid={task_id} dict-inst status={inst_status} ssh_dest={inst.get('ssh_destination')} public_ip={inst.get('public_ip')}"
                        )
                    if not any(s in inst_status for s in ("termin", "cancel")):
                        chosen = inst
                        break
                if chosen is None:
                    chosen = dict_instances[-1]
            else:
                # Instances are IDs; if allowed, fetch details and pick a live one
                if fetch_instance_details:
                    for inst_id in reversed(instances):
                        if not isinstance(inst_id, str):
                            continue
                        inst_data = self._fetch_instance_details(inst_id)
                        if not inst_data:
                            continue
                        inst_status = str(inst_data.get("status", "")).lower()
                        if debug:
                            print(
                                f"[build_task] bid={task_id} fetched inst={inst_id} status={inst_status} ssh_dest={inst_data.get('ssh_destination')} public_ip={inst_data.get('public_ip')}"
                            )
                        # Take the first non-terminated; keep updating so we fall back to the latest
                        chosen = inst_data
                        if not any(s in inst_status for s in ("termin", "cancel")):
                            break
                else:
                    # No details requested; assume the latest id is most recent
                    chosen = instances[-1]

            # Populate SSH info from the chosen instance
            if isinstance(chosen, dict):
                ssh_destination = chosen.get("ssh_destination")
                if ssh_destination:
                    from flow.adapters.providers.builtin.mithril.domain.ssh_access import (
                        parse_ssh_destination,
                    )

                    ssh_host, ssh_port = parse_ssh_destination(ssh_destination)
                else:
                    public_ip = chosen.get("public_ip")
                    if public_ip:
                        ssh_host = public_ip
                        ssh_port = self._default_ssh_port
                if chosen.get("created_at"):
                    try:
                        instance_created_at = datetime.fromisoformat(
                            str(chosen["created_at"]).replace("Z", "+00:00")
                        )
                    except Exception:
                        instance_created_at = None
            # If chosen is a plain string, we could not enrich; leave ssh_host None

            if ssh_host:
                ssh_command = f"ssh -p {ssh_port} {self._default_ssh_user}@{ssh_host}"

        # If still no ssh_host (instances list stale), try enriching from the instance ids we have
        if not ssh_host and fetch_instance_details and isinstance(instances, list):
            try:
                for inst_id in reversed(instances):
                    if not isinstance(inst_id, str):
                        continue
                    doc = self._fetch_instance_details(inst_id)
                    if not doc:
                        continue
                    st = str(doc.get("status", "")).lower()
                    ssh_destination = doc.get("ssh_destination")
                    public_ip = doc.get("public_ip")
                    host: str | None = None
                    port: int = self._default_ssh_port
                    if ssh_destination:
                        from flow.adapters.providers.builtin.mithril.domain.ssh_access import (
                            parse_ssh_destination,
                        )

                        host, port = parse_ssh_destination(ssh_destination)
                    elif public_ip:
                        host = public_ip
                    if debug:
                        print(
                            f"[build_task] fallback inst={inst_id} status={st} host={host} port={port}"
                        )
                    if host:
                        ssh_host, ssh_port = host, port
                        if doc.get("created_at"):
                            try:
                                instance_created_at = datetime.fromisoformat(
                                    str(doc["created_at"]).replace("Z", "+00:00")
                                )
                            except Exception:
                                instance_created_at = None
                        # Prefer non-terminated; if this one is terminated, keep going to find a live one
                        if not any(s in st for s in ("termin", "cancel")):
                            break
            except Exception:
                pass

        # Final resort: project-scan by bid to find a live instance (spec: /v2/instances?project=)
        if not ssh_host and fetch_instance_details:
            try:
                all_docs = self._instances.list_project_instances_by_bid(task_id, max_pages=3)
                for doc in reversed(all_docs):  # latest first
                    st = str(doc.get("status", "")).lower()
                    if any(s in st for s in ("termin", "cancel")):
                        continue
                    ssh_destination = doc.get("ssh_destination")
                    public_ip = doc.get("public_ip")
                    host: str | None = None
                    port: int = self._default_ssh_port
                    if ssh_destination:
                        from flow.adapters.providers.builtin.mithril.domain.ssh_access import (
                            parse_ssh_destination,
                        )

                        host, port = parse_ssh_destination(ssh_destination)
                    elif public_ip:
                        host = public_ip
                    if host:
                        ssh_host, ssh_port = host, port
                        if doc.get("created_at"):
                            try:
                                instance_created_at = datetime.fromisoformat(
                                    str(doc["created_at"]).replace("Z", "+00:00")
                                )
                            except Exception:
                                instance_created_at = None
                        break
            except Exception:
                pass

        if debug:
            print(f"[build_task] bid={task_id} final ssh_host={ssh_host} ssh_port={ssh_port}")

        # Provider metadata
        provider_metadata: dict[str, Any] = {
            "provider": "mithril",
            "bid_id": task_id,
            "bid_status": bid_data.get("status", "unknown"),
            "instance_type_id": instance_type_id,
            "limit_price": bid_data.get("limit_price"),
        }

        # Attach origin hint only for tasks created by this process (fresh submission path)
        if config is not None:
            try:
                from flow.cli.utils.origin import detect_origin as _detect_origin

                provider_metadata["origin"] = _detect_origin()
            except Exception:
                pass
        else:
            # Fallback: infer origin from startup script header embedded in bid launch_specification
            try:
                ls = bid_data.get("launch_specification")
                script = None
                if isinstance(ls, dict):
                    script = ls.get("startup_script")
                if not script:
                    script = bid_data.get("startup_script")  # defensive fallback
                if isinstance(script, str) and script:
                    for line in script.splitlines()[:6]:
                        m = re.match(r"^#\s*FLOW_ORIGIN:\s*([A-Za-z0-9_-]+)", line)
                        if m:
                            provider_metadata["origin"] = m.group(1).lower()
                            break
            except Exception:
                pass

        # Price competitiveness for pending bids
        if status == TaskStatus.PENDING and instance_type_id and region and fetch_instance_details:
            try:
                market_price = self._pricing.get_current_market_price(instance_type_id, region)
                if market_price:
                    provider_metadata["market_price"] = market_price
                    bid_val = self._pricing.parse_price(str(bid_data.get("limit_price", "")))
                    if bid_val and market_price:
                        if bid_val < market_price:
                            diff = market_price - bid_val
                            provider_metadata["price_competitiveness"] = "below_market"
                            provider_metadata["price_diff"] = diff
                            provider_metadata["price_message"] = (
                                f"Your bid is ${diff:.2f}/hour below market price"
                            )
                        elif bid_val > market_price * 1.2:
                            diff = bid_val - market_price
                            provider_metadata["price_competitiveness"] = "above_market"
                            provider_metadata["price_diff"] = diff
                            provider_metadata["price_message"] = (
                                f"Your bid is ${diff:.2f}/hour above market price"
                            )
                        else:
                            provider_metadata["price_competitiveness"] = "at_market"
                            provider_metadata["price_message"] = (
                                "Your bid is competitive with market price"
                            )
            except Exception:
                pass

        # Instance-level state
        if instances and isinstance(instances, list) and instances[0]:
            first = instances[0]
            if isinstance(first, dict):
                inst_status = first.get("status", "")
                if inst_status:
                    # Normalize to canonical INSTANCE status form expected by CLI formatters
                    provider_metadata["instance_status"] = self._normalize_instance_status(
                        str(inst_status)
                    )

        # Console link
        from flow.utils.links import WebLinks

        provider_metadata["web_console_url"] = WebLinks.instances_spot()

        task = Task(
            task_id=task_id,
            name=name,
            status=status,
            config=config,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            created_by=bid_data.get("created_by"),
            instance_created_at=instance_created_at,
            instance_type=instance_type,
            num_instances=num_instances,
            region=region,
            cost_per_hour=cost_per_hour,
            total_cost=total_cost,
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_command=ssh_command,
            instances=[
                inst.get("fid", "") if isinstance(inst, dict) else str(inst)
                for inst in (instances or [])
            ],
            message=bid_data.get("message"),
            provider_metadata=provider_metadata,
        )

        return task

    def build_task_from_reservation(self, reservation: Reservation, config: TaskConfig) -> Task:
        """Build a synthetic Task representing a scheduled/active reservation.

        The task is a UX handle: it will show pending until the reservation becomes
        active and instances are allocated. Logs/SSH become available only once
        instances boot and the startup script has executed.
        """
        # Map reservation status to TaskStatus for display
        status_map: dict[str, TaskStatus] = {
            "scheduled": TaskStatus.PENDING,
            "pending": TaskStatus.PENDING,
            "active": TaskStatus.RUNNING,
            "running": TaskStatus.RUNNING,
            "allocated": TaskStatus.RUNNING,
            "expired": TaskStatus.COMPLETED,
            "completed": TaskStatus.COMPLETED,
            "ended": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED,
            "canceled": TaskStatus.FAILED,
            "cancelled": TaskStatus.FAILED,
        }

        raw_status = (
            reservation.status.value
            if hasattr(reservation.status, "value")
            else str(reservation.status)
        )
        task_status = status_map.get(str(raw_status).lower(), TaskStatus.PENDING)

        bid_like: dict[str, Any] = {
            "fid": reservation.reservation_id,
            "task_name": getattr(config, "name", "reservation-task"),
            "status": task_status.value,
            "created_at": (reservation.start_time_utc or datetime.now(timezone.utc)).isoformat(),
            "instance_type": reservation.instance_type,
            "region": reservation.region,
            "limit_price": "$0",
            "instances": [],
        }

        task = self.build_task(bid_like, config=config)
        try:
            # Attach reservation metadata for downstream consumers
            meta = {
                "reservation_id": reservation.reservation_id,
                "status": raw_status,
                "start_time": (
                    reservation.start_time_utc.isoformat() if reservation.start_time_utc else None
                ),
                "end_time": (
                    reservation.end_time_utc.isoformat() if reservation.end_time_utc else None
                ),
            }
            task.provider_metadata = {**(task.provider_metadata or {}), "reservation": meta}
        except Exception:
            pass
        return task

    # ------------------------- helpers -------------------------

    def _fetch_instance_details(self, instance_id: str) -> dict[str, Any] | None:
        try:
            return self._instances.get_instance(instance_id)
        except Exception:
            return None

    def _map_mithril_status_to_enum(self, mithril_status: str) -> TaskStatus:
        if not mithril_status:
            return TaskStatus.PENDING
        normalized = mithril_status.lower().strip()
        mapped = STATUS_MAPPINGS.get(normalized)
        if mapped:
            return TaskStatus[mapped]
        if "alloc" in normalized:
            return TaskStatus.RUNNING
        if "termin" in normalized or "cancel" in normalized:
            return TaskStatus.CANCELLED
        if "fail" in normalized or "error" in normalized:
            return TaskStatus.FAILED
        if "complete" in normalized or "success" in normalized:
            return TaskStatus.COMPLETED
        if "open" in normalized:
            return TaskStatus.PENDING
        return TaskStatus.PENDING

    def _normalize_instance_status(self, instance_status: str) -> str:
        """Normalize provider instance status to canonical STATUS_* strings.

        Accepts values like "running", "Allocated", or already canonical
        forms like "STATUS_RUNNING" and returns canonical variants used by
        CLI display logic (TaskFormatter.get_display_status).
        """
        if not instance_status:
            return "STATUS_PENDING"
        s = str(instance_status).strip()
        lower = s.lower()
        # Pass-through if already canonical
        if s.startswith("STATUS_"):
            return s
        if lower in {"pending", "provisioning", "scheduled"}:
            return "STATUS_SCHEDULED" if lower == "scheduled" else "STATUS_PENDING"
        if lower in {"new", "confirmed", "initializing", "starting"}:
            return "STATUS_STARTING"
        if lower in {"running", "allocated"}:
            return "STATUS_RUNNING"
        if lower in {"stopping"}:
            return "STATUS_STOPPING"
        if lower in {"stopped"}:
            return "STATUS_STOPPED"
        if any(k in lower for k in ("preempt",)):
            return "STATUS_PREEMPTING"
        if any(k in lower for k in ("relocat",)):
            return "STATUS_RELOCATING"
        if any(k in lower for k in ("terminat")):
            return "STATUS_TERMINATED"
        return "STATUS_PENDING"

    # Public wrappers to avoid cross-object private access from provider facade
    def map_mithril_status_to_enum(self, mithril_status: str) -> TaskStatus:
        return self._map_mithril_status_to_enum(mithril_status)

    def _determine_cost_per_hour(
        self,
        bid_data: dict[str, Any],
        status: TaskStatus,
        instance_type_id: str,
        region: str,
        fetch_details: bool,
    ) -> str:
        if (
            status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]
            and instance_type_id
            and region
            and fetch_details
        ):
            try:
                market_price = self._pricing.get_current_market_price(instance_type_id, region)
                if market_price:
                    return f"${market_price:.2f}"
            except Exception:
                pass
        limit_price = bid_data.get("limit_price", "$0")
        return limit_price if isinstance(limit_price, str) else f"${limit_price}"

    # Removed _parse_ssh_destination; use flow.providers.mithril.domain.ssh_access.parse_ssh_destination()

    def _is_more_specific_type(self, type1: str, type2: str) -> bool:
        """Return True if type1 is more specific than type2.

        Specificity heuristic:
        - Prefer higher GPUs per node
        - If equal, prefer types that specify non-default memory
        - If equal, prefer types that specify interconnect
        """
        try:
            c1 = parse_instance_spec(type1)
            c2 = parse_instance_spec(type2)

            # If both types represent H100 8x in different notations, consider them equal (not more specific)
            try:
                if (
                    c1.gpu_type == "h100"
                    and c2.gpu_type == "h100"
                    and c1.gpu_count == 8
                    and c2.gpu_count == 8
                ):
                    return False
            except Exception:
                pass

            # Prefer higher GPU counts; treat implicit (None) as 0 so that 1xa100 > a100
            if c1.gpu_count != c2.gpu_count:
                g1 = c1.gpu_count if c1.gpu_count is not None else 0
                g2 = c2.gpu_count if c2.gpu_count is not None else 0
                return g1 > g2

            # Prefer explicit non-default memory
            d1 = get_default_gpu_memory(c1.gpu_type)
            d2 = get_default_gpu_memory(c2.gpu_type)
            m1_specific = (c1.memory_gb is not None) and (c1.memory_gb != d1)
            m2_specific = (c2.memory_gb is not None) and (c2.memory_gb != d2)
            if m1_specific != m2_specific:
                return m1_specific and not m2_specific

            # Prefer explicit interconnect
            i1 = bool(c1.interconnect)
            i2 = bool(c2.interconnect)
            if i1 != i2:
                return i1 and not i2

            # Finally, if GPU counts equal numerically (including both 1 or both None treated as 1),
            # prefer explicit count over implicit. Example: 1xa100 is more specific than a100.
            try:
                import re as _re

                p1 = parse_instance_spec(type1)
                p2 = parse_instance_spec(type2)
                g1 = p1.gpu_count or 1
                g2 = p2.gpu_count or 1
                if g1 == g2:
                    # Detect explicit count in the original string (not the parsed default)
                    explicit_pattern = _re.compile(r"(^\d+x)|x\d+$|\.\d+x$", _re.IGNORECASE)
                    has_count_1 = bool(explicit_pattern.search(type1))
                    has_count_2 = bool(explicit_pattern.search(type2))
                    if has_count_1 != has_count_2:
                        return has_count_1 and not has_count_2
            except Exception:
                pass
            return False
        except Exception:
            import re as _re

            m1 = _re.match(r"(\d+)x(.+)", type1.lower())
            m2 = _re.match(r"(\d+)x(.+)", type2.lower())
            if m1 and not m2:
                return True
            if m2 and not m1:
                return False
            if m1 and m2:
                c1_num, c2_num = int(m1.group(1)), int(m2.group(1))
                if c1_num != c2_num:
                    return c1_num > c2_num
            return False

    def _get_instance_type_name(self, instance_id: str) -> str:
        from flow.adapters.providers.builtin.mithril.core.constants import INSTANCE_TYPE_NAMES

        # Prefer static reverse mapping when available
        if instance_id in INSTANCE_TYPE_NAMES:
            name = INSTANCE_TYPE_NAMES[instance_id]
            # Policy:
            # - Primary H100 ID → canonical short form '8xh100'
            # - All other IDs → return the provider-native display name unchanged
            if instance_id == "it_5ECSoHQjLBzrp5YM":
                return "8xh100"
            return name

        # Fallback: build reverse from forward mappings (best-effort)
        reverse: dict[str, str] = {}
        for name, fid in INSTANCE_TYPE_MAPPINGS.items():
            if fid not in reverse or self._is_more_specific_type(name, reverse[fid]):
                reverse[fid] = name
        if instance_id in reverse:
            mapped = reverse[instance_id]
            # Normalize mapped value using the same simplified canonicalization
            # For reverse-derived names, prefer simplified canonicalization where possible
            try:
                comp = parse_instance_spec(mapped)
                gpu = comp.gpu_type or "gpu"
                default_mem = get_default_gpu_memory(gpu)
                mem_suffix = (
                    f"-{comp.memory_gb}gb"
                    if comp.memory_gb and comp.memory_gb != default_mem
                    else ""
                )
                if (comp.gpu_count or 1) > 1:
                    return f"{comp.gpu_count}x{gpu}{mem_suffix}"
                return f"{gpu}{mem_suffix}"
            except Exception:
                return mapped

        upper = instance_id.upper()
        gpu_patterns: list[tuple[str, list[str]]] = [
            ("A100", ["A100", "AMPERE"]),
            ("H100", ["H100", "HOPPER"]),
            ("A10", ["A10"]),
            ("V100", ["V100", "VOLTA"]),
            ("T4", ["T4", "TURING"]),
            ("L4", ["L4"]),
            ("A40", ["A40"]),
        ]
        for gpu_name, patterns in gpu_patterns:
            if any(p in upper for p in patterns):
                return f"GPU-{gpu_name}"
        if instance_id.startswith(("it_", "IT_")):
            return "GPU"
        return instance_id

    def get_instance_type_name(self, instance_id: str) -> str:
        return self._get_instance_type_name(instance_id)
