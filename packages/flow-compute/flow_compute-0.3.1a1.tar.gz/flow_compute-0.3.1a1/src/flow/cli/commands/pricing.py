"""Pricing visibility command.

Summary-first views for:
- Defaults/overrides: per-GPU tiers and per-instance limit prices
- Market: regional quantiles (P50/P90/P95) and recommended limit prices

Details are opt-in via flags; default output stays concise and actionable.
"""

from typing import Any

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.presentation.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.telemetry import Telemetry
from flow.cli.utils.theme_manager import theme_manager
from flow.domain.pricing import calculator as pricing_core
from flow.domain.pricing.insights import (
    aggregate_market,
    derive_recommendations,
)
from flow.utils.links import DocsLinks, WebLinks


class PricingCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "pricing"

    @property
    def help(self) -> str:
        return "Show market prices and recommendations"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option(
            "--market",
            is_flag=True,
            help="(No-op) Market summary is shown by default",
        )
        @click.option("--region", help="Filter market by region (e.g., us-central1-b)")
        @click.option("--gpu", help="Filter to a GPU (e.g., h100, a100)")
        @click.option("--gpus", type=int, help="Target GPU count for per-instance limit prices")
        @click.option(
            "--list", "show_list", is_flag=True, help="List raw market instances (verbose)"
        )
        @click.option("--explain", is_flag=True, help="Explain recommendations (verbose)")
        @click.option("--json", "as_json", is_flag=True, help="Output JSON for automation")
        @cli_error_guard(self)
        def pricing(
            market: bool = False,
            region: str | None = None,
            gpu: str | None = None,
            gpus: int | None = None,
            show_list: bool = False,
            explain: bool = False,
            as_json: bool = False,
        ):
            """Display market summary (default)."""
            # Header
            try:
                accent = theme_manager.get_color("accent")
                console.print(f"[bold {accent}]Flow Pricing[/bold {accent}]")
            except Exception:
                pass

            # Telemetry (best-effort)
            try:
                Telemetry().log_event(
                    "pricing_view_shown",
                    {
                        "view": "market" if market else "defaults",
                        "gpu": (gpu or ""),
                        "gpus": (gpus or 0),
                        "region": (region or ""),
                    },
                )
            except Exception:
                pass

            # ---- Market summary view (default) ----
            if True:
                # Helpers: render separate panels for stats vs limit prices
                def _render_stats_panel(rows: list[dict[str, Any]]) -> None:
                    stats_table = create_flow_table(
                        title=None, show_borders=True, padding=1, expand=True
                    )
                    stats_table.add_column(
                        "GPU", style=theme_manager.get_color("accent"), no_wrap=True
                    )
                    stats_table.add_column("Region", no_wrap=True)
                    stats_table.add_column("Current", justify="right")

                    for r in rows:
                        stats_table.add_row(
                            r.get("gpu", ""),
                            r.get("region", ""),
                            r.get("current_fmt", "-"),
                        )

                    title_suffix = f" • {region}" if region else ""
                    wrap_table_in_panel(stats_table, f"Market Stats{title_suffix}", console)

                def _render_caps_panel(rows: list[dict[str, Any]], *, counts: list[int]) -> None:
                    caps_table = create_flow_table(
                        title=None, show_borders=True, padding=1, expand=True
                    )
                    caps_table.add_column(
                        "GPU", style=theme_manager.get_color("accent"), no_wrap=True
                    )
                    caps_table.add_column("Region", no_wrap=True)

                    # Add 1x/4x/8x (or single Limit Price when a specific count is requested)
                    if len(counts) == 1:
                        caps_table.add_column("Limit Price", justify="right", no_wrap=True)
                    else:
                        for c in counts:
                            caps_table.add_column(f"{c}x", justify="right", no_wrap=True)

                    for r in rows:
                        cap_cells: list[str] = [r.get("gpu", ""), r.get("region", "")]
                        cap_med = r.get("cap_med")
                        avail_counts = set(r.get("avail_counts", []) or [])
                        if isinstance(cap_med, (int, float)):
                            from flow.domain.pricing.insights import per_instance_caps as _caps

                            caps_map = _caps(float(cap_med), counts)
                            if len(counts) == 1:
                                v = caps_map.get(counts[0])
                                cap_cells.append(
                                    f"${v:.2f}"
                                    if (
                                        isinstance(v, (int, float))
                                        and ((not avail_counts) or (counts[0] in avail_counts))
                                    )
                                    else "-"
                                )
                            else:
                                for c in counts:
                                    v = caps_map.get(c)
                                    cap_cells.append(
                                        f"${v:.2f}"
                                        if (
                                            isinstance(v, (int, float))
                                            and ((not avail_counts) or (c in avail_counts))
                                        )
                                        else "-"
                                    )
                        else:
                            cap_cells.extend(["-"] * (1 if len(counts) == 1 else len(counts)))

                        caps_table.add_row(*cap_cells)

                    title_suffix = f" • {region}" if region else ""
                    wrap_table_in_panel(
                        caps_table,
                        f"Likely Billing Price Estimate{title_suffix}",
                        console,
                    )

                # Try authenticated path first (if project is configured)
                def _try_authenticated() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
                    from flow.sdk.factory import create_client

                    client = create_client(auto_init=True)
                    req: dict[str, Any] = {}
                    if region:
                        req["region"] = region
                    instances = client.find_instances(req, limit=250)
                    raw_rows: list[dict[str, Any]] = []
                    for inst in instances:
                        raw_rows.append(
                            {
                                "region": inst.region,
                                "gpu_type": (inst.gpu_type or "")
                                or pricing_core._infer_gpu_type(inst.instance_type),
                                "gpu_count": inst.gpu_count,
                                "price_per_hour": inst.price_per_hour,
                                "instance_type": inst.instance_type,
                                "available_quantity": inst.available_quantity,
                            }
                        )
                    return raw_rows, raw_rows

                def _try_public() -> list[dict[str, Any]]:
                    """Fetch market data via public endpoints using stdlib HTTP.

                    Avoids internal exception mapping so users see clearer reasons on failure.
                    """
                    import json as _json
                    import os as _os
                    import ssl as _ssl
                    from urllib import request as _urlreq
                    from urllib.parse import urlencode as _urlencode
                    from urllib.parse import urljoin as _urljoin

                    from flow.domain.services.pricing import PriceParser as _PriceParser

                    api_base = (
                        _os.getenv("MITHRIL_API_URL", "https://api.mithril.ai").rstrip("/") + "/"
                    )
                    api_key = _os.getenv("MITHRIL_API_KEY")
                    project = _os.getenv("MITHRIL_PROJECT_ID") or _os.getenv("MITHRIL_PROJECT")

                    # If env not set, try loading from Config (non-interactive)
                    if not api_key or not project:
                        try:
                            from flow.application.config.config import Config as _Cfg

                            _cfg = _Cfg.from_env(require_auth=False)
                            if not api_key:
                                api_key = _cfg.auth_token or api_key
                            if not project:
                                project = (_cfg.provider_config or {}).get("project") or project
                            # Respect configured API URL if provided
                            api_base = (
                                (_cfg.provider_config or {}).get("api_url") or api_base
                            ).rstrip("/") + "/"
                        except Exception:
                            pass

                    def _get_json(path: str, params: dict[str, Any] | None = None) -> Any:
                        qs = f"?{_urlencode(params)}" if params else ""
                        url = _urljoin(api_base, path.lstrip("/")) + qs
                        headers = {"Accept": "application/json"}
                        if api_key:
                            headers["Authorization"] = f"Bearer {api_key}"
                        req = _urlreq.Request(url, headers=headers, method="GET")
                        ctx = _ssl.create_default_context()
                        with _urlreq.urlopen(req, context=ctx, timeout=15) as resp:
                            data = resp.read()
                            return _json.loads(data.decode("utf-8"))

                    # Build mapping from instance_type id -> (display_name, gpu_count, gpu_type)
                    id_to_name: dict[str, str] = {}
                    id_to_gpus: dict[str, int] = {}
                    id_to_gpu_type: dict[str, str] = {}
                    try:
                        itypes = _get_json("/v2/instance-types")
                        if isinstance(itypes, list):
                            for it in itypes:
                                try:
                                    fid = it.get("fid") or it.get("id")
                                    name = it.get("name") or fid
                                    gpus = 0
                                    gpu_type = ""
                                    for g in it.get("gpus", []) or []:
                                        try:
                                            gpus += int(g.get("count", 0) or 0)
                                            if not gpu_type:
                                                nm = str(g.get("name") or "").lower()
                                                if "h100" in nm:
                                                    gpu_type = "h100"
                                                elif "a100" in nm:
                                                    gpu_type = "a100"
                                        except Exception:
                                            continue
                                    if fid:
                                        id_to_name[str(fid)] = str(name)
                                        id_to_gpus[str(fid)] = gpus if gpus > 0 else 0
                                        id_to_gpu_type[str(fid)] = (
                                            gpu_type or pricing_core._infer_gpu_type(name)
                                        )
                                except Exception:
                                    continue
                    except Exception:
                        # Non-fatal; still attempt availability
                        pass

                    params = {"limit": 100}
                    if region:
                        params["region"] = region
                    if project:
                        # Not all deployments require this; safe to include if present
                        params["project"] = project
                    avail = _get_json("/v2/spot/availability", params=params)
                    if not isinstance(avail, list):
                        avail = []

                    parser = _PriceParser()
                    rows: list[dict[str, Any]] = []
                    # Helper to parse GPU count from instance_type string (e.g., "h100-80gb.sxm.8x")
                    import re as _re

                    def _parse_gpus_from_name(name: str) -> int:
                        try:
                            m = _re.search(r"(\d+)x\b", str(name))
                            if m:
                                val = int(m.group(1))
                                return val if val > 0 else 0
                        except Exception:
                            pass
                        return 0

                    for a in avail:
                        try:
                            rgn = str(a.get("region", "") or "")
                            it_id = str(
                                a.get("instance_type")
                                or a.get("instanceType")
                                or a.get("instanceTypeId")
                                or ""
                            )
                            # Parse various price fields
                            price_str = (
                                a.get("last_instance_price")
                                or a.get("current_price")
                                or a.get("price_per_hour")
                                or a.get("price")
                                or None
                            )
                            price = 0.0
                            if isinstance(price_str, (int, float)):
                                price = float(price_str)
                            elif isinstance(price_str, str):
                                try:
                                    price = float(parser.parse(price_str))
                                except Exception:
                                    price = 0.0

                            # GPU count resolution
                            gpus = int(
                                a.get("gpu_count")
                                or a.get("gpus")
                                or id_to_gpus.get(it_id, 0)
                                or _parse_gpus_from_name(id_to_name.get(it_id, ""))
                                or _parse_gpus_from_name(it_id)
                                or 0
                            )
                            # Availability amount (best-effort)
                            avail_count = None
                            for key in (
                                "available_quantity",
                                "available_count",
                                "capacity",
                                "quantity",
                            ):
                                v = a.get(key)
                                if isinstance(v, (int, float)):
                                    avail_count = int(v)
                                    break

                            # Convert to per-GPU price if we know GPU count
                            per_gpu_price = (price / gpus) if (gpus and price) else 0.0

                            rows.append(
                                {
                                    "region": rgn,
                                    "gpu_type": id_to_gpu_type.get(
                                        it_id, pricing_core._infer_gpu_type(it_id)
                                    ),
                                    "gpu_count": gpus or None,
                                    "price_per_hour": per_gpu_price or price,
                                    "instance_type": id_to_name.get(it_id, it_id),
                                    "available_quantity": avail_count,
                                }
                            )
                        except Exception:
                            continue

                    return rows

                raw_rows: list[dict[str, Any]] = []
                offline_note: str | None = None
                try:
                    raw_rows, _ = _try_authenticated()
                except Exception:
                    try:
                        raw_rows = _try_public()
                    except Exception:  # pragma: no cover - network specific
                        # Offline or public API not reachable — do NOT show defaults.
                        # Keep offline output minimal; avoid noisy error reasons.
                        offline_note = None

                # If we have no live data, surface a clear message and exit early
                if not raw_rows:
                    # Minimal offline output: just point to live price charts.
                    console.print(f"See live price charts: {WebLinks.price_chart()}\n")
                    return

                # Optional raw list view
                if show_list:
                    table = create_flow_table(
                        title=None, show_borders=True, padding=1, expand=False
                    )
                    table.add_column(
                        "Region", style=theme_manager.get_color("accent"), no_wrap=True
                    )
                    table.add_column("GPU", no_wrap=True)
                    table.add_column("GPUs", justify="right")
                    table.add_column("Price/GPU", justify="right")
                    table.add_column("Price/inst", justify="right")
                    table.add_column("Avail", justify="right")

                    raw_rows.sort(
                        key=lambda x: (x.get("region", ""), float(x.get("price_per_hour") or 0))
                    )
                    for r in raw_rows:
                        # Here price_per_hour is per-GPU (normalized above)
                        p = float(r.get("price_per_hour") or 0)
                        g = r.get("gpu_count") or 0
                        per_inst = (p * g) if (p and g) else 0.0
                        table.add_row(
                            r.get("region", ""),
                            r.get("gpu_type", ""),
                            str(g or "-"),
                            f"${p:.2f}/hr" if p else "-",
                            f"${per_inst:.2f}/hr" if per_inst else "-",
                            str(r.get("available_quantity") or "-"),
                        )
                    wrap_table_in_panel(
                        table, f"Listings{' • ' + region if region else ''}", console
                    )
                    return

                # Aggregate into quantiles and recommendations (for estimates), and compute current prices
                # Build availability size map: (gpu, region) -> set of GPU counts present
                from collections import defaultdict as _dd

                avail_size_map: dict[tuple[str, str], set[int]] = _dd(set)
                try:
                    for r in raw_rows:
                        gk = str(r.get("gpu_type") or "").lower().strip()
                        rgn = str(r.get("region") or "").strip()
                        gc = r.get("gpu_count")
                        if gk and rgn and isinstance(gc, (int, float)) and int(gc) > 0:
                            avail_size_map[(gk, rgn)].add(int(gc))
                except Exception:
                    avail_size_map = _dd(set)

                market = aggregate_market(raw_rows, target_gpu=None)
                recs = derive_recommendations(market)

                # Compute current (snapshot) lowest per‑GPU price per region
                from collections import defaultdict as _dd2

                current_map: dict[tuple[str, str], dict[str, float | int]] = _dd2(dict)
                try:
                    for r in raw_rows:
                        gk = str(r.get("gpu_type") or "").lower().strip()
                        rgn = str(r.get("region") or "").strip()
                        p = float(r.get("price_per_hour") or 0)
                        if not gk or not rgn or p <= 0:
                            continue
                        entry = current_map.get((gk, rgn))
                        if not entry:
                            current_map[(gk, rgn)] = {"price": p, "n": 1}
                        else:
                            entry["price"] = min(float(entry.get("price") or p), p)
                            entry["n"] = int(entry.get("n") or 0) + 1
                except Exception:
                    current_map = {}

                # GPUs to show: requested, else H100 + A100 if available, else first two
                gpu_req = (gpu or "").lower().strip()
                if gpu_req:
                    gpu_keys = [gpu_req]
                else:
                    preferred = [g for g in ("h100", "a100") if g in market]
                    gpu_keys = preferred if preferred else sorted(market.keys())[:2]

                # Build rows across selected GPUs using current lowest price per region
                rows: list[dict[str, Any]] = []
                for gpu_key in gpu_keys:
                    # Filter current_map keys for this GPU (and region filter if provided)
                    items: list[tuple[str, float]] = []
                    for (gk, rgn), data in current_map.items():
                        if gk != gpu_key:
                            continue
                        if region and rgn != region:
                            continue
                        price_val = float(data.get("price") or 0)
                        if price_val > 0:
                            items.append((rgn, price_val))
                    # Sort by current price asc and take top 3
                    items.sort(key=lambda t: t[1])
                    for rgn, price_val in items[:3]:
                        r_per_gpu = recs.get(gpu_key, {}).get(rgn, {})
                        # Keep estimate logic for caps (med heuristic)
                        per_gpu_cap = r_per_gpu.get("med")
                        rows.append(
                            {
                                "gpu": gpu_key,
                                "region": rgn,
                                "current_fmt": f"${price_val:.2f}",
                                "cap_med": (
                                    per_gpu_cap if isinstance(per_gpu_cap, (int, float)) else None
                                ),
                                "avail_counts": sorted(
                                    list(avail_size_map.get((gpu_key, rgn), set()))
                                ),
                            }
                        )

                # JSON output for automation / debugging (includes raw listings)
                if as_json:
                    try:
                        import json as _json

                        payload = {
                            "context": {
                                "region_filter": region,
                                "gpu_filter": gpu,
                                "target_gpus": gpus,
                            },
                            "raw_listings": raw_rows,
                            "market": market,
                            "recommendations": recs,
                            "top_rows": rows,
                        }
                        click.echo(_json.dumps(payload, indent=2))
                        return
                    except Exception:
                        # Fall through to normal rendering if JSON serialization fails
                        pass

                target_counts = [gpus] if gpus and gpus > 0 else [1, 4, 8]
                _render_stats_panel(rows)
                try:
                    console.print(
                        "[dim]Per‑GPU USD/hr. Current = lowest listing price per region (snapshot).[/dim]"
                    )
                except Exception:
                    pass
                # Add a blank line between sections for readability
                try:
                    console.print("")
                except Exception:
                    pass
                _render_caps_panel(rows, counts=target_counts)
                try:
                    console.print(
                        "[dim]Estimate reflects prediction based on history; prices vary with load. '-' means size not seen in availability.[/dim]"
                    )
                    console.print(
                        "[dim]Set your limit price above this estimate to reflect your threshold price; you pay the clearing price (second‑price auction), not your limit price.[/dim]"
                    )
                    # Space before docs block
                    console.print("")
                    console.print("[dim]Docs:[/dim]")
                    console.print(
                        f"[dim]- Threshold price vs billing price: {DocsLinks.spot_bids()}[/dim]"
                    )
                    console.print(
                        f"[dim]- Auction mechanics: {DocsLinks.spot_auction_mechanics()}[/dim]"
                    )
                    # Space after docs block
                    console.print("")
                except Exception:
                    pass

                # Surface Flow's default balanced/high limit prices concisely so users see safer options
                # without overwhelming the main view. These come from packaged pricing.json.
                try:
                    from flow.resources import get_gpu_pricing as _get_pricing

                    _base = _get_pricing() or {}
                    med_parts: list[str] = []
                    high_parts: list[str] = []
                    for gk in gpu_keys:
                        tiers = _base.get(gk) or _base.get("default") or {}
                        m = tiers.get("med")
                        h = tiers.get("high")
                        if isinstance(m, (int, float)):
                            med_parts.append(f"{gk} ${float(m):.2f}")
                        if isinstance(h, (int, float)):
                            high_parts.append(f"{gk} ${float(h):.2f}")
                    if med_parts or high_parts:
                        console.print("")
                    if med_parts:
                        console.print(
                            "[dim]Med limit price recommendations (per‑GPU): "
                            + ", ".join(med_parts)
                            + "[/dim]"
                        )
                    if high_parts:
                        console.print(
                            "[dim]High limit price recommendations (per‑GPU): "
                            + ", ".join(high_parts)
                            + "  (fewer preemptions)[/dim]"
                        )
                        console.print("[dim]Select priority when running: -p med or -p high[/dim]")
                except Exception:
                    pass
                if offline_note:
                    console.print(f"[dim]{offline_note}[/dim]")
                    try:
                        reason_lower = offline_note.lower()
                        if "project" in reason_lower and "required" in reason_lower:
                            console.print(
                                "[dim]Hint: Configure your project via 'flow init' or set MITHRIL_PROJECT_ID.[/dim]"
                            )
                        if (
                            ("401" in reason_lower)
                            or ("unauthorized" in reason_lower)
                            or ("403" in reason_lower)
                            or ("forbidden" in reason_lower)
                        ):
                            console.print(
                                "[dim]Hint: Set MITHRIL_API_KEY or run 'flow init' to authenticate. For curl: -H \"Authorization: Bearer $MITHRIL_API_KEY\"[/dim]"
                            )
                    except Exception:
                        pass
                try:
                    Telemetry().log_event(
                        "pricing_recommendation_shown",
                        {
                            "gpu": ",".join(gpu_keys),
                            "rows": len(rows),
                            "region_filter": bool(region),
                            "gpus": gpus or 0,
                        },
                    )
                except Exception:
                    pass

                # Optional explanation of heuristics
                if explain:
                    console.print(
                        "[dim]Heuristics: Low=P50×1.15  Med=P90×1.10  High=P95×1.25 (rounded). Confidence rises with sample size.[/dim]\n"
                    )

                # Space before end note
                console.print("")
                console.print(f"See live price charts: {WebLinks.price_chart()}\n")
                return

        return pricing


# Export command instance
command = PricingCommand()
