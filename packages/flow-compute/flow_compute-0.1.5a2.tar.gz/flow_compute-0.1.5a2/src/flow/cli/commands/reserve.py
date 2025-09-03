from __future__ import annotations

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.services.reservations_service import ReservationsService
from flow.cli.ui.presentation.reservations_view import (
    handle_availability_flow,
    handle_list_flow,
    render_reservation_details,
)
from flow.cli.utils.error_handling import cli_error_guard
from flow.sdk.factory import create_client


class ReserveCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "reserve"

    @property
    def help(self) -> str:
        return "Reserve capacity (create/list/show)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help, invoke_without_command=True)
        @click.pass_context
        @cli_error_guard(self)
        def grp(ctx):
            # Initialize and cache a single client per invocation for reuse
            try:
                ctx.ensure_object(dict)
                if (ctx.obj or {}).get("flow_client") is None:
                    ctx.obj["flow_client"] = create_client(auto_init=True)
            except Exception:
                ctx.ensure_object(dict)
                ctx.obj["flow_client"] = None

            # If invoked without a subcommand, run the wizard in TTY
            try:
                import sys as _sys

                no_sub = ctx.invoked_subcommand is None
                is_tty = bool(getattr(_sys.stdout, "isatty", lambda: False)()) and bool(
                    getattr(_sys.stdin, "isatty", lambda: True)()
                )
            except Exception:
                no_sub = False
                is_tty = False

            if no_sub and is_tty:
                try:
                    from flow.cli.ui.components.reserve_wizard import ReserveWizard as _Wizard

                    flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                    flow = flow or create_client(auto_init=True)
                    _Wizard(console).run(flow)
                    return
                except KeyboardInterrupt:
                    return
                except Exception as e:
                    # Fall through to help on wizard errors
                    try:
                        console.print(f"[error]Wizard error:[/error] {e}")
                    except Exception:
                        pass
            if no_sub and not is_tty:
                # Non-TTY: show concise guidance
                try:
                    console.print("Usage: flow reserve [availability|create|list|show|now]")
                except Exception:
                    pass

        @grp.command(name="availability", help="Get availability slots for reservations")
        @click.option(
            "-i",
            "--instance-type",
            "instance_type",
            required=False,
            help="Instance type (e.g., h100, 8xh100); when omitted, use selector in TTY (Phase 2)",
        )
        @click.option(
            "-r", "--region", required=False, help="Region/zone; defaults from config when omitted"
        )
        @click.option(
            "-s",
            "--earliest",
            "earliest_start_time",
            required=False,
            help="Earliest start (ISO8601 or relative: now, +2h); default: now",
        )
        @click.option(
            "-e",
            "--latest",
            "latest_end_time",
            required=False,
            help="Latest end (ISO8601); default: earliest + duration",
        )
        @click.option(
            "-q",
            "--qty",
            "quantity",
            type=int,
            default=None,
            help="Requested instance quantity (default 1)",
        )
        @click.option(
            "-d",
            "--duration",
            type=int,
            default=None,
            help="Requested duration in hours (default 8)",
        )
        @click.option(
            "--mode",
            type=click.Choice(["slots", "latest_end_time", "check"], case_sensitive=False),
            default=None,
            help="Availability mode (provider-dependent). Defaults to 'slots' for TTY and 'latest_end_time' for --json",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option("--local-time", is_flag=True, help="Display local time in tables")
        @click.option(
            "--show-price", is_flag=True, help="Show estimated price (heuristic)", hidden=True
        )
        @click.option(
            "--grid", is_flag=True, help="Show compact daily grid under table", hidden=True
        )
        @click.pass_context
        def availability_cmd(
            ctx,
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
            """Call reservations availability and display slots (delegated to view)."""
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            provider = flow.provider

            # Gather project from centralized config (provider_config) or env; fail fast if missing
            project = None
            try:
                cfg = getattr(flow, "config", None)
                if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                    project = cfg.provider_config.get("project")
            except Exception:
                project = None
            if not project:
                import os as _os

                project = _os.getenv("MITHRIL_PROJECT_ID") or _os.getenv("MITHRIL_PROJECT")
            if not project:
                console.print(
                    "Project is required for availability. Run 'flow init' or set MITHRIL_PROJECT."
                )
                return

            # Derive defaults for optional inputs
            import sys as _sys

            from flow.cli.services.reservations_service import ReservationsService as _RS

            # Default duration (hours)
            duration = int(duration) if duration is not None else 8
            # Parse earliest (default now)
            parsed_earliest = _RS.parse_time_expr(earliest_start_time or "now")
            # Compute latest if omitted
            latest_end_time = latest_end_time or _RS.parse_time_expr(parsed_earliest)
            try:
                from datetime import datetime as _dt
                from datetime import timedelta as _td

                st = _dt.fromisoformat(parsed_earliest.replace("Z", "+00:00"))
                if not latest_end_time or latest_end_time == parsed_earliest:
                    et = (st + _td(hours=duration)).replace(microsecond=0).isoformat() + "Z"
                    latest_end_time = et
            except Exception:
                # Best effort: if parsing fails, keep provided values and let service validate
                pass

            # Local time default: true in TTY unless --json
            try:
                if (
                    not output_json
                    and not local_time
                    and bool(getattr(_sys.stdout, "isatty", lambda: False)())
                ):
                    local_time = True
            except Exception:
                pass

            # Instance type sanity
            if not instance_type:
                console.print("Instance type is required. Pass -i/--instance-type (e.g., h100).")
                return
            # Region default from config if omitted
            if not region:
                try:
                    cfg = getattr(flow, "config", None)
                    if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                        region = cfg.provider_config.get("region")
                except Exception:
                    region = None
            if not region:
                console.print(
                    "Region is required. Set a default with 'flow init' or pass -r/--region."
                )
                return

            # Mode default: slots for TTY, latest_end_time for JSON
            if mode is None:
                try:
                    is_tty = bool(getattr(_sys.stdout, "isatty", lambda: False)()) and bool(
                        getattr(_sys.stdin, "isatty", lambda: True)()
                    )
                except Exception:
                    is_tty = False
                mode = "slots" if (not output_json and is_tty) else "latest_end_time"

            try:
                handle_availability_flow(
                    console,
                    flow_client=flow,
                    instance_type=instance_type,
                    region=region,
                    earliest_start_time=parsed_earliest,
                    latest_end_time=latest_end_time,
                    quantity=quantity,
                    duration=duration,
                    mode=mode,
                    output_json=output_json,
                    local_time=local_time,
                    show_price=show_price,
                    grid=grid,
                )
            except Exception as e:
                self.handle_error(e)
                return

        @grp.command(name="create", help="Create a new reservation")
        @click.option("--instance-type", "instance_type", required=True)
        @click.option("--region", required=False)
        @click.option("--quantity", type=int, default=1)
        @click.option(
            "--start",
            "start_time",
            required=True,
            help="ISO8601 UTC or relative time (e.g., +2h, +30m, now)",
        )
        @click.option("--duration", "duration_hours", type=int, required=True)
        @click.option("--name", default=None)
        @click.option("--ssh-key", "ssh_keys", multiple=True)
        @click.option(
            "--with-slurm",
            is_flag=True,
            help="Provision Slurm controller/workers for this reservation",
        )
        @click.option(
            "--slurm-version", default=None, help="Requested Slurm version (e.g., 25.05.1)"
        )
        @click.option(
            "--format",
            "format_",
            type=click.Choice(["table", "json"], case_sensitive=False),
            default="table",
            show_default=True,
            help="Output format",
        )
        @click.option(
            "--json", "output_json", is_flag=True, help="Output JSON (alias for --format json)"
        )
        @click.pass_context
        def create(
            ctx,
            instance_type: str,
            region: str | None,
            quantity: int,
            start_time: str,
            duration_hours: int,
            name: str | None,
            ssh_keys: tuple[str, ...],
            with_slurm: bool,
            slurm_version: str | None,
            format_: str,
            output_json: bool,
        ):
            # Parse absolute or relative start and normalize to ISO Z
            try:
                start_iso = ReservationsService.isoformat_utc_z(
                    ReservationsService.parse_time_expr(start_time)
                )
            except Exception as e:
                self.handle_error(str(e))
                return

            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            service = ReservationsService(flow)
            # Capability gate: require provider reservations support
            if not service.supports_reservations():
                console.print(
                    "Reservations are not supported by the current provider (demo/mock mode)."
                )
                try:
                    self.show_next_actions(
                        [
                            "Switch provider: flow init --provider mithril",
                            "Create a reservation: flow reserve create --instance-type h100 --start <ISO> --duration <h>",
                        ]
                    )
                except Exception:
                    pass
                return
            # Build a minimal TaskConfig to carry startup script env and num_instances
            env: dict[str, str] | None = None
            if with_slurm:
                env = {"_FLOW_WITH_SLURM": "1"}
                if slurm_version:
                    env["_FLOW_SLURM_VERSION"] = slurm_version
            task = service.create_reservation(
                instance_type=instance_type,
                region=region,
                quantity=quantity,
                start_time_iso_z=start_iso,
                duration_hours=duration_hours,
                name=name,
                ssh_keys=list(ssh_keys or ()),
                env=env,
            )
            rid = (
                task.provider_metadata.get("reservation", {}).get("reservation_id")
                if getattr(task, "provider_metadata", None)
                else None
            )
            # Telemetry: availability->create funnel attribution (best effort)
            ReservationsService.telemetry(
                "reservations.create",
                {
                    "instance_type": instance_type,
                    "region": region,
                    "quantity": quantity,
                    "duration_hours": duration_hours,
                    "with_slurm": with_slurm,
                    "slurm_version": slurm_version,
                    "reservation_id": rid or task.task_id,
                },
            )
            fmt = "json" if output_json else (format_ or "table")
            if fmt == "json":
                from flow.cli.utils.json_output import print_json

                print_json({"reservation_id": rid or task.task_id, "task_id": task.task_id})
                return
            console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
            # Next steps
            try:
                ref = rid or task.task_id
                self.show_next_actions(
                    [
                        "List reservations: [accent]flow reserve list[/accent]",
                        f"Show details: [accent]flow reserve show {ref}[/accent]",
                        "Monitor tasks: [accent]flow status --all[/accent]",
                    ]
                )
            except Exception:
                pass

        @grp.command(name="list", help="List reservations")
        @click.option(
            "--json", "output_json", is_flag=True, help="Output JSON (alias for --format json)"
        )
        @click.option("--slurm-only", is_flag=True, help="Show only Slurm-enabled reservations")
        @click.option(
            "--status",
            type=click.Choice(["scheduled", "active", "expired", "failed"], case_sensitive=False),
            default=None,
            help="Filter by status",
        )
        @click.option("--region", type=str, default=None, help="Filter by region")
        @click.option(
            "--instance-type",
            "instance_type",
            type=str,
            default=None,
            help="Filter by instance type",
        )
        @click.option(
            "--format",
            "format_",
            type=click.Choice(["table", "json", "csv", "yaml"], case_sensitive=False),
            default="table",
            show_default=True,
            help="Output format",
        )
        @click.option(
            "--columns", type=str, default=None, help="Comma-separated columns for table output"
        )
        @click.option(
            "--local-time", is_flag=True, help="Display local time instead of UTC in tables"
        )
        @click.pass_context
        def list_cmd(
            ctx,
            output_json: bool,
            slurm_only: bool,
            status: str | None,
            region: str | None,
            instance_type: str | None,
            format_: str,
            columns: str | None,
            local_time: bool,
        ):
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            try:
                cols = [c.strip() for c in columns.split(",") if c.strip()] if columns else None
                handle_list_flow(
                    console,
                    flow_client=flow,
                    output_json=output_json,
                    slurm_only=slurm_only,
                    status=status,
                    region=region,
                    instance_type=instance_type,
                    format_=format_,
                    columns=cols,
                    local_time=local_time,
                )
            except Exception as e:
                self.handle_error(e)
                return

        @grp.command(name="show", help="Show reservation details")
        @click.argument("reservation_id")
        @click.option(
            "--json", "output_json", is_flag=True, help="Output JSON (alias for --format json)"
        )
        @click.option(
            "--format",
            "format_",
            type=click.Choice(["table", "json"], case_sensitive=False),
            default="table",
            show_default=True,
            help="Output format",
        )
        @click.option(
            "--local-time", is_flag=True, help="Display local time instead of UTC in tables"
        )
        @click.option("--watch", is_flag=True, help="Live update the reservation details")
        @click.option(
            "--refresh-rate",
            type=float,
            default=5.0,
            show_default=True,
            help="Refresh interval for --watch (seconds)",
        )
        @click.pass_context
        def show_cmd(
            ctx,
            reservation_id: str,
            output_json: bool,
            format_: str,
            local_time: bool,
            watch: bool,
            refresh_rate: float,
        ):
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            provider = flow.provider
            try:
                if not hasattr(provider, "get_reservation") and not hasattr(
                    flow, "get_reservation"
                ):
                    console.print(
                        "Reservations are not supported by the current provider (demo/mock mode)."
                    )
                    return
                # Prefer Flow wrapper, then provider fallback
                try:
                    res = flow.get_reservation(reservation_id)
                except Exception:
                    res = provider.get_reservation(reservation_id)
            except Exception as e:
                self.handle_error(e)
                return
            fmt = "json" if output_json else (format_ or "table")
            if fmt == "json":
                from flow.cli.utils.json_output import print_json, reservation_to_json

                print_json(reservation_to_json(res))
                return
            # Telemetry (best-effort)
            ReservationsService.telemetry(
                "reservations.show",
                {
                    "reservation_id": reservation_id,
                    "format": fmt,
                    "watch": watch,
                    "refresh_rate": refresh_rate,
                },
            )
            if watch:
                try:
                    from flow.cli.ui.presentation.reservations_view import (
                        render_reservation_live,
                    )

                    def _fetch_once():
                        try:
                            return flow.get_reservation(reservation_id)
                        except Exception:
                            return res

                    render_reservation_live(
                        console,
                        fetch_once=_fetch_once,
                        local_time=local_time,
                        refresh_rate=refresh_rate,
                    )
                except KeyboardInterrupt:
                    return
                except Exception:
                    # Fallback to single-shot render
                    render_reservation_details(
                        console, res, local_time=local_time, title="Reservation"
                    )
            else:
                render_reservation_details(console, res, local_time=local_time, title="Reservation")
                # Next steps
                try:
                    self.show_next_actions(
                        [
                            "List reservations: [accent]flow reserve list[/accent]",
                            "Monitor capacity: [accent]flow alloc --watch[/accent]",
                        ]
                    )
                except Exception:
                    pass

        @grp.command(
            name="extension-availability", help="Show extension availability for a reservation"
        )
        @click.argument("reservation_id")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option("--local-time", is_flag=True, help="Display local time in tables")
        @click.pass_context
        def extension_availability_cmd(
            ctx,
            reservation_id: str,
            output_json: bool,
            local_time: bool,
        ) -> None:
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            service = ReservationsService(flow)
            try:
                slots = service.extension_availability(reservation_id)
            except Exception as e:
                self.handle_error(e)
                return
            if output_json:
                import json as _json

                console.print(_json.dumps(slots))
                return
            if not slots:
                console.print("No extension availability or provider unsupported.")
                return
            from flow.cli.ui.presentation.reservations_view import render_availability

            render_availability(
                console,
                slots,
                local_time=local_time,
                show_price=False,
                title="Extension Availability",
                grid=False,
            )

        @grp.command(name="extend", help="Extend a reservation's end time")
        @click.argument("reservation_id")
        @click.option(
            "--end-time",
            "end_time",
            required=True,
            help="New end time (ISO8601 or relative: +2h, +30m, now)",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        def extend_cmd(
            ctx,
            reservation_id: str,
            end_time: str,
            output_json: bool,
        ) -> None:
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)
            service = ReservationsService(flow)
            # Parse and normalize end time
            try:
                end_iso = ReservationsService.isoformat_utc_z(
                    ReservationsService.parse_time_expr(end_time)
                )
            except Exception as e:
                self.handle_error(e)
                return
            try:
                res = service.extend(reservation_id, end_iso)
            except Exception as e:
                self.handle_error(e)
                return
            if output_json:
                from flow.cli.utils.json_output import print_json

                print_json({"ok": bool(res is not None), "end_time": end_iso})
                return
            if res is None:
                console.print("Provider does not support reservation extension or request failed.")
                return
            console.print(f"Requested extension to: [accent]{end_iso}[/accent]")

        @grp.command(name="now", help="Reserve capacity starting now with fast fallback")
        @click.option("-i", "--instance-type", "instance_type", required=False)
        @click.option("-r", "--region", required=False)
        @click.option("-d", "--duration", type=int, default=None, help="Duration hours (default 8)")
        @click.option(
            "-q", "--qty", "quantity", type=int, default=None, help="Quantity (default 1)"
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option("--local-time", is_flag=True, help="Display local time")
        @click.pass_context
        def reserve_now(
            ctx,
            instance_type: str | None,
            region: str | None,
            duration: int | None,
            quantity: int | None,
            output_json: bool,
            local_time: bool,
        ) -> None:
            """Check immediate availability; reserve now or suggest nearest slot."""
            flow = (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
            flow = flow or create_client(auto_init=True)

            # Project required (centralized config or env)
            project = None
            try:
                cfg = getattr(flow, "config", None)
                if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                    project = cfg.provider_config.get("project")
            except Exception:
                project = None
            if not project:
                import os as _os

                project = _os.getenv("MITHRIL_PROJECT_ID") or _os.getenv("MITHRIL_PROJECT")
            if not project:
                console.print("Project is required. Run 'flow init' or set MITHRIL_PROJECT.")
                return

            import sys as _sys
            from datetime import datetime as _dt
            from datetime import timedelta as _td
            from datetime import timezone as _tz

            from flow.cli.services.reservations_service import ReservationsService as _RS
            from flow.cli.ui.presentation.reservations_renderer import (
                ReservationsRenderer as _Renderer,
            )

            # Defaults
            duration = int(duration) if duration is not None else 8
            quantity = int(quantity) if quantity is not None else 1
            if not instance_type:
                console.print("Instance type is required. Pass -i/--instance-type (e.g., h100).")
                return
            if not region:
                try:
                    cfg = getattr(flow, "config", None)
                    if cfg and isinstance(getattr(cfg, "provider_config", None), dict):
                        region = cfg.provider_config.get("region")
                except Exception:
                    region = None
            if not region:
                console.print(
                    "Region is required. Set a default with 'flow init' or pass -r/--region."
                )
                return

            # Local time default for TTY
            try:
                if (
                    not output_json
                    and not local_time
                    and bool(getattr(_sys.stdout, "isatty", lambda: False)())
                ):
                    local_time = True
            except Exception:
                pass

            service = ReservationsService(flow)

            # Compute now -> now+duration window
            now_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc))
            end_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(hours=duration))

            # Immediate check: get slots in the exact duration window
            try:
                slots_raw = service.availability(
                    _RS.AvailabilityQuery(
                        instance_type=instance_type,
                        region=str(region),
                        earliest_start_time=now_iso,
                        latest_end_time=end_iso,
                        quantity=quantity,
                        duration_hours=duration,
                        mode="slots",
                    )
                )
            except Exception as e:
                self.handle_error(e)
                return
            slots = _RS.normalize_slots(slots_raw)

            # Determine if we can start now: slot starting at now with enough duration
            def _can_start_now(slot: dict) -> bool:
                try:
                    st = _RS._to_dt(slot.get("start_time_utc"))  # type: ignore[attr-defined]
                    return bool(
                        st
                        and abs(
                            (st - _dt.fromisoformat(now_iso.replace("Z", "+00:00"))).total_seconds()
                        )
                        < 120
                    )
                except Exception:
                    return False

            immediate = None
            for s in slots:
                if (
                    _can_start_now(s)
                    and _RS.slot_duration_hours(s) >= int(duration or 1)
                    and int(s.get("quantity", 0) or 0) >= int(quantity or 1)
                ):
                    immediate = s
                    break

            if immediate is not None:
                # Create reservation starting now
                try:
                    task = service.create_reservation(
                        instance_type=instance_type,
                        region=str(region),
                        quantity=int(quantity or 1),
                        start_time_iso_z=now_iso,
                        duration_hours=int(duration or 1),
                        name=f"reservation-{instance_type}",
                        ssh_keys=[],
                        env=None,
                    )
                except Exception as e:
                    self.handle_error(e)
                    return
                rid = (
                    task.provider_metadata.get("reservation", {}).get("reservation_id")
                    if getattr(task, "provider_metadata", None)
                    else None
                )
                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {
                            "reserved": True,
                            "reservation_id": rid or task.task_id,
                            "task_id": task.task_id,
                        }
                    )
                    return
                console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
                return

            # Fallback: search next 24 hours, offer earliest slot
            horizon_iso = _RS.isoformat_utc_z(_dt.now(_tz.utc) + _td(hours=24))
            try:
                slots_raw2 = service.availability(
                    _RS.AvailabilityQuery(
                        instance_type=instance_type,
                        region=str(region),
                        earliest_start_time=now_iso,
                        latest_end_time=horizon_iso,
                        quantity=quantity,
                        duration_hours=duration,
                        mode="slots",
                    )
                )
            except Exception as e:
                self.handle_error(e)
                return
            slots2 = _RS.filter_slots(
                _RS.normalize_slots(slots_raw2), min_quantity=quantity, min_duration_hours=duration
            )

            if output_json:
                from flow.cli.utils.json_output import print_json

                print_json({"reserved": False, "slots": slots2})
                return

            if not slots2:
                console.print(
                    "No self-serve availability found within the next 24 hours. Please reach out to the Flow team."
                )
                return

            recommended = slots2[0]
            console.print("Earliest available slot:")
            try:
                _Renderer(console).render_availability_table(
                    [recommended], local_time=local_time, show_price=False, title=None
                )
            except Exception:
                pass
            try:
                import click as _click

                if _click.confirm("Reserve this slot?", default=True):
                    start_iso = _RS.isoformat_utc_z(recommended.get("start_time_utc"))
                    try:
                        task = service.create_reservation(
                            instance_type=instance_type,
                            region=str(region),
                            quantity=int(quantity or 1),
                            start_time_iso_z=start_iso,
                            duration_hours=int(duration or 1),
                            name=f"reservation-{instance_type}",
                            ssh_keys=[],
                            env=None,
                        )
                    except Exception as e:
                        self.handle_error(e)
                        return
                    rid = (
                        task.provider_metadata.get("reservation", {}).get("reservation_id")
                        if getattr(task, "provider_metadata", None)
                        else None
                    )
                    console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")
                    return
            except Exception:
                pass
            console.print("Reservation not created.")

        return grp


command = ReserveCommand()
