from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter
from flow.cli.utils.theme_manager import theme_manager


def _to_utc(dt: datetime | str | None) -> datetime | None:
    """Parse various timestamp inputs and return a timezone-aware UTC datetime.

    Accepts ISO8601 strings (with optional 'Z') or datetime objects.
    Returns None on failure.
    """
    if dt is None:
        return None
    try:
        if isinstance(dt, datetime):
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        s = str(dt).replace("Z", "+00:00")
        return datetime.fromisoformat(s).astimezone(timezone.utc)
    except Exception:
        return None


def _format_countdown(start_utc: datetime | None) -> str:
    """Return compact countdown until start: e.g., '45m', '3h', '-' when unknown or past."""
    if not start_utc:
        return "-"
    try:
        now = datetime.now(timezone.utc)
        delta = (start_utc - now).total_seconds()
        if delta <= 0:
            return "0m"
        minutes = int(delta // 60)
        if minutes < 120:
            return f"{minutes}m"
        return f"{minutes // 60}h"
    except Exception:
        return "-"


def _format_window(start_utc: datetime | None, end_utc: datetime | None) -> str:
    """Return window size like '6h'."""
    if not start_utc or not end_utc:
        return "-"
    try:
        hours = int(round((end_utc - start_utc).total_seconds() / 3600))
        return f"{hours}h"
    except Exception:
        return "-"


def _format_dt(dt: datetime | None, *, local_time: bool = False) -> str:
    if not dt:
        return "-"
    try:
        if local_time:
            return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(dt)


@dataclass
class AvailabilitySlot:
    start_time_utc: datetime
    end_time_utc: datetime
    quantity: int
    region: str | None = None
    instance_type: str | None = None

    @property
    def duration_hours(self) -> int:
        return max(0, int(round((self.end_time_utc - self.start_time_utc).total_seconds() / 3600)))


class ReservationsRenderer:
    """Renders reservations data in tables and panels."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or theme_manager.create_console()
        self.term = TerminalAdapter()

    # -------- Availability --------
    def render_availability_table(
        self,
        slots: Iterable[AvailabilitySlot | dict[str, Any]],
        *,
        columns: Sequence[str] | None = None,
        local_time: bool = False,
        grid: bool = False,
        show_price: bool = False,
        price_priority: str = "med",
        title: str | None = None,
        return_renderable: bool = False,
    ):
        """Render an availability table.

        Default columns: StartUTC, EndUTC, Duration, Qty, Region, Type, StartIn
        """
        col_order = (
            list(columns)
            if columns
            else [
                "StartUTC",
                "EndUTC",
                "Duration",
                "Qty",
                "Region",
                "Type",
                "StartIn",
            ]
        )

        table = Table(
            box=None,
            show_header=True,
            header_style=theme_manager.get_color("table.header"),
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=False,
        )
        for name in col_order:
            justify = "right" if name in {"Qty", "Duration", "StartIn"} else "left"
            width = 8 if name in {"Qty", "Duration", "StartIn"} else None
            table.add_column(
                name, justify=justify, width=width, no_wrap=name in {"Qty", "Duration", "StartIn"}
            )

        # Normalize input and accumulate for optional grid rendering
        normalized: list[dict[str, Any]] = []
        any_rows = False
        # Optional pricing support
        if show_price:
            try:
                from flow.domain.pricing import calculator as pricing_core

                pricing_table = pricing_core.get_pricing_table()

                def _price_for(it_name: str | None) -> float:
                    try:
                        return float(
                            pricing_core.calculate_instance_price(
                                it_name or "", priority=price_priority, pricing_table=pricing_table
                            )
                        )
                    except Exception:
                        return 0.0

            except Exception:
                show_price = False  # disable silently if pricing core unavailable
                pricing_table = None  # type: ignore[assignment]

                def _price_for(_it: str | None) -> float:
                    return 0.0

        else:

            def _price_for(_it: str | None) -> float:  # type: ignore[no-redef]
                return 0.0

        for s in slots:
            if isinstance(s, dict):
                st = _to_utc(s.get("start_time_utc") or s.get("start_time") or s.get("start"))
                et = _to_utc(s.get("end_time_utc") or s.get("end_time") or s.get("end"))
                qty = int(s.get("quantity", 0) or 0)
                reg = s.get("region")
                it = s.get("instance_type")
            else:
                st = _to_utc(s.start_time_utc)
                et = _to_utc(s.end_time_utc)
                qty = int(getattr(s, "quantity", 0) or 0)
                reg = getattr(s, "region", None)
                it = getattr(s, "instance_type", None)

            duration = _format_window(st, et)
            start_in = _format_countdown(st)
            # Numeric hours for pricing
            hours_num = 0
            try:
                if st and et:
                    hours_num = max(0, int(round((et - st).total_seconds() / 3600)))
            except Exception:
                hours_num = 0

            row_map: dict[str, str] = {
                "StartUTC": _format_dt(st, local_time=local_time),
                "EndUTC": _format_dt(et, local_time=local_time),
                "Duration": duration,
                "Qty": str(qty),
                "Region": str(reg or "-"),
                "Type": str(it or "-"),
                "StartIn": start_in,
            }
            if show_price:
                try:
                    per_inst = _price_for(str(it or ""))
                    est_total = per_inst * max(1, qty) * max(1, hours_num)
                    row_map["EstUSD"] = f"${est_total:,.2f}"
                except Exception:
                    row_map["EstUSD"] = "-"
            table.add_row(*[row_map.get(c, "-") for c in col_order])
            any_rows = True
            normalized.append(
                {
                    "start": st,
                    "end": et,
                    "qty": qty,
                    "region": reg,
                    "type": it,
                }
            )

        if not any_rows:
            msg = "No self-serve availability found. Reach out to the Flow team for assistance."
            empty = Panel(msg, border_style=theme_manager.get_color("muted"))
            return (
                empty
                if return_renderable
                else self.console.print(
                    "[dim]No self-serve availability found. Reach out to the Flow team for assistance.[/dim]"
                )
            )

        # Optional inline grid/timeline view (minimal, ASCII-based)
        if grid and normalized:
            try:
                # Group by date (start day) and render hour blocks with quantity bands
                from collections import defaultdict

                days: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for n in normalized:
                    st = n.get("start")
                    if isinstance(st, datetime):
                        key = st.astimezone(timezone.utc).strftime("%Y-%m-%d")
                    else:
                        key = "unknown"
                    days[key].append(n)

                blocks: list[Any] = [table, Rule(style=theme_manager.get_color("table.border"))]
                for day, items in sorted(days.items()):
                    # Build a 24-char line, each char an hour; fill with 0/+/# based on qty thresholds
                    line = [" "] * 24
                    for n in items:
                        st = n.get("start")
                        et = n.get("end")
                        q = int(n.get("qty") or 0)
                        if not isinstance(st, datetime) or not isinstance(et, datetime):
                            continue
                        st_h = st.hour
                        et_h = max(st_h, min(23, et.hour))
                        for h in range(st_h, et_h + 1):
                            line[h] = "#" if q >= 8 else "+" if q >= 2 else "·"
                    label = Text(f"{day} ", style=theme_manager.get_color("accent"))
                    grid_line = Text("".join(line), style=theme_manager.get_color("default"))
                    blocks.append(Text.assemble(label, grid_line))

                from rich.console import Group

                combined = Group(*blocks)
                if title:
                    title_text = Text(str(title), style=f"bold {theme_manager.get_color('accent')}")
                    panel = Panel(
                        combined,
                        title=title_text,
                        title_align="center",
                        border_style=theme_manager.get_color("table.border"),
                        padding=(1, 2),
                        expand=False,
                    )
                    return panel if return_renderable else self.console.print(panel)
                return combined if return_renderable else self.console.print(combined)
            except Exception:
                # Fall back to table-only
                pass

        if title:
            title_text = Text(str(title), style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
                expand=False,
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)

    # -------- Reservations list --------
    def render_reservations_table(
        self,
        reservations: Iterable[Any],
        *,
        columns: Sequence[str] | None = None,
        local_time: bool = False,
        show_price: bool = False,
        price_priority: str = "med",
        title: str | None = None,
        return_renderable: bool = False,
    ):
        col_order = (
            list(columns)
            if columns
            else [
                "ID",
                "Status",
                "Type",
                "Qty",
                "Region",
                "StartUTC",
                "EndUTC",
                "StartIn",
                "Window",
                "Slurm",
            ]
        )

        table = Table(
            box=None,
            show_header=True,
            header_style=theme_manager.get_color("table.header"),
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=False,
        )
        for name in col_order:
            justify = (
                "right"
                if name in {"Qty", "StartIn", "Window"}
                else ("center" if name == "Status" else "left")
            )
            width = 8 if name in {"Qty", "StartIn", "Window"} else None
            table.add_column(
                name, justify=justify, width=width, no_wrap=name in {"Qty", "StartIn", "Window"}
            )

        any_rows = False
        # Optional pricing support
        if show_price:
            try:
                from flow.domain.pricing import calculator as pricing_core

                pricing_table = pricing_core.get_pricing_table()

                def _price_for(it_name: str | None) -> float:
                    try:
                        return float(
                            pricing_core.calculate_instance_price(
                                it_name or "", priority=price_priority, pricing_table=pricing_table
                            )
                        )
                    except Exception:
                        return 0.0

            except Exception:
                show_price = False

                def _price_for(_it: str | None) -> float:
                    return 0.0

        else:

            def _price_for(_it: str | None) -> float:  # type: ignore[no-redef]
                return 0.0

        for r in reservations:
            try:
                rid = getattr(r, "reservation_id", None) or getattr(r, "id", None) or ""
                status_obj = getattr(r, "status", None)
                status = getattr(status_obj, "value", None) or str(status_obj or "")
                it = getattr(r, "instance_type", "")
                qty = int(getattr(r, "quantity", 1) or 1)
                region = getattr(r, "region", "")
                st = _to_utc(getattr(r, "start_time_utc", None) or getattr(r, "start_time", None))
                et = _to_utc(getattr(r, "end_time_utc", None) or getattr(r, "end_time", None))
                meta = getattr(r, "provider_metadata", {}) or {}
                slurm = "yes" if (meta.get("slurm") or {}) else "-"
                # Numeric hours for pricing
                hours_num = 0
                try:
                    if st and et:
                        hours_num = max(0, int(round((et - st).total_seconds() / 3600)))
                except Exception:
                    hours_num = 0
                row_map: dict[str, str] = {
                    "ID": str(rid),
                    "Status": str(status),
                    "Type": str(it),
                    "Qty": str(qty),
                    "Region": str(region or "-"),
                    "StartUTC": _format_dt(st, local_time=local_time),
                    "EndUTC": _format_dt(et, local_time=local_time),
                    "StartIn": _format_countdown(st),
                    "Window": _format_window(st, et),
                    "Slurm": slurm,
                }
                if show_price:
                    try:
                        per_inst = _price_for(str(it or ""))
                        est_total = per_inst * max(1, qty) * max(1, hours_num)
                        row_map["EstUSD"] = f"${est_total:,.2f}"
                    except Exception:
                        row_map["EstUSD"] = "-"
                table.add_row(*[row_map.get(c, "-") for c in col_order])
                any_rows = True
            except Exception:
                # Be defensive; skip problematic rows to avoid breaking listing
                continue

        if not any_rows:
            empty = Panel("No reservations found", border_style=theme_manager.get_color("muted"))
            return (
                empty
                if return_renderable
                else self.console.print("[dim]No reservations found[/dim]")
            )

        if title:
            title_text = Text(str(title), style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
                expand=False,
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)

    # -------- Single reservation details --------
    def render_reservation_details(
        self,
        reservation: Any,
        *,
        local_time: bool = False,
        show_price: bool = False,
        price_priority: str = "med",
        title: str | None = None,
        return_renderable: bool = False,
    ):
        try:
            rid = (
                getattr(reservation, "reservation_id", None)
                or getattr(reservation, "id", None)
                or ""
            )
            status_obj = getattr(reservation, "status", None)
            status = getattr(status_obj, "value", None) or str(status_obj or "")
            it = getattr(reservation, "instance_type", "")
            qty = int(getattr(reservation, "quantity", 1) or 1)
            region = getattr(reservation, "region", "")
            st = _to_utc(
                getattr(reservation, "start_time_utc", None)
                or getattr(reservation, "start_time", None)
            )
            et = _to_utc(
                getattr(reservation, "end_time_utc", None) or getattr(reservation, "end_time", None)
            )
        except Exception:
            # Fallback to simple print if attributes are missing
            rid = str(getattr(reservation, "reservation_id", ""))
            status = str(getattr(reservation, "status", ""))
            it = str(getattr(reservation, "instance_type", ""))
            qty = int(getattr(reservation, "quantity", 1) or 1)
            region = str(getattr(reservation, "region", ""))
            st = _to_utc(getattr(reservation, "start_time_utc", None))
            et = _to_utc(getattr(reservation, "end_time_utc", None))

        table = Table(
            box=None,
            show_header=False,
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=False,
        )
        table.add_column("Field", style=theme_manager.get_color("accent"), no_wrap=True)
        table.add_column("Value")

        table.add_row("Reservation", f"[accent]{rid}[/accent]")
        table.add_row("Status", str(status))
        table.add_row("Type", str(it))
        table.add_row("Quantity", str(qty))
        table.add_row("Region", str(region))
        table.add_row("Start", _format_dt(st, local_time=local_time))
        table.add_row("End", _format_dt(et, local_time=local_time))
        table.add_row("Start In", _format_countdown(st))
        table.add_row("Window", _format_window(st, et))
        if show_price:
            try:
                from flow.domain.pricing import calculator as pricing_core

                hours_num = 0
                if st and et:
                    hours_num = max(0, int(round((et - st).total_seconds() / 3600)))
                per_inst = pricing_core.calculate_instance_price(
                    it, priority=price_priority, pricing_table=pricing_core.get_pricing_table()
                )
                est_total = per_inst * max(1, int(qty)) * max(1, hours_num)
                table.add_row("Estimated Cost", f"${est_total:,.2f}")
            except Exception:
                table.add_row("Estimated Cost", "-")

        if title:
            title_text = Text(str(title), style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
                expand=False,
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)
