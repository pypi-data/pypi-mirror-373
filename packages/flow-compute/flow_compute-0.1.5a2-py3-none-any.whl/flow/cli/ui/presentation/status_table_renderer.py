"""Status table renderer (core).

Unified task table for the Flow CLI with compact columns.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flow.cli.ui.presentation.gpu_formatter import GPUFormatter
from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter
from flow.cli.ui.presentation.time_formatter import TimeFormatter
from flow.cli.ui.runtime.owner_resolver import Me, OwnerResolver
from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.models import Task


class StatusTableRenderer:
    """Render tasks per the compact Status Table Spec.

    Columns (core, fixed positions):
      Index | Status | Task | GPU | Owner | Age

    Wide mode appends right-side columns only.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or theme_manager.create_console()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()
        self.term = TerminalAdapter()
        # Centralized column config (DRY) — single source of truth for widths/alignments
        self._col_cfg = {
            "#": {"justify": "right", "width": 3, "no_wrap": True},
            "Status": {
                "justify": "center",
                "width": 12,  # slightly wider so long states like "completed" fit
                "min_width": 11,
                "no_wrap": True,
                "overflow": "crop",
            },
            "Task": {
                "justify": "left",
                "min_width": 16,
                "max_width": 40,
                "no_wrap": True,
                "overflow": "ellipsis",
            },
            "GPU": {
                "justify": "center",
                "width": 12,
                "min_width": 10,
                "no_wrap": True,
                "overflow": "crop",
            },
            "Owner": {
                "justify": "center",
                "min_width": 8,
                "max_width": 12,
                "no_wrap": True,
                "overflow": "ellipsis",
            },
            # Ensure Age always has room for compact formats like "8m", "11h", "2d"
            # Use width 4 to avoid header cropping edge-cases under tight padding
            "Age": {"justify": "right", "width": 4, "min_width": 3, "no_wrap": True},
        }
        # Cache for quick access
        self._gpu_col_width = self._col_cfg["GPU"].get("width", 12)

    def render(
        self,
        tasks: list[Task],
        *,
        me: Me | None = None,
        owner_map: dict[str, str] | None = None,
        title: str | None = None,
        wide: bool = False,
        start_index: int = 1,
        return_renderable: bool = False,
        forced_gpu_width: int | None = None,
    ):
        if not tasks:
            return (
                Panel("No tasks found", border_style=theme_manager.get_color("muted"))
                if return_renderable
                else self.console.print("[dim]No tasks found[/dim]")
            )

        layout = self.term.get_responsive_layout()

        # Dynamically right-size the GPU column to avoid hanging/cropping.
        # Compute the ideal width from actual content, then clamp to a sane cap
        # to keep the table compact. This is surgical and only affects the GPU column.
        gpu_width = int(self._col_cfg.get("GPU", {}).get("width", 12))
        try:
            if forced_gpu_width is None:
                desired = 0
                for t in tasks:
                    # Coerce num_instances safely
                    ni = getattr(t, "num_instances", 1)
                    try:
                        ni = max(1, int(ni))
                    except Exception:
                        ni = 1
                    # Get unconstrained (full) compact string to measure
                    s = GPUFormatter.format_ultra_compact(getattr(t, "instance_type", "") or "", ni)
                    desired = max(desired, len(s))
            else:
                desired = int(forced_gpu_width)
            # Respect column min width; cap to keep layout tidy
            gpu_min = int(self._col_cfg.get("GPU", {}).get("min_width", 10))
            gpu_cap = 18  # fits values like "32×H100·80G" comfortably
            gpu_width = max(gpu_min, min(desired, gpu_cap))
        except Exception:
            pass
        # Update effective width used by width-aware formatter downstream
        self._gpu_col_width = gpu_width

        # Allow table to expand to available width to avoid cramped columns
        table = Table(
            box=None if not title else None,
            show_header=True,
            header_style=theme_manager.get_color("table.header"),
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=True,  # Allow table to use available width to avoid header cropping
        )

        # Core columns from centralized config
        for name in ["#", "Status", "Task", "GPU", "Owner", "Age"]:
            cfg = self._col_cfg[name]
            # Column-specific, restrained styling
            if name == "#":
                style = theme_manager.get_color("muted")
            elif name == "Task":
                style = theme_manager.get_color("task.name")
            elif name == "GPU":
                style = theme_manager.get_color("accent")
            elif name == "Owner":
                style = theme_manager.get_color("muted")
            elif name == "Age":
                style = theme_manager.get_color("task.time")
            else:
                style = None

            table.add_column(
                name,
                justify=cfg.get("justify", "left"),
                width=(gpu_width if name == "GPU" else cfg.get("width")),
                min_width=cfg.get("min_width"),
                max_width=cfg.get("max_width"),
                no_wrap=cfg.get("no_wrap", False),
                overflow=cfg.get("overflow"),
                style=style,
            )

        # Wide-only appended columns
        if wide:
            table.add_column("IP", justify="left", width=15, no_wrap=True)
            table.add_column("Class", justify="left", width=6, no_wrap=True)
            table.add_column("Created", justify="right", width=10, no_wrap=True)
            # Use shorter, unambiguous headers and slightly larger widths to avoid header cropping
            table.add_column("StartIn", justify="right", width=9, no_wrap=True)
            table.add_column("Window", justify="right", width=8, no_wrap=True)

        for idx, task in enumerate(tasks, start=start_index):
            status_display = self._format_status(task)
            # Coerce possible Mock attributes to safe strings
            try:
                name_val = getattr(task, "name", None)
                if name_val is None:
                    name_val = getattr(task, "task_id", "unnamed")
                task_name = str(name_val)
            except Exception:
                task_name = "unnamed"
            gpu = self._format_gpu(task)
            owner = self._format_owner(task, me, owner_map)
            age = self.time_fmt.format_ultra_compact_age(task.created_at)

            row = [str(idx), status_display, task_name, gpu, owner, age]

            if wide:
                start_in, window = self._format_reservation_columns(task)
                row.extend(
                    [
                        task.ssh_host or "-",
                        self._format_class(task),
                        self.time_fmt.format_ultra_compact_age(task.created_at),
                        start_in,
                        window,
                    ]
                )

            table.add_row(*row)

        if title:
            from rich.markup import escape

            try:
                safe_title = escape(str(title))
            except Exception:
                safe_title = "Tasks"
            title_text = Text(safe_title, style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
                # Avoid stretching to full terminal width when content is narrow
                expand=False,
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)

    # --- Cell formatters ---

    def _format_status(self, task: Task) -> str:
        from flow.cli.ui.presentation.task_formatter import TaskFormatter

        # Width-aware hybrid: show word when it fits, otherwise compact symbol-only
        # Use configured column width when available
        try:
            STATUS_COL_WIDTH = int(self._col_cfg.get("Status", {}).get("width", 10))
        except Exception:
            STATUS_COL_WIDTH = 10
        layout = self.term.get_responsive_layout()

        display_status = TaskFormatter.get_display_status(task)

        plain_length = 2 + len(display_status)  # symbol + space + word
        compact = layout.get("use_compact_status", False) or plain_length > STATUS_COL_WIDTH
        base = (
            TaskFormatter.format_compact_status(display_status)
            if compact
            else TaskFormatter.format_status_with_color(display_status)
        )

        # Append a tiny reserved badge when space allows
        try:
            meta = getattr(task, "provider_metadata", {}) or {}
            res = meta.get("reservation")
            if res:
                # Only annotate when not extremely tight
                if not compact and (plain_length + 3) <= STATUS_COL_WIDTH:
                    # Use subtle dim 'R' badge to indicate reserved capacity
                    return f"{base} [dim]R[/dim]"
        except Exception:
            pass
        return base

    def _format_task_name(self, task: Task) -> str:
        # Let the table column control width and overflow; avoid pre-truncation
        return task.name or "unnamed"

    def _format_owner(
        self, task: Task, me: Me | None, owner_map: dict[str, str] | None = None
    ) -> str:
        created_by = getattr(task, "created_by", None)
        resolved_text: str | None = None
        # Early debug context
        try:
            import os as _os

            if (_os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                me_uid = getattr(me, "user_id", None) if me else None
                me_email = getattr(me, "email", None) if me else None
                me_un = getattr(me, "username", None) if me else None
                print(
                    f"[owner-debug] _format_owner: created_by={created_by} me.uid={me_uid} me.email={me_email} me.username={me_un} owner_map.size={len(owner_map) if isinstance(owner_map, dict) else 0}"
                )
        except Exception:
            pass
        try:
            # Centralized resolution: let OwnerResolver handle friendly mapping
            resolved_text = OwnerResolver.format_owner(created_by, me, owner_map)
        except Exception:
            resolved_text = None

        # Decide whether to accept resolver output or try to improve it using provider user info
        fallback_token = None
        try:
            fallback_token = str(created_by).replace("user_", "")[:8]
        except Exception:
            fallback_token = None

        def _derive_from_user_obj(u: object) -> str | None:
            # Support dicts and objects for user info
            if u is None:
                return None
            if isinstance(u, dict):
                # Accept more shapes for email/username/display
                email = (
                    u.get("email")
                    or u.get("primary_email")
                    or u.get("primaryEmail")
                    or u.get("email_address")
                    or u.get("emailAddress")
                )
                if not email:
                    emails = u.get("emails")
                    if isinstance(emails, list) and emails:
                        first = emails[0]
                        if isinstance(first, str):
                            email = first
                        elif isinstance(first, dict):
                            email = first.get("email") or first.get("address") or first.get("value")
                username = (
                    u.get("username")
                    or u.get("user_name")
                    or u.get("handle")
                    or u.get("name")
                    or u.get("display_name")
                    or u.get("displayName")
                    or u.get("full_name")
                    or u.get("fullName")
                    or u.get("given_name")
                    or u.get("givenName")
                )
                display = (
                    u.get("name")
                    or u.get("display_name")
                    or u.get("displayName")
                    or u.get("full_name")
                    or u.get("fullName")
                )
            else:
                email = (
                    getattr(u, "email", None)
                    or getattr(u, "primary_email", None)
                    or getattr(u, "primaryEmail", None)
                )
                username = (
                    getattr(u, "username", None)
                    or getattr(u, "user_name", None)
                    or getattr(u, "handle", None)
                    or getattr(u, "display_name", None)
                    or getattr(u, "displayName", None)
                )
                display = (
                    getattr(u, "name", None)
                    or getattr(u, "display_name", None)
                    or getattr(u, "displayName", None)
                )
            if isinstance(email, str) and "@" in email:
                local = email.split("@")[0]
                import re as _re

                first = _re.split(r"[._-]+", local)[0]
                if first:
                    return first.lower()
            if isinstance(username, str) and username.strip():
                import re as _re

                first = _re.split(r"[\s._-]+", username.strip())[0]
                if first:
                    return first.lower()
            if isinstance(display, str) and display.strip():
                import re as _re

                first = _re.split(r"[\s._-]+", display.strip())[0]
                if first:
                    return first.lower()
            return None

        # If resolver provided a non-generic label, use it
        generic_labels = {"external", "console", "system", "unknown", "you", "-"}
        if (
            resolved_text
            and resolved_text not in generic_labels
            and resolved_text != fallback_token
        ):
            return resolved_text

        # Otherwise, try to fetch user info from provider and derive a friendlier label
        try:
            u = task.get_user()
            derived = _derive_from_user_obj(u)
            if derived:
                try:
                    import os as _os

                    if (_os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                        print(
                            f"[owner-debug] created_by={created_by} resolved={resolved_text} derived_user=1 label={derived}"
                        )
                except Exception:
                    pass
                return derived
        except Exception as _e:
            try:
                import os as _os

                if (_os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                    print(f"[owner-debug] task.get_user() failed for created_by={created_by}: {_e}")
            except Exception:
                pass
            # Non-fatal: fall through to compact token
            pass
        # Accept resolver output if present (even if generic) before compact fallback
        if resolved_text:
            try:
                import os as _os

                if (_os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                    print(
                        f"[owner-debug] created_by={created_by} resolved={resolved_text} derived_user=0 label={resolved_text}"
                    )
            except Exception:
                pass
            return resolved_text
        # Final fallback: compact form of creator identifier
        if not created_by:
            return "-"
        try:
            label = str(created_by).replace("user_", "")[:8]
            try:
                import os as _os

                if (_os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                    print(
                        f"[owner-debug] created_by={created_by} resolved={resolved_text} derived_user=0 label={label}"
                    )
            except Exception:
                pass
            return label
        except Exception:
            return "-"

    def _format_gpu(self, task: Task) -> str:
        # Be resilient to Mock objects: coerce num_instances to int>0
        num = getattr(task, "num_instances", 1)
        try:
            num = int(num)
            if num <= 0:
                num = 1
        except Exception:
            num = 1
        # Use the configured GPU column width to drive width-aware formatting
        return self.gpu_fmt.format_ultra_compact_width_aware(
            task.instance_type, num, self._gpu_col_width
        )

    def _format_class(self, task: Task) -> str:
        it = (task.instance_type or "").lower()
        try:
            provider_meta = getattr(task, "provider_metadata", {}) or {}
        except Exception:
            provider_meta = {}
        if "sxm" in it:
            return "SXM"
        socket = str(provider_meta.get("socket", "")).lower()
        if "pcie" in it or "pcie" in socket:
            return "PCIe"
        return "-"

    def _format_reservation_columns(self, task: Task) -> tuple[str, str]:
        """Return (Start In, Window) for wide mode when task has reservation metadata."""
        try:
            from datetime import datetime, timezone

            meta = getattr(task, "provider_metadata", {}) or {}
            res = meta.get("reservation")
            if not res:
                return "-", "-"
            st = res.get("start_time") or res.get("start_time_utc")
            et = res.get("end_time") or res.get("end_time_utc")
            start_in = "-"
            if st:
                try:
                    s = str(st).replace("Z", "+00:00")
                    dt = datetime.fromisoformat(s)
                    delta_min = max(0, int((dt - datetime.now(timezone.utc)).total_seconds() // 60))
                    start_in = f"{delta_min}m" if delta_min < 120 else f"{delta_min//60}h"
                except Exception:
                    pass
            window = "-"
            if st and et:
                try:
                    s1 = str(st).replace("Z", "+00:00")
                    s2 = str(et).replace("Z", "+00:00")
                    dt1 = datetime.fromisoformat(s1)
                    dt2 = datetime.fromisoformat(s2)
                    hours = int(round((dt2 - dt1).total_seconds() / 3600))
                    window = f"{hours}h"
                except Exception:
                    pass
            return start_in, window
        except Exception:
            return "-", "-"
