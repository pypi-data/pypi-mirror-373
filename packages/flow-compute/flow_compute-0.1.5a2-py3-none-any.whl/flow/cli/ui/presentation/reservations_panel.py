"""Presentation for the optional Reservations side panel in status view."""

from __future__ import annotations

from datetime import datetime, timezone

from rich.panel import Panel
from rich.table import Table


def render_reservations_panel(provider) -> Panel | None:
    try:
        caps = None
        try:
            caps = provider.get_capabilities()
        except Exception:
            caps = None
        if not (
            caps is not None
            and getattr(caps, "supports_reservations", False) is True
            and hasattr(provider, "list_reservations")
        ):
            return None

        try:
            try:
                from flow.sdk.client import Flow as _Flow

                if isinstance(flow, _Flow):
                    reservations = flow.reservations.list()
                else:
                    reservations = provider.list_reservations()
            except Exception:
                reservations = provider.list_reservations()
        except Exception:
            reservations = []

        def _start(r):
            return getattr(r, "start_time_utc", None) or datetime.now(timezone.utc)

        try:
            if isinstance(reservations, list):
                reservations.sort(key=_start)
                reservations = reservations[:5]
            else:
                reservations = []
        except Exception:
            reservations = []

        if not reservations:
            return None

        table = Table(show_header=True, header_style="bold", expand=False)
        table.add_column("Name", no_wrap=True)
        table.add_column("Type", no_wrap=True)
        table.add_column("Qty", justify="right")
        table.add_column("Region", no_wrap=True)
        table.add_column("Start (UTC)")
        table.add_column("Start In", justify="right")
        table.add_column("Window", justify="right")

        now = datetime.now(timezone.utc)
        for r in reservations:
            name = getattr(r, "name", None) or getattr(r, "reservation_id", "-")
            it = getattr(r, "instance_type", "-")
            qty = str(getattr(r, "quantity", 1))
            region = getattr(r, "region", "-")
            st = getattr(r, "start_time_utc", None)
            et = getattr(r, "end_time_utc", None)
            start_str = st.isoformat().replace("+00:00", "Z") if st else "-"
            start_in = "-"
            if st:
                try:
                    delta_min = max(0, int((st - now).total_seconds() // 60))
                    start_in = f"{delta_min}m" if delta_min < 120 else f"{delta_min//60}h"
                except Exception:
                    pass
            window = "-"
            if st and et:
                try:
                    dur_h = int(round((et - st).total_seconds() / 3600))
                    window = f"{dur_h}h"
                except Exception:
                    pass
            table.add_row(name, it, qty, region, start_str, start_in, window)

        return Panel(table, title="Reservations", border_style="bright_black")
    except Exception:
        return None
