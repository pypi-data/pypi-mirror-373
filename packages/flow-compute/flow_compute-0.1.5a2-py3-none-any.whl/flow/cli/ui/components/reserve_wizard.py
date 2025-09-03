from __future__ import annotations

"""Reserve wizard: interactive, default-first flow for 'flow reserve'."""

from dataclasses import dataclass
from datetime import datetime as _dt
from datetime import timedelta as _td
from datetime import timezone as _tz

from rich.console import Console

from flow.cli.services.reservations_service import ReservationsService as _RS
from flow.cli.ui.components.models import SelectionItem
from flow.cli.ui.components.selector import InteractiveSelector
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress as AEP
from flow.cli.ui.presentation.reservations_renderer import ReservationsRenderer
from flow.domain.parsers.instance_parser import infer_gpu_family_from_name


@dataclass
class WizardState:
    project: str | None = None
    instance_type: str | None = None
    region: str | None = None
    duration_hours: int = 8
    quantity: int = 1


class ReserveWizard:
    def __init__(self, console: Console | None = None) -> None:
        from flow.cli.utils.theme_manager import theme_manager

        self.console = console or theme_manager.create_console()
        self._offline: bool = False

    # ---- Small helpers for provider meta/types/regions ----
    def _meta(self, flow):
        try:
            return getattr(getattr(flow, "provider", None), "meta", None)
        except Exception:
            return None

    def _instance_types(self, flow, region: str | None):
        try:
            meta = self._meta(flow)
            if meta and hasattr(meta, "get_instance_types"):
                return meta.get_instance_types(region=region)
        except Exception:
            pass
        return []

    def _valid_regions(self, flow) -> list[str]:
        # Prefer meta capabilities → provider capabilities → constants → small fallback
        try:
            meta = self._meta(flow)
            if meta and hasattr(meta, "get_capabilities"):
                caps = meta.get_capabilities() or {}
                rg = list(caps.get("regions") or [])
                if rg:
                    return rg
        except Exception:
            pass
        try:
            caps = getattr(getattr(flow, "provider", None), "capabilities", None)
            if caps and getattr(caps, "supported_regions", None):
                return list(caps.supported_regions)
        except Exception:
            pass
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import VALID_REGIONS as _VR

            return list(_VR)
        except Exception:
            return ["us-central1-b", "us-central2-a", "eu-central1-a", "eu-central1-b"]

    def _region_gpu_families(self, flow, region: str) -> list[str]:
        """Return a sorted list of GPU families available in a region.

        Prefers provider meta's centralized view when available, falling back to
        inferring from instance types when necessary.
        """
        try:
            meta = self._meta(flow)
            # Prefer centralized provider method when available
            if meta and hasattr(meta, "get_region_gpu_families"):
                fams = meta.get_region_gpu_families(region)
                if fams:
                    # Cross-validate with instance types when available to avoid over-reporting
                    try:
                        if hasattr(meta, "get_instance_types"):
                            raw = meta.get_instance_types(region=region)
                            present: set[str] = set()
                            for it in raw or []:
                                # GPU sub-objects
                                gpus = (
                                    getattr(it, "gpus", None)
                                    if not isinstance(it, dict)
                                    else it.get("gpus")
                                )
                                if isinstance(gpus, list):
                                    for g in gpus:
                                        nm = (
                                            getattr(g, "name", None)
                                            if not isinstance(g, dict)
                                            else g.get("name")
                                        )
                                        fam = (
                                            infer_gpu_family_from_name(str(nm or ""))
                                            if nm
                                            else None
                                        )
                                        if fam:
                                            present.add(fam)
                                # Fallback to instance type name
                                nm2 = (
                                    getattr(it, "name", None)
                                    or (it.get("name") if isinstance(it, dict) else None)
                                    or getattr(it, "display_name", None)
                                    or (it.get("display_name") if isinstance(it, dict) else None)
                                    or getattr(it, "fid", None)
                                    or (it.get("fid") if isinstance(it, dict) else None)
                                )
                                fam2 = infer_gpu_family_from_name(str(nm2 or "")) if nm2 else None
                                if fam2:
                                    present.add(fam2)
                            inter = {f.lower() for f in fams} & {p.lower() for p in present}
                            if inter:
                                fams = sorted(list({f.lower() for f in inter}))
                    except Exception:
                        # Best-effort cross-check; ignore errors
                        pass
                    return sorted(list(set(fams)), key=lambda f: {"h100": 0, "a100": 1}.get(f, 10))
            if not (meta and hasattr(meta, "get_instance_types")):
                return []
            families: set[str] = set()
            raw = meta.get_instance_types(region=region)
            for it in raw or []:
                # Try GPU sub-objects first
                try:
                    gpus = getattr(it, "gpus", None) if not isinstance(it, dict) else it.get("gpus")
                    if isinstance(gpus, list):
                        for g in gpus:
                            nm = (
                                getattr(g, "name", None)
                                if not isinstance(g, dict)
                                else g.get("name")
                            )
                            fam = infer_gpu_family_from_name(str(nm or "")) if nm else None
                            if fam:
                                families.add(fam)
                except Exception:
                    pass
                # Fallback to instance type name-based inference
                try:
                    nm = (
                        getattr(it, "name", None)
                        or (it.get("name") if isinstance(it, dict) else None)
                        or getattr(it, "display_name", None)
                        or (it.get("display_name") if isinstance(it, dict) else None)
                        or getattr(it, "fid", None)
                        or (it.get("fid") if isinstance(it, dict) else None)
                    )
                    fam = infer_gpu_family_from_name(str(nm or "")) if nm else None
                    if fam:
                        families.add(fam)
                except Exception:
                    pass
            # Stable order: H100 then A100 then others alphabetically
            return sorted(list(families), key=lambda f: {"h100": 0, "a100": 1}.get(f, 10))
        except Exception:
            return []

    def _format_family_badges(self, families: list[str]) -> str:
        try:
            ordered = sorted(
                list({f.upper() for f in families}), key=lambda f: {"H100": 0, "A100": 1}.get(f, 10)
            )
            # ASCII-friendly badges
            return " ".join(f"[{f}]" for f in ordered)
        except Exception:
            return ", ".join(families)

    def _map_fid_to_name(self, fid: str | None) -> str | None:
        if not fid:
            return None
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import (
                INSTANCE_TYPE_NAMES as _IT_NAMES,
            )

            return _IT_NAMES.get(str(fid))
        except Exception:
            return None

    def _is_network_reachable(self) -> bool:
        """Best-effort check for network reachability to provider API.

        Never raises; returns False on any error.
        """
        try:
            import os
            import socket
            from urllib.parse import urlparse

            # Allow explicit override for CI or advanced users
            if os.environ.get("FLOW_RESERVE_ALLOW_OFFLINE", "").strip() in {"1", "true", "yes"}:
                return True

            # Use Mithril API base URL when available
            try:
                from flow.adapters.providers.builtin.mithril.core.constants import (
                    MITHRIL_API_BASE_URL,
                )
            except Exception:
                MITHRIL_API_BASE_URL = "https://api.mithril.ai"

            parsed = urlparse(MITHRIL_API_BASE_URL)
            host = parsed.hostname or "api.mithril.ai"
            port = parsed.port or (443 if (parsed.scheme or "https") == "https" else 80)

            with socket.create_connection((host, port), timeout=0.75):
                return True
        except Exception:
            return False

    def _filter_types_by_availability(
        self, flow, region: str | None, items: list[SelectionItem[str]]
    ) -> list[SelectionItem[str]]:
        """Best-effort filter: keep types with any reservation availability in next 7 days.

        Guarded behind try/except to remain resilient when provider lacks support or network is unavailable.
        """
        try:
            if not items:
                return items
            from datetime import datetime as _dt
            from datetime import timedelta as _td
            from datetime import timezone as _tz

            service = _RS(flow)
            # Add a small scheduling buffer to avoid near-now edge cases
            now_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(minutes=30))
            horizon_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(days=7))
            filtered: list[SelectionItem[str]] = []
            limit = 20  # avoid excessive API calls
            for it in items[:limit]:
                try:
                    slots = service.availability(
                        _RS.AvailabilityQuery(
                            instance_type=it.value,
                            region=str(region or ""),
                            earliest_start_time=now_iso,
                            latest_end_time=horizon_iso,
                            quantity=1,
                            duration_hours=8,
                            mode="slots",
                        )
                    )
                    norm = _RS.normalize_slots(slots)
                    if norm:
                        filtered.append(it)
                except Exception:
                    # Skip on error
                    continue
            # If we ended up with none, keep the originals to avoid empty lists
            return filtered or items
        except Exception:
            return items

    def _select(
        self, title: str, options: list[SelectionItem[str]], *, default_index: int = 0
    ) -> str | None:
        try:
            if not options:
                return None
            selector = InteractiveSelector(
                options, title=title, show_keybindings=True, compact_mode=True
            )
            # Clamp default index to valid range
            default_index = min(max(0, int(default_index)), len(options) - 1)
            selector.state.selected_index = default_index
            # Non-interactive/No-TTY fallback: return default option value directly
            try:
                if not selector._check_terminal_compatibility():  # type: ignore[attr-defined]
                    return options[default_index].value
            except Exception:
                # If compatibility check fails, still try interactive path
                pass
            result = selector.select()
            if isinstance(result, SelectionItem):
                return result.value
            if isinstance(result, str):
                return result
            if result is not None:
                return str(result)
            return None
        except Exception:
            return None

    def _choose_project(self, flow) -> str | None:
        # Try config first
        try:
            proj = getattr(flow.config, "project", None)
            if proj:
                return str(proj)
        except Exception:
            pass
        # Fallback: attempt to list via provider facet; guarded since network may be restricted
        try:
            meta = getattr(getattr(flow, "provider", None), "meta", None)
            projects = []
            if meta and hasattr(meta, "get_projects"):
                projects = meta.get_projects() or []
            names = [p.get("name") or p.get("id") for p in projects if isinstance(p, dict)]
            names = [str(n) for n in names if n]
            if not names:
                return None
            items = [
                SelectionItem(value=n, id=n, title=n, subtitle=None, status=None) for n in names
            ]
            return self._select("Select project", items, default_index=0)
        except Exception:
            return None

    def _choose_gpu_type(self, flow) -> str | None:
        """Choose GPU family first, aggregating from provider instance types.

        Falls back to a curated set when provider listing is unavailable.
        """
        families: list[str] = []
        try:
            meta = self._meta(flow)
            if meta and hasattr(meta, "get_instance_types"):
                with AEP(self.console, "Loading instance types", start_immediately=True, pad_top=0):
                    raw = meta.get_instance_types(region=None)  # type: ignore[call-arg]
            else:
                raw = []
            seen: set[str] = set()
            for it in raw or []:
                nm = (
                    getattr(it, "name", None)
                    or (it.get("name") if isinstance(it, dict) else None)
                    or getattr(it, "display_name", None)
                    or (it.get("display_name") if isinstance(it, dict) else None)
                    or getattr(it, "fid", None)
                    or (it.get("fid") if isinstance(it, dict) else None)
                )
                fam = infer_gpu_family_from_name(str(nm or "")) if nm else None
                if fam and fam not in seen:
                    seen.add(fam)
                    families.append(fam)
        except Exception:
            families = []
        # Secondary attempt: if global types failed, try a region-scoped query using
        # configured region or a well-known Mithril region to infer families.
        if not families:
            try:
                meta = self._meta(flow)
                # Prefer configured region
                try:
                    cfg_region = getattr(flow.config, "region", None)
                except Exception:
                    cfg_region = None
                if not cfg_region:
                    try:
                        from flow.adapters.providers.builtin.mithril.core.constants import (
                            VALID_REGIONS as _VR,
                        )

                        ordered = sorted(list(_VR), key=lambda r: 0 if r == "us-central1-b" else 1)
                        cfg_region = ordered[0] if ordered else None
                    except Exception:
                        cfg_region = None
                if meta and hasattr(meta, "get_instance_types") and cfg_region:
                    with AEP(
                        self.console,
                        f"Loading instance types for {cfg_region}",
                        start_immediately=True,
                        pad_top=0,
                    ):
                        raw = meta.get_instance_types(region=cfg_region)
                    seen: set[str] = set()
                    for it in raw or []:
                        nm = (
                            getattr(it, "name", None)
                            or (it.get("name") if isinstance(it, dict) else None)
                            or getattr(it, "display_name", None)
                            or (it.get("display_name") if isinstance(it, dict) else None)
                            or getattr(it, "fid", None)
                            or (it.get("fid") if isinstance(it, dict) else None)
                        )
                        fam = infer_gpu_family_from_name(str(nm or "")) if nm else None
                        if fam and fam not in seen:
                            seen.add(fam)
                            families.append(fam)
            except Exception:
                families = []
        if not families:
            # When provider types aren't available, skip GPU step (fallback to instance types)
            return None
        # Prefer H100 at top
        families = sorted(families, key=lambda x: {"h100": 0, "a100": 1}.get(x, 10))
        items = [
            SelectionItem(value=f, id=f, title=f.upper(), subtitle=None, status=None)
            for f in families
        ]
        return self._select("Select GPU type", items, default_index=0)

    def _choose_instance_type(self, flow, region: str | None, gpu_family: str | None) -> str | None:
        """Fetch instance types from provider (region-aware) with strict filtering and clear fallbacks.

        Uses provider list when available; otherwise falls back to a small curated set.
        """
        try:
            meta = self._meta(flow)
            if meta and hasattr(meta, "get_instance_types"):
                with AEP(
                    self.console,
                    f"Loading instance types for {region or 'region'}",
                    start_immediately=True,
                    pad_top=0,
                ):
                    raw = meta.get_instance_types(region=region)
                # Limit by region-supported families when known
                region_fams: set[str] | None = None
                try:
                    if region:
                        region_fams = {
                            f.lower() for f in (self._region_gpu_families(flow, region) or [])
                        }
                        if not region_fams:
                            region_fams = None
                except Exception:
                    region_fams = None
                # Build helper maps for sorting and display
                id_to_gpu_count: dict[str, int] = {}
                try:
                    for it in raw or []:
                        fid = (
                            getattr(it, "fid", None)
                            or (it.get("fid") if isinstance(it, dict) else None)
                            or getattr(it, "id", None)
                            or (it.get("id") if isinstance(it, dict) else None)
                        )
                        if not fid:
                            continue
                        gpus = (
                            getattr(it, "gpus", None)
                            if not isinstance(it, dict)
                            else it.get("gpus")
                        )
                        total = 0
                        if isinstance(gpus, list):
                            for g in gpus:
                                try:
                                    cnt = (
                                        getattr(g, "count", None)
                                        if not isinstance(g, dict)
                                        else g.get("count")
                                    )
                                    total += int(cnt or 0)
                                except Exception:
                                    continue
                        # Only set when provider reports a positive GPU count; otherwise
                        # leave absent so we can fall back to name-based parsing.
                        if total > 0:
                            id_to_gpu_count[str(fid)] = int(total)
                except Exception:
                    id_to_gpu_count = {}
                if gpu_family:
                    raw = _RS._filter_offers_by_family(raw, gpu_family)  # type: ignore[attr-defined]
                    if not raw:
                        # If unfiltered had items, prefer curated fallback instead of confusing empty list
                        if meta.get_instance_types(region=region):
                            raw = []
                # Optional mapping to recover display names
                items: list[SelectionItem[str]] = []
                seen_names: set[str] = set()

                # helper: derive GPU count from title if missing
                def _count_from_title(name: str) -> int:
                    try:
                        import re as _re

                        # patterns like '8xh100' or 'a100-80gb.sxm.8x'
                        m = _re.search(r"(\d+)\s*x", name.lower())
                        if m:
                            return max(1, int(m.group(1)))
                        # default 1 for single-GPU types
                        return 1
                    except Exception:
                        return 1

                for it in raw or []:
                    name = _RS._get_any_attr_or_key(it, "name", "display_name") or ""
                    fid = _RS._get_any_attr_or_key(it, "fid", "id", "instance_type") or name

                    # If name looks like an internal id, try mapping to a human label
                    if (not name or name.startswith("it_")) and fid:
                        mapped = self._map_fid_to_name(str(fid))
                        if mapped:
                            name = str(mapped)

                    if not (name and fid):
                        continue

                    # Enforce region family visibility when available
                    if region_fams is not None:
                        fam_tmp = infer_gpu_family_from_name(name)
                        if not fam_tmp and fid:
                            mapped2 = self._map_fid_to_name(str(fid))
                            if mapped2:
                                fam_tmp = infer_gpu_family_from_name(str(mapped2))
                        if fam_tmp and fam_tmp.lower() not in region_fams:
                            continue

                    if gpu_family:
                        # Determine family from current name; if ambiguous, consult mapped name
                        fam = infer_gpu_family_from_name(name)
                        if not fam:
                            mapped2 = self._map_fid_to_name(str(fid))
                            if mapped2:
                                fam2 = infer_gpu_family_from_name(str(mapped2))
                                if fam2 == gpu_family:
                                    # Use mapped display name if it clarifies the family
                                    name = str(mapped2)
                                    fam = fam2
                        # Exclude when family is known and does not match selection
                        if fam and fam != gpu_family:
                            continue
                        # Extra safety: explicitly exclude opposite family tokens present in name
                        opposite = (
                            "h100"
                            if gpu_family == "a100"
                            else "a100" if gpu_family == "h100" else None
                        )
                        if opposite and opposite in name.lower():
                            continue

                    key = name.strip().lower()
                    if key in seen_names:
                        continue
                    seen_names.add(key)
                    # Attach a compact subtitle for GPU count, e.g., "8×"
                    count = id_to_gpu_count.get(str(fid))
                    if not isinstance(count, int) or count <= 0:
                        count = _count_from_title(str(name))
                    try:
                        import os as _os

                        ascii_only = str(
                            _os.environ.get("FLOW_ASCII_ONLY", "0")
                        ).strip().lower() in {"1", "true", "yes", "on"}
                    except Exception:
                        ascii_only = False
                    times_char = "x" if ascii_only else "×"
                    subtitle = f"{int(count)}{times_char}"
                    
                    # Convert display name to a user-friendly spec that can be resolved
                    # e.g., "h100-80gb.sxm.8x" -> "8xh100"
                    friendly_spec = str(name)
                    if "h100" in friendly_spec.lower() and count == 8:
                        friendly_spec = "8xh100"
                    elif "h100" in friendly_spec.lower():
                        friendly_spec = f"{count}xh100" if count > 1 else "h100"
                    elif "a100" in friendly_spec.lower():
                        friendly_spec = f"{count}xa100" if count > 1 else "a100"
                    # For other types, try to use the display name as-is if it looks resolvable
                    # Otherwise fallback to FID (though this may cause issues)
                    elif not any(c in friendly_spec for c in ["x", "gpu", "."]):
                        friendly_spec = str(fid)  # Last resort: use FID
                    
                    items.append(
                        SelectionItem(
                            value=friendly_spec,  # Use friendly spec instead of FID
                            id=str(fid),
                            title=str(name),
                            subtitle=subtitle,
                            status=None,
                        )
                    )

                if items:
                    # Sort by GPU count ascending by default; set FLOW_RESERVE_SORT_DESC=1 to flip
                    try:
                        import os as _os

                        desc = _os.environ.get("FLOW_RESERVE_SORT_DESC", "").strip().lower() in {
                            "1",
                            "true",
                            "yes",
                            "desc",
                        }
                    except Exception:
                        desc = False

                    def _gpu_count(it: SelectionItem[str]) -> int:
                        try:
                            # subtitle like "8 GPUs" -> 8
                            s = (it.subtitle or "").split(" ")[0]
                            return int(s)
                        except Exception:
                            return 1

                    items.sort(key=lambda x: (_gpu_count(x), x.title.lower()), reverse=desc)
                    if len(items) > 20:
                        items = self._filter_types_by_availability(flow, region, items)
                    return self._select("Select instance type", items, default_index=0)
        except Exception:
            pass

        # Fallback: conservative curated options
        # Restrict curated defaults by region family support when known
        fams = None
        try:
            if region:
                fams = {f.lower() for f in (self._region_gpu_families(flow, region) or [])}
        except Exception:
            fams = None
        if gpu_family in {"h100", "a100"}:
            base = [gpu_family, f"2x{gpu_family}", f"4x{gpu_family}", f"8x{gpu_family}"]
        elif gpu_family:
            base = [gpu_family]
        else:
            base = ["h100", "8xh100", "a100", "4xa100"]
        if fams is not None:
            base = [b for b in base if (infer_gpu_family_from_name(b) or "").lower() in fams]
        defaults = base
        items = [
            SelectionItem(value=it, id=it, title=it, subtitle=None, status=None) for it in defaults
        ]
        return self._select("Select instance type", items, default_index=0)

    def _region_supports_family(self, flow, region: str, gpu_family: str) -> bool:
        try:
            meta = self._meta(flow)
            # Use centralized meta method when available
            if meta and hasattr(meta, "get_region_gpu_families"):
                fams = meta.get_region_gpu_families(region) or []
                return str(gpu_family).lower() in {f.lower() for f in fams}
            if not (meta and hasattr(meta, "get_instance_types")):
                return False
            raw = meta.get_instance_types(region=region)
            for it in raw or []:
                name = (
                    getattr(it, "name", None)
                    or (it.get("name") if isinstance(it, dict) else None)
                    or getattr(it, "fid", None)
                    or (it.get("fid") if isinstance(it, dict) else None)
                )
                fam = infer_gpu_family_from_name(str(name or "")) if name else None
                if fam and fam == gpu_family:
                    return True
            return False
        except Exception:
            return False

    def _choose_region(
        self, flow, *, gpu_family: str | None = None, force: bool = False
    ) -> str | None:
        # Default from config when available; else offer known valid regions
        try:
            cfg_region = getattr(flow.config, "region", None)
        except Exception:
            cfg_region = None
        # Prefer provider meta capabilities regions; fall back to provider capabilities; then constants
        regions: list[str] = self._valid_regions(flow)
        valid_regions: list[str] | None = None
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import VALID_REGIONS as _VR

            valid_regions = list(_VR)
        except Exception:
            valid_regions = None
        # Filter out obviously invalid regions (when meta fallback returned non-Mithril names)
        if valid_regions:
            filtered = [r for r in regions if r in valid_regions]
            if filtered:
                regions = filtered
        # Prefer family-appropriate region ordering
        if gpu_family == "h100":
            regions = sorted(
                regions,
                key=lambda r: (0 if r == "us-central1-a" else (1 if r == "us-central1-b" else 2)),
            )
        elif gpu_family == "a100":
            regions = sorted(
                regions,
                key=lambda r: (
                    0
                    if r == "us-central2-a"
                    else (1 if r in {"eu-central1-b", "eu-central1-a"} else 2)
                ),
            )
        # If not forcing selection, auto-pick a region that supports the chosen GPU family when possible
        if not force:
            if gpu_family:
                # Prefer configured region when it supports the family
                if cfg_region and self._region_supports_family(flow, cfg_region, gpu_family):
                    return cfg_region
                # Otherwise choose first preferred region that supports the family
                for r in regions:
                    if self._region_supports_family(flow, r, gpu_family):
                        return r
                # If none of the advertised regions support the family, retry with provider constants
                if valid_regions:
                    for r in valid_regions:
                        try:
                            if self._region_supports_family(flow, r, gpu_family):
                                return r
                        except Exception:
                            continue
                # If support checks failed (e.g., offline) choose a sensible family default
                family_defaults = {
                    "h100": ["us-central1-b"],
                    "a100": ["us-central2-a", "eu-central1-b", "eu-central1-a"],
                }
                for cand in family_defaults.get(gpu_family, []):
                    if cand in regions:
                        return cand
            # Fallback: configured region or first in preference order
            return cfg_region or regions[0]

        # Force selection: build list (prefer regions that support the chosen family)
        from flow.cli.ui.presentation.animated_progress import (
            AnimatedEllipsisProgress as _AEP_regions,
        )

        region_entries: list[tuple[str, list[str], bool]] = (
            []
        )  # (region, families, supports_selected)
        with _AEP_regions(
            self.console, "Preparing region options", start_immediately=True, pad_top=0
        ):
            for r in regions:
                families = self._region_gpu_families(flow, r)
                supports_selected = False
                if gpu_family:
                    try:
                        supports_selected = (
                            gpu_family in families
                        ) or self._region_supports_family(flow, r, gpu_family)
                    except Exception:
                        supports_selected = False
                region_entries.append((r, families, supports_selected))

        # If any region supports the selected family, filter to only supporting
        if gpu_family and any(s for (_, _, s) in region_entries):
            region_entries = [e for e in region_entries if e[2]]

        region_items: list[SelectionItem[str]] = []
        for r, families, _supports in region_entries:
            # Minimalism: when a family is already selected, omit badges entirely
            subtitle = (
                None if gpu_family else (self._format_family_badges(families) if families else None)
            )
            region_items.append(
                SelectionItem(value=r, id=r, title=r, subtitle=subtitle, status=None)
            )
        default_idx = 0
        if cfg_region:
            for idx, it in enumerate(region_items):
                if it.value == cfg_region:
                    default_idx = idx
                    break
        return self._select("Select region", region_items, default_index=default_idx)

    def _should_show_region(self, flow, gpu_family: str | None) -> bool:
        """Decide whether to show the region selector.

        Policy: show when we detect meaningful per-region price differences OR
        when we cannot confidently determine differences (e.g., missing provider
        capability or offline). This avoids confusing auto-selection.
        """
        try:
            if not gpu_family:
                return False
            # If offline or lacking capability, prefer explicit user choice
            if self._offline:
                return True
            meta = self._meta(flow)
            if not meta or not hasattr(meta, "get_region_price_samples"):
                return True
            # Use family as the spec; provider will resolve to an instance id
            price_map = meta.get_region_price_samples(gpu_family)
            if not price_map:
                return True
            prices = [float(v) for v in price_map.values() if isinstance(v, (int, float))]
            if len(prices) < 2:
                return True
            mn, mx = min(prices), max(prices)
            # Show region selector if prices vary by >= 5%
            return (mx - mn) / max(mx, 1e-6) >= 0.05
        except Exception:
            return True

    def _choose_duration(
        self,
        flow=None,
        *,
        instance_type: str | None = None,
        region: str | None = None,
        quantity: int = 1,
    ) -> int:
        """Choose duration with quick picks or free-form input.

        Supports formats like:
        - "90m", "2h", "1d", "1d2h30m"
        - decimals: "1.5h", "0.5d"
        - bare numbers interpreted as hours (e.g., "6")
        Returns integer hours (rounded up when minutes/decimals provided).
        """
        options = [3, 6, 8, 12, 24]
        items: list[SelectionItem[str]] = []

        # Best-effort availability-aware annotation and default selection
        default_index = 2  # 8h by default
        counts: dict[int, int] = {}
        try:
            if flow and instance_type and region:
                service = _RS(flow)
                # Add a small scheduling buffer to avoid near-now edge cases
                now_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(minutes=30))
                horizon_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(days=7))
                # Prefer longer durations first when picking default
                with AEP(
                    self.console,
                    "Scanning availability by duration",
                    start_immediately=True,
                    pad_top=0,
                ):
                    for d in [24, 12, 8, 6, 3]:
                        try:
                            raw = service.availability(
                                _RS.AvailabilityQuery(
                                    instance_type=str(instance_type),
                                    region=str(region),
                                    earliest_start_time=now_iso,
                                    latest_end_time=horizon_iso,
                                    quantity=int(max(1, quantity)),
                                    duration_hours=d,
                                    mode="slots",
                                )
                            )
                            slots = _RS.filter_slots(
                                _RS.normalize_slots(raw),
                                min_quantity=int(max(1, quantity)),
                                min_duration_hours=d,
                            )
                            counts[d] = len(slots)
                        except Exception:
                            counts[d] = 0

                def _idx_for(opt: int) -> int:
                    try:
                        return options.index(opt)
                    except ValueError:
                        return 2

                # Heuristic: choose longest with >= 3 windows, else longest with >= 1, else 8h
                for d in [24, 12, 8, 6, 3]:
                    if counts.get(d, 0) >= 3:
                        default_index = _idx_for(d)
                        break
                else:
                    for d in [24, 12, 8, 6, 3]:
                        if counts.get(d, 0) >= 1:
                            default_index = _idx_for(d)
                            break
        except Exception:
            counts = {}

        # If all preset options show zero windows, warn early with actionable guidance
        try:
            preset = [24, 12, 8, 6, 3]
            if counts and all(int(counts.get(d, 0)) == 0 for d in preset):
                self.console.print(
                    "[warning]All preset durations show 0 availability this week.[/warning]\n"
                    "Try: choose Other to expand the window, try a different region, or use spot/auto allocation (flow run --allocation auto)."
                )
                _RS.telemetry(
                    "reservations.duration.zero",
                    {
                        "instance_type": instance_type,
                        "region": region,
                        "qty": quantity,
                        "context": "wizard",
                    },
                )
        except Exception:
            pass

        # Build items with optional availability subtitle
        for h in options:
            subtitle = None
            try:
                if counts:
                    c = counts.get(h)
                    if c is not None:
                        subtitle = f"~{c} windows this week"
            except Exception:
                subtitle = None
            items.append(
                SelectionItem(
                    value=str(h), id=str(h), title=f"{h} hours", subtitle=subtitle, status=None
                )
            )
        items.append(
            SelectionItem(
                value="__other__",
                id="other",
                title="Other…",
                subtitle="Type a duration like 90m, 2h, 1d",
                status=None,
            )
        )

        sel = self._select("Select duration", items, default_index=default_index)

        # Quick pick path
        try:
            if sel and sel != "__other__":
                return int(sel)
        except Exception:
            pass

        # Free-form input path
        hint = (
            "Enter duration (examples: 90m, 2h, 1d, 1d2h30m; bare number = hours).\n"
            "We round up to whole hours for reservation windows."
        )
        try:
            import click as _click

            self.console.print(f"[muted]{hint}[/muted]")
            raw = _click.prompt("Duration", default="8h", show_default=True)
        except Exception:
            raw = "8h"

        return _RS.parse_duration_to_hours(raw, default_hours=8)

    def _choose_quantity(self) -> int:
        options = [1, 2, 4, 8]
        items = [
            SelectionItem(value=str(q), id=str(q), title=str(q), subtitle=None, status=None)
            for q in options
        ]
        sel = self._select("Select quantity", items, default_index=0)
        try:
            return int(sel) if sel else 1
        except Exception:
            return 1

    def run(self, flow) -> None:
        # Build state
        st = WizardState()
        # If we are offline, inform the user and exit early to avoid confusing heuristics
        self._offline = not self._is_network_reachable()
        if self._offline:
            try:
                self.console.print(
                    "[error]Network appears unavailable. Unable to reach provider API.[/error]\n"
                    "Connect to the internet and retry, or set FLOW_RESERVE_ALLOW_OFFLINE=1 to proceed with best-effort lists (not recommended)."
                )
            except Exception:
                pass
            return
        st.project = self._choose_project(flow)
        if st.project:
            try:
                # Persist chosen project into provider config for this session
                cfg = getattr(flow, "config", None)
                if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                    cfg.provider_config["project"] = st.project
            except Exception:
                pass
            # Resolve and inject the project into the provider context immediately
            try:
                provider = getattr(flow, "provider", None)
                resolver = getattr(provider, "project_resolver", None)
                if resolver and callable(getattr(resolver, "resolve", None)):
                    pid = resolver.resolve(st.project)  # name -> id
                    # Update provider context so subsequent calls have a project
                    try:
                        # Cache the resolved project id
                        if hasattr(provider, "ctx"):
                            setattr(provider.ctx, "_project_id", pid)
                            if getattr(provider.ctx, "mithril_config", None):
                                provider.ctx.mithril_config.project = pid
                    except Exception:
                        pass
            except Exception:
                pass
        # GPU family first
        gpu_family = self._choose_gpu_type(flow)
        # Region: only show selection when price differences are detectable
        try:
            from flow.cli.ui.presentation.animated_progress import (
                AnimatedEllipsisProgress as _AEP_region,
            )

            with _AEP_region(
                self.console, "Checking region pricing", start_immediately=True, pad_top=0
            ):
                show_region = self._should_show_region(flow, gpu_family)
        except Exception:
            show_region = self._should_show_region(flow, gpu_family)
        st.region = self._choose_region(flow, gpu_family=gpu_family, force=show_region)
        if not show_region and st.region:
            try:
                from flow.utils.links import docs

                url = docs.instance_types_and_specs()
                # Print compact hyperlink label instead of full URL
                self.console.print(
                    f"Region auto-selected: [accent]{st.region}[/accent]. [link={url}]Learn more[/link]"
                )
            except Exception:
                pass
        st.instance_type = self._choose_instance_type(flow, st.region, gpu_family)
        # Quantity first improves availability-aware duration defaulting
        st.quantity = self._choose_quantity()
        st.duration_hours = self._choose_duration(
            flow,
            instance_type=st.instance_type,
            region=st.region,
            quantity=st.quantity,
        )

        if not st.instance_type or not st.region:
            self.console.print(
                "[error]Missing required selections (instance type or region).[/error]"
            )
            return

        # Availability query
        service = _RS(flow)
        # Add a small scheduling buffer to avoid near-now edge cases
        now_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(minutes=30))
        horizon_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(days=7))
        with AEP(self.console, "Finding reservation windows", start_immediately=True, pad_top=0):
            slots_raw = service.availability(
                _RS.AvailabilityQuery(
                    instance_type=str(st.instance_type),
                    region=str(st.region),
                    earliest_start_time=now_iso,
                    latest_end_time=horizon_iso,
                    quantity=st.quantity,
                    duration_hours=st.duration_hours,
                    mode="slots",
                )
            )
        slots = _RS.filter_slots(
            _RS.normalize_slots(slots_raw),
            min_quantity=st.quantity,
            min_duration_hours=st.duration_hours,
        )
        
        # Adjust slot end times to reflect actual reservation duration
        # This prevents confusion where availability windows show 168h when user selected 3h
        if slots and st.duration_hours:
            adjusted_slots = []
            for slot in slots:
                adjusted_slot = dict(slot)
                start_time = _RS._to_dt(slot.get("start_time_utc"))
                if start_time:
                    # Set end time to start + requested duration (not the full availability window)
                    adjusted_end = start_time + _td(hours=st.duration_hours)
                    adjusted_slot["end_time_utc"] = _RS.isoformat_utc_z(adjusted_end)
                adjusted_slots.append(adjusted_slot)
            slots = adjusted_slots

        if not slots:
            self.console.print(
                "[warning]No self-serve availability found in the next 7 days.[/warning]"
            )
            try:
                self.console.print(
                    "Try one or more: \n"
                    " - Expand the time window or choose a shorter duration\n"
                    " - Try another region (e.g., us-central1-b)\n"
                    " - Use spot/auto allocation (flow run --allocation auto)\n"
                    " - Reach out to the Flow team to schedule capacity or discuss options"
                )
            except Exception:
                pass
            try:
                _RS.telemetry(
                    "reservations.availability.zero",
                    {
                        "instance_type": st.instance_type,
                        "region": st.region,
                        "qty": st.quantity,
                        "duration_hours": st.duration_hours,
                        "context": "wizard",
                    },
                )
            except Exception:
                pass
            return

        recommended = slots[0]
        self.console.print("Recommended slot:")
        try:
            ReservationsRenderer(self.console).render_availability_table(
                [recommended], local_time=True, show_price=True, title=None
            )
        except Exception:
            pass

        # Confirm or browse more
        try:
            import click as _click

            if not _click.confirm("Reserve this slot?", default=True):
                try:
                    from flow.cli.ui.presentation.reservations_view import (
                        choose_availability_slot as _choose_slot,
                    )
                    from flow.cli.ui.presentation.reservations_view import (
                        render_availability as _render_avail,
                    )

                    # Offer interactive browsing of all slots
                    if _click.confirm("Browse other slots?", default=True):
                        # Show compact table + grid first for orientation
                        try:
                            _render_avail(
                                self.console,
                                slots,
                                local_time=True,
                                show_price=True,
                                title="Availability",
                                grid=True,
                            )
                        except Exception:
                            pass
                        chosen = _choose_slot(
                            slots, region=str(st.region), instance_type=str(st.instance_type)
                        )
                        if not chosen:
                            self.console.print("No slot selected. Reservation not created.")
                            return
                        recommended = chosen
                    else:
                        self.console.print("Reservation not created.")
                        return
                except Exception:
                    self.console.print("Reservation not created.")
                    return
        except Exception:
            return

        # Create reservation
        start_iso = _RS.isoformat_utc_z(recommended.get("start_time_utc"))
        task = service.create_reservation(
            instance_type=str(st.instance_type),
            region=str(st.region),
            quantity=int(st.quantity),
            start_time_iso_z=start_iso,
            duration_hours=int(st.duration_hours),
            name=f"reservation-{st.instance_type}",
            ssh_keys=[],
            env=None,
        )
        rid = (
            task.provider_metadata.get("reservation", {}).get("reservation_id")
            if getattr(task, "provider_metadata", None)
            else None
        )
        self.console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
