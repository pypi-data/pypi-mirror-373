"""Reservations service for list/show/availability shaping."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime as _dt
from datetime import timedelta as _td
from datetime import timezone as _tz
from typing import Any

from flow.sdk.client import Flow
from flow.sdk.factory import create_client


@dataclass
class AvailabilityQuery:
    instance_type: str
    region: str
    earliest_start_time: str
    latest_end_time: str
    quantity: int | None = None
    duration_hours: int | None = None
    mode: str | None = None


class ReservationsService:
    # Expose query model as a class attribute for convenient access
    # (referenced as ReservationsService.AvailabilityQuery in CLI/UI code)
    AvailabilityQuery = AvailabilityQuery

    def __init__(self, flow: Flow | None = None) -> None:
        # Prefer factory to avoid direct client construction in CLI layer
        self._flow = flow or create_client(auto_init=True)
        self._provider = self._flow.provider
        self._facets = None  # lazy facet cache

    # --------------- Internal utilities ---------------
    @staticmethod
    def _get_any_attr_or_key(obj: object, *names: str) -> str | None:
        """Return the first non-empty attribute or dict key value as a string.

        Accepts heterogeneous API shapes (objects or dicts). Returns None if not found.
        """
        for name in names:
            try:
                if isinstance(obj, dict):
                    val = obj.get(name)
                else:
                    val = getattr(obj, name, None)
                if val:  # non-empty
                    return str(val)
            except Exception:
                continue
        return None

    def _call_reservations_method(
        self,
        facet_method: str,
        provider_fallbacks: tuple[str, ...],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Try reservations facet first, then provider method fallbacks.

        - facet_method: name on facets.reservations (if available)
        - provider_fallbacks: one or more method names to try on provider
        Returns None on unsupported or errors.
        """
        facets = self._get_facets()
        try:
            if facets and getattr(facets, "reservations", None) is not None:
                fn = getattr(facets.reservations, facet_method, None)
                if callable(fn):
                    return fn(*args, **kwargs)
        except Exception:
            pass

        for name in provider_fallbacks:
            try:
                fn = getattr(self._provider, name, None)
                if callable(fn):
                    return fn(*args, **kwargs)
            except Exception:
                # Try next fallback
                continue
        return None

    # --------------- Offer helpers (family filtering) ---------------
    @staticmethod
    def _filter_offers_by_family(offers: list[object], selected_family: str | None) -> list[object]:
        """Filter a heterogeneous list of offers by accelerator family.

        Strategy (robust to varied provider shapes):
        - Prefer direct string match on common name fields (accelerator_model, instance_type,
          sku, display_name, name) using equality or prefix (e.g., "h100-*").
        - Fall back to family inference from human-readable labels.
        - As a last resort, map a fid/id to a name via provider constants and re-try.
        Returns original list if no family is provided.
        """
        if not selected_family:
            return offers
        family = str(selected_family).lower().strip()

        try:
            from flow.domain.parsers.instance_parser import (
                infer_gpu_family_from_name as _infer,
            )
        except Exception:
            _infer = None  # type: ignore[assignment]

        try:
            from flow.adapters.providers.builtin.mithril.core.constants import (
                INSTANCE_TYPE_NAMES as _IT_NAMES,
            )
        except Exception:
            _IT_NAMES = {}  # type: ignore[assignment]

        def _text_candidates(o: object) -> list[str]:
            vals: list[str] = []
            # Common textual fields across providers
            for key in (
                "accelerator_model",
                "gpu_model",
                "gpu_type",
                "instance_type",
                "sku",
                "display_name",
                "name",
            ):
                v = ReservationsService._get_any_attr_or_key(o, key)
                if v:
                    vals.append(v)
            # GPU sub-objects (e.g., Mithril InstanceTypeModel.gpus)
            try:
                gpus = getattr(o, "gpus", None) if not isinstance(o, dict) else o.get("gpus")
                if isinstance(gpus, list):
                    for g in gpus:
                        gv = ReservationsService._get_any_attr_or_key(g, "name", "model")
                        if gv:
                            vals.append(gv)
            except Exception:
                pass
            # Append mapped name when only fid/id exists
            fid = ReservationsService._get_any_attr_or_key(o, "fid", "id")
            mapped = _IT_NAMES.get(str(fid)) if fid else None
            if mapped:
                vals.append(str(mapped))
            # Lowercase unique
            seen: set[str] = set()
            out: list[str] = []
            for v in vals:
                v2 = str(v).lower()
                if v2 and v2 not in seen:
                    seen.add(v2)
                    out.append(v2)
            return out

        def _matches_family(o: object) -> bool:
            labels = _text_candidates(o)
            for t in labels:
                # direct matches and common separators
                if t == family or t.startswith(f"{family}-") or t.startswith(f"{family}."):
                    return True
            if callable(_infer):
                for t in labels:
                    fam = _infer(t)
                    if fam and fam.lower() == family:
                        return True
            return False

        try:
            return [o for o in (offers or []) if _matches_family(o)]
        except Exception:
            return offers

    def _get_facets(self):
        if self._facets is not None:
            return self._facets
        try:
            from flow.adapters.providers.registry import ProviderRegistry  # local import

            self._facets = ProviderRegistry.facets_for_instance(self._provider)
            return self._facets
        except Exception:
            return None

    def availability(self, q: AvailabilityQuery) -> list[dict[str, Any]]:
        # Normalize query into provider-friendly params
        num_nodes = int(q.quantity) if getattr(q, "quantity", None) else 1
        duration_hours = int(q.duration_hours) if getattr(q, "duration_hours", None) else 8

        params = {
            "instance_type": q.instance_type,
            "num_nodes": num_nodes,
            "duration_hours": duration_hours,
            "region": q.region,
            "earliest_start_time": q.earliest_start_time,
            "latest_end_time": q.latest_end_time,
        }
        # Include mode pass-through only when provided (best-effort, provider may ignore)
        if getattr(q, "mode", None):
            params["mode"] = q.mode
        params = {k: v for k, v in params.items() if v is not None}

        # Prefer reservations facet when available; fall back to provider or empty
        results = (
            self._call_reservations_method(
                "get_reservation_availability",
                ("get_reservation_availability",),
                **params,
            )
            or []
        )
        slots = results.get("data", results) if isinstance(results, dict) else results
        return [s for s in (slots or []) if isinstance(s, dict)]

    def list(self) -> list[object]:
        res = self._call_reservations_method("list_reservations", ("list_reservations",)) or []
        try:
            return list(res or [])
        except Exception:
            return []

    def show(self, reservation_id: str) -> object | None:
        return self._call_reservations_method(
            "get_reservation",
            ("get_reservation",),
            reservation_id,
        )

    # --------------- Extensions (experimental) ---------------
    def extension_availability(self, reservation_id: str) -> list[dict[str, Any]]:
        """Return extension availability windows for a reservation when supported.

        Falls back to empty list when unsupported or on error.
        """
        res = self._call_reservations_method(
            "get_extension_availability",
            ("get_extension_availability", "get_reservation_extension_availability"),
            reservation_id,
        )
        if res is None:
            return []
        slots = res.get("data", res) if isinstance(res, dict) else res
        return [s for s in (slots or []) if isinstance(s, dict)]

    def extend(self, reservation_id: str, end_time_iso_z: str) -> Any | None:
        """Extend a reservation to the specified end time when supported.

        Returns provider response or None when unsupported.
        """
        return self._call_reservations_method(
            "extend_reservation",
            ("extend_reservation", "reservation_extend"),
            reservation_id,
            end_time_iso_z,
        )

    # --------------- Provider capabilities and caching ---------------
    def supports_reservations(self) -> bool:
        try:
            caps = self._provider.get_capabilities()
            return bool(getattr(caps, "supports_reservations", False))
        except Exception:
            # If capability lookup fails, allow upper layer to proceed and surface provider error
            return True

    def list_with_prefetch(self) -> tuple[list[object], bool]:
        """Return (items, supported) where supported indicates provider support.

        Uses prefetch cache when available for faster UX.
        """
        try:
            if hasattr(self._provider, "list_reservations"):
                try:
                    from flow.cli.utils.prefetch import get_cached  # type: ignore

                    cached = get_cached("reservations")
                except Exception:
                    cached = None
                items = cached or self._provider.list_reservations()
                return list(items or ()), True
            return [], False
        except Exception:
            raise

    # --------------- Helpers to slim CLI commands ---------------
    @staticmethod
    def parse_time_expr(expr: str) -> str:
        """Parse an absolute ISO8601 or relative time expression to ISO8601 Z string.

        Supports:
        - "now" / "now()"
        - Relative: "+2h", "+30m", "+1d" (also accepts leading "+" without "now+")
        - Absolute ISO8601 with optional trailing "Z"
        Fallback: returns the original string on failure (let provider validate).
        """
        try:
            s = (expr or "").strip().lower()
            if s in {"now", "now()"}:
                return ReservationsService.isoformat_utc_z(_dt.utcnow())
            if s.startswith("now+") or s.startswith("+"):
                plus = s.replace("now+", "+", 1)
                val = plus[1:]
                num = "".join(ch for ch in val if ch.isdigit())
                unit = val[len(num) :] if num else "h"
                n = int(num or "0")
                if unit in {"h", "hr", "hrs", "hour", "hours"}:
                    dt = _dt.utcnow() + _td(hours=n)
                elif unit in {"m", "min", "mins", "minute", "minutes"}:
                    dt = _dt.utcnow() + _td(minutes=n)
                elif unit in {"d", "day", "days"}:
                    dt = _dt.utcnow() + _td(days=n)
                else:
                    dt = _dt.utcnow()
                return ReservationsService.isoformat_utc_z(dt)
            _ = _dt.fromisoformat(expr.replace("Z", "+00:00"))
            return expr
        except Exception:
            return expr

    @staticmethod
    def parse_duration_to_hours(s: str, *, default_hours: int = 8) -> int:
        """Parse duration strings like '90m', '2h', '1d2h30m', '1.5h', '0.5d', or bare hours.

        Returns whole hours, rounding up when minutes/decimals are provided. Falls back to default on error.
        """
        try:
            import re as _re

            text = (s or "").strip().lower()
            if not text:
                return max(1, int(default_hours))
            # Bare number = hours
            if text.isdigit():
                return max(1, int(text))
            # Pattern: series of number+unit (allow decimals for h/d)
            total_minutes = 0.0
            for num, unit in _re.findall(
                r"(\d+(?:\.\d+)?)\s*(d|day|days|h|hr|hrs|hour|hours|m|min|mins|minute|minutes)",
                text,
            ):
                val = float(num)
                if unit in {"d", "day", "days"}:
                    total_minutes += val * 24 * 60
                elif unit in {"h", "hr", "hrs", "hour", "hours"}:
                    total_minutes += val * 60
                elif unit in {"m", "min", "mins", "minute", "minutes"}:
                    total_minutes += val
            if total_minutes <= 0:
                # Last resort: try float hours like '1.5'
                try:
                    return max(1, int(float(text) + 0.9999))
                except Exception:
                    return max(1, int(default_hours))
            # Round up to nearest whole hour
            hours = int((total_minutes + 59.999) // 60)
            return max(1, hours)
        except Exception:
            return max(1, int(default_hours))

    @staticmethod
    def _to_dt(v: Any) -> _dt | None:
        try:
            if isinstance(v, _dt):
                return v
            return _dt.fromisoformat(str(v).replace("Z", "+00:00"))
        except Exception:
            return None

    @classmethod
    def slot_duration_hours(cls, slot: dict[str, Any]) -> int:
        start = cls._to_dt(
            slot.get("start_time_utc") or slot.get("start") or slot.get("start_time")
        )
        end = cls._to_dt(slot.get("end_time_utc") or slot.get("end") or slot.get("end_time"))
        if not start or not end:
            return 0
        try:
            return max(0, int(round((end - start).total_seconds() / 3600)))
        except Exception:
            return 0

    @staticmethod
    def normalize_slots(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        def _norm(slot: dict[str, Any]) -> dict[str, Any]:
            st = slot.get("start_time_utc") or slot.get("start_time") or slot.get("start")
            et = slot.get("end_time_utc") or slot.get("end_time") or slot.get("end")
            qty = slot.get("quantity")
            return {
                "start_time_utc": st,
                "end_time_utc": et,
                "quantity": int(qty or 0),
                "region": slot.get("region"),
                "instance_type": slot.get("instance_type"),
            }

        return [_norm(s) for s in slots if isinstance(s, dict)]

    @classmethod
    def filter_slots(
        cls,
        slots: list[dict[str, Any]],
        *,
        min_quantity: int | None = None,
        min_duration_hours: int | None = None,
    ) -> list[dict[str, Any]]:
        filtered = list(slots)
        if min_quantity is not None:
            try:
                q = max(1, int(min_quantity))
                filtered = [s for s in filtered if int(s.get("quantity", 0) or 0) >= q]
            except Exception:
                pass
        if min_duration_hours is not None:
            try:
                dh = int(min_duration_hours)
                filtered = [s for s in filtered if cls.slot_duration_hours(s) >= dh]
            except Exception:
                pass
        # Sort by start time ascending
        filtered.sort(key=lambda s: (cls._to_dt(s.get("start_time_utc")) or _dt.max))
        return filtered

    @staticmethod
    def isoformat_utc_z(dt_like: Any) -> str:
        """Return ISO8601 UTC with trailing 'Z' from datetime or string."""
        try:
            if isinstance(dt_like, _dt):
                return (
                    dt_like.astimezone(_tz.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
            dt = _dt.fromisoformat(str(dt_like).replace("Z", "+00:00"))
            return dt.astimezone(_tz.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except Exception:
            # Best effort: return as string
            return str(dt_like)

    def create_reservation(
        self,
        *,
        instance_type: str,
        region: str | None,
        quantity: int,
        start_time_iso_z: str,
        duration_hours: int,
        name: str | None = None,
        ssh_keys: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> Any:
        """Create a reservation by calling run() with a reserved TaskConfig."""
        from flow.sdk.models import TaskConfig

        cfg_updates: dict[str, Any] = {
            "name": name or f"reservation-{instance_type}",
            "instance_type": instance_type,
            "num_instances": int(quantity),
            "ssh_keys": list(ssh_keys or ()),
            "allocation_mode": "reserved",
            "scheduled_start_time": start_time_iso_z,
            "reserved_duration_hours": int(duration_hours),
        }
        if region:
            cfg_updates["region"] = region
        if env:
            cfg_updates["env"] = env
        config = TaskConfig(**cfg_updates)
        return self._flow.run(config)

    # --------------- Reservations list helpers ---------------
    @staticmethod
    def _status_value(res: Any) -> str:
        st = getattr(res, "status", None)
        return (getattr(st, "value", None) or str(st or "")).lower()

    @staticmethod
    def _has_slurm(res: Any) -> bool:
        meta = getattr(res, "provider_metadata", {}) or {}
        return bool(meta.get("slurm"))

    def filter_reservations(
        self,
        reservations: list[Any],
        *,
        status: str | None = None,
        region: str | None = None,
        instance_type: str | None = None,
        slurm_only: bool = False,
    ) -> list[Any]:
        items = list(reservations)
        if slurm_only:
            items = [it for it in items if self._has_slurm(it)]
        if status:
            status_l = status.lower()
            items = [it for it in items if self._status_value(it) == status_l]
        if region:
            items = [it for it in items if str(getattr(it, "region", "")) == region]
        if instance_type:
            items = [it for it in items if str(getattr(it, "instance_type", "")) == instance_type]
        return items

    # --------------- Telemetry helper ---------------
    @staticmethod
    def telemetry(event: str, payload: dict[str, Any]) -> None:
        try:
            from flow.cli.utils.telemetry import Telemetry as _Telemetry

            _Telemetry().log_event(event, payload)
        except Exception:
            pass
