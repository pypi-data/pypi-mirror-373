"""Reservations presentation wrappers."""

from __future__ import annotations

import sys as _sys
from collections.abc import Iterable
from typing import Any

from rich.console import Console
from rich.live import Live

# Service-layer imports kept here to centralize orchestration logic for the
# reservations command while keeping the CLI command file slim.
from flow.cli.services.reservations_service import (
    AvailabilityQuery,
    ReservationsService,
)
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress as AEP
from flow.cli.ui.presentation.reservations_renderer import ReservationsRenderer


def render_availability(
    console: Console,
    slots: list[dict[str, Any]],
    *,
    local_time: bool,
    show_price: bool,
    title: str | None = None,
    grid: bool = False,
) -> None:
    renderer = ReservationsRenderer()
    renderer.render_availability_table(
        slots, title=title, local_time=local_time, show_price=show_price, grid=grid
    )


def render_reservations_table(
    console: Console,
    items: Iterable[object],
    *,
    columns: list[str] | None,
    local_time: bool,
    title: str,
) -> None:
    renderer = ReservationsRenderer()
    renderer.render_reservations_table(
        list(items), columns=columns, local_time=local_time, title=title
    )


def render_reservation_details(
    console: Console, res: object, *, local_time: bool, title: str = "Reservation"
) -> None:
    renderer = ReservationsRenderer()
    renderer.render_reservation_details(res, local_time=local_time, title=title)


def render_reservations_csv(console: Console, items: Iterable[object]) -> None:
    import csv as _csv
    import io as _io

    output = _io.StringIO()
    writer = _csv.writer(output)
    header = [
        "reservation_id",
        "status",
        "instance_type",
        "quantity",
        "region",
        "start_time_utc",
        "end_time_utc",
    ]
    writer.writerow(header)
    for it in items:
        st = getattr(it, "status", None)
        writer.writerow(
            [
                getattr(it, "reservation_id", ""),
                getattr(st, "value", None) or str(st or ""),
                getattr(it, "instance_type", ""),
                getattr(it, "quantity", 1),
                getattr(it, "region", ""),
                getattr(it, "start_time_utc", None),
                getattr(it, "end_time_utc", None),
            ]
        )
    console.print(output.getvalue().rstrip("\n"))


def render_reservations_yaml(console: Console, items: Iterable[object]) -> None:
    try:
        import yaml as _yaml

        console.print(
            _yaml.safe_dump(
                [getattr(it, "model_dump", lambda: it)() for it in items], sort_keys=False
            )
        )
    except Exception:
        import json as _json

        console.print(_json.dumps([getattr(it, "model_dump", lambda: it)() for it in items]))


def render_reservation_live(
    console: Console, *, fetch_once: callable, local_time: bool, refresh_rate: float
) -> None:  # type: ignore[valid-type]
    renderer = ReservationsRenderer()
    res = fetch_once()
    initial = renderer.render_reservation_details(
        res, local_time=local_time, title="Reservation", return_renderable=True
    )
    with Live(initial, console=console, refresh_per_second=4, transient=False) as live:
        import time as _time

        while True:
            try:
                res = fetch_once()
            except Exception:
                pass
            renderable = renderer.render_reservation_details(
                res, local_time=local_time, title="Reservation", return_renderable=True
            )
            live.update(renderable)
            _time.sleep(max(0.2, float(refresh_rate)))


def choose_availability_slot(
    slots: list[dict[str, Any]], *, region: str, instance_type: str
) -> dict[str, Any] | None:
    """Interactive selector for availability slots. Returns chosen slot or None."""
    try:
        from flow.cli.ui.components import (
            InteractiveSelector,
            SelectionItem,
        )

        def slot_to_selection(s: dict[str, Any]) -> "SelectionItem[dict[str, Any}]":  # type: ignore[name-defined]
            st = s.get("start_time_utc")
            et = s.get("end_time_utc")
            qty = s.get("quantity")
            title = f"{st} → {et}"
            subtitle = (
                f"qty={qty} {s.get('region') or region} {s.get('instance_type') or instance_type}"
            )
            return SelectionItem(value=s, id=title, title=title, subtitle=subtitle, status=None)

        selector = InteractiveSelector(
            items=slots,
            item_to_selection=slot_to_selection,
            title="Select an availability slot",
            allow_multiple=False,
            show_preview=True,
        )
        chosen = selector.select()
        return chosen if isinstance(chosen, dict) else None
    except Exception:
        return None


# ================ Orchestrated CLI flows ================


def handle_availability_flow(
    console: Console,
    *,
    flow_client: Any,
    instance_type: str,
    region: str,
    earliest_start_time: str,
    latest_end_time: str,
    quantity: int | None,
    duration: int | None,
    mode: str | None,
    output_json: bool,
    local_time: bool,
    show_price: bool,
    grid: bool,
) -> None:
    """End-to-end availability command flow with optional reservation creation."""
    service = ReservationsService(flow_client)

    # Build and execute availability query
    with AEP(console, "Checking reservation availability", start_immediately=True, pad_top=0):
        slots_raw = service.availability(
            AvailabilityQuery(
                instance_type=instance_type,
                region=region,
                earliest_start_time=earliest_start_time,
                latest_end_time=latest_end_time,
                quantity=quantity,
                duration_hours=duration,
                mode=mode,
            )
        )
    slots = ReservationsService.normalize_slots(slots_raw)
    slots = ReservationsService.filter_slots(
        slots,
        min_quantity=quantity,
        min_duration_hours=duration,
    )

    # Non-interactive/automation
    is_tty = bool(getattr(_sys.stdout, "isatty", lambda: False)()) and bool(
        getattr(_sys.stdin, "isatty", lambda: True)()
    )
    if output_json or not is_tty:
        import json as _json

        console.print(_json.dumps(slots))
        return

    # Telemetry (best-effort)
    ReservationsService.telemetry(
        "reservations.availability",
        {
            "instance_type": instance_type,
            "region": region,
            "qty": quantity,
            "duration_hours": duration,
            "slots": len(slots),
            "format": "table",
            "interactive": True,
            "best": True,
        },
    )

    if not slots:
        console.print(
            "[warning]No self-serve availability found for the requested window.[/warning]"
        )
        # Telemetry (best-effort)
        ReservationsService.telemetry(
            "reservations.availability.zero",
            {
                "instance_type": instance_type,
                "region": region,
                "qty": quantity,
                "duration_hours": duration,
                "mode": mode,
                "context": "cmd",
            },
        )
        # Actionable next steps (concise, avoids blocking flow)
        try:
            console.print(
                "Try one or more: \n"
                " - Expand time window or adjust duration\n"
                " - Try another region (e.g., --region us-central1-b)\n"
                " - Use spot/auto allocation (e.g., flow run --allocation auto)\n"
                " - Reach out to the Flow team to schedule capacity or discuss options"
            )
        except Exception:
            pass
        return

    # Recommended slot + confirm path
    recommended = slots[0]
    console.print("Recommended slot:")
    renderer = ReservationsRenderer(console)
    renderer.render_availability_table(
        [recommended], local_time=local_time, show_price=show_price, title=None
    )

    try:
        import click as _click

        if _click.confirm("Reserve this slot now?", default=True):

            def _derive(vals: tuple[int | None, int]) -> int:
                for v in vals:
                    if v and isinstance(v, int) and v > 0:
                        return v
                return 1

            req_qty = _derive((quantity, recommended.get("quantity", 1)))
            req_dur = _derive((duration, ReservationsService.slot_duration_hours(recommended)))
            start_iso = ReservationsService.isoformat_utc_z(recommended.get("start_time_utc"))
            task = service.create_reservation(
                instance_type=instance_type,
                region=region,
                quantity=req_qty,
                start_time_iso_z=start_iso,
                duration_hours=req_dur,
                name=f"reservation-{instance_type}",
                ssh_keys=[],
            )
            rid = (
                task.provider_metadata.get("reservation", {}).get("reservation_id")
                if getattr(task, "provider_metadata", None)
                else None
            )
            console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
            return
    except Exception:
        # Fall through to selection/table paths
        pass

    # Optional interactive selection if declined
    chosen_slot = choose_availability_slot(slots, region=region, instance_type=instance_type)
    if chosen_slot:
        try:
            import click as _click

            if _click.confirm("Reserve selected slot?", default=True):
                req_qty = max(1, int(quantity or chosen_slot.get("quantity") or 1))
                req_dur = max(
                    1, int(duration or ReservationsService.slot_duration_hours(chosen_slot) or 1)
                )
                start_iso = ReservationsService.isoformat_utc_z(chosen_slot.get("start_time_utc"))
                task = service.create_reservation(
                    instance_type=instance_type,
                    region=region,
                    quantity=req_qty,
                    start_time_iso_z=start_iso,
                    duration_hours=req_dur,
                    name=f"reservation-{instance_type}",
                    ssh_keys=[],
                )
                rid = (
                    task.provider_metadata.get("reservation", {}).get("reservation_id")
                    if getattr(task, "provider_metadata", None)
                    else None
                )
                console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
                return
        except Exception:
            # Fallback: show all slots
            pass

    renderer.render_availability_table(
        slots,
        local_time=local_time,
        show_price=show_price,
        title="Availability",
        grid=grid,
    )


def handle_list_flow(
    console: Console,
    *,
    flow_client: Any,
    output_json: bool,
    slurm_only: bool,
    status: str | None,
    region: str | None,
    instance_type: str | None,
    format_: str,
    columns: list[str] | None,
    local_time: bool,
) -> None:
    """Reservations list flow with filtering and multiple output formats."""
    service = ReservationsService(flow_client)
    items, supported = service.list_with_prefetch()
    if not supported:
        console.print("Reservations are not supported by the current provider (demo/mock mode).")
        try:
            from flow.cli.commands.base import BaseCommand

            BaseCommand().show_next_actions(
                [
                    "Switch provider: flow init --provider mithril",
                    "Create a reservation: flow reserve create --instance-type h100 --start <ISO> --duration <h>",
                ]
            )
        except Exception:
            pass
        return

    items = service.filter_reservations(
        list(items),
        status=status,
        region=region,
        instance_type=instance_type,
        slurm_only=slurm_only,
    )

    fmt = "json" if output_json else (format_ or "table")
    if fmt == "json":
        from flow.cli.utils.json_output import print_json, reservation_to_json

        print_json([reservation_to_json(it) for it in items])
        return

    # Telemetry (best-effort)
    ReservationsService.telemetry(
        "reservations.list",
        {
            "count": len(items),
            "slurm_only": slurm_only,
            "status": status,
            "region": region,
            "instance_type": instance_type,
            "format": fmt,
        },
    )

    if fmt == "csv":
        render_reservations_csv(console, items)
        return
    if fmt == "yaml":
        render_reservations_yaml(console, items)
        return

    renderer = ReservationsRenderer(console)
    renderer.render_reservations_table(
        items, columns=columns, local_time=local_time, title="Reservations"
    )

    try:
        from flow.cli.commands.base import BaseCommand

        BaseCommand().show_next_actions(
            [
                "Create a reservation: [accent]flow reserve create --instance-type h100 --start 2025-01-01T00:00:00Z --duration 4[/accent]",
                "Show a reservation: [accent]flow reserve show <reservation-id>[/accent]",
            ]
        )
    except Exception:
        pass
