from __future__ import annotations

"""UI rendering helpers for the setup wizard.

This module focuses on presentation (Rich Panels/Tables) and avoids any API calls.
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flow.cli.ui.presentation.visual_constants import (
    DENSITY,
    SPACING,
    format_text,
    get_colors,
    get_panel_styles,
    get_status_display,
)
from flow.cli.utils.theme_manager import theme_manager
from flow.core.setup_adapters import ProviderSetupAdapter
from flow.sdk.helpers.masking import mask_strict_last4


class AnimatedDots:
    """Minimal animated dots implementation for progress messages."""

    def __init__(self) -> None:
        self._counter = 0
        self._dots = ["", ".", "..", "..."]

    def next(self) -> str:
        dots = self._dots[self._counter % len(self._dots)]
        self._counter += 1
        return dots


def build_selector_header(adapter: ProviderSetupAdapter, existing_config: dict[str, Any]) -> str:
    try:
        fields = adapter.get_configuration_fields()
        missing_required: list[str] = []
        for f in fields:
            if not getattr(f, "required", False):
                continue
            if existing_config.get(f.name) in (None, ""):
                missing_required.append(f.display_name or f.name.replace("_", " ").title())
        if missing_required:
            missing_str = ", ".join(missing_required)
            return f"<b>Missing</b>: {missing_str}"
        return ""
    except Exception:
        return ""


class UIRenderer:
    """Handles rendering of UI components for the setup wizard."""

    def __init__(self, console: Console):
        self.console = console
        self._shown_demo_panel: bool = False

    def render_welcome(self, adapter: ProviderSetupAdapter) -> None:
        self.console.clear()
        colors = get_colors()
        panel_styles = get_panel_styles()
        title, features = adapter.get_welcome_message()
        welcome_content = (
            f"{format_text('title', 'Flow SDK Setup')}\n\n"
            f"{format_text('muted', f'Configure your environment for GPU workloads on {adapter.get_provider_name().upper()}')}\n\n"
            f"{format_text('body', 'This wizard will:')}\n"
        )
        for feature in features:
            welcome_content += f"  [{colors['primary']}]◦[/{colors['primary']}] {feature}\n"
        self.console.print(
            Panel(
                welcome_content.rstrip(),
                title=f"{format_text('title', '❊ Flow')}",
                title_align=panel_styles["main"]["title_align"],
                border_style=panel_styles["main"]["border_style"],
                padding=panel_styles["main"]["padding"],
                width=SPACING["panel_width"],
            )
        )
        self.console.print()
        try:
            if str(adapter.get_provider_name()).lower() == "mock":
                panel = self._create_demo_mode_panel()
                self.console.print(panel)
                self.console.print()
                self._shown_demo_panel = True
        except Exception:
            pass

    def render_completion(self, adapter: ProviderSetupAdapter) -> None:
        self.console.print("\n" + "─" * 50)
        completion_message = adapter.get_completion_message()
        billing_reminder = ""
        if hasattr(adapter, "billing_not_configured") and adapter.billing_not_configured:
            link_color = theme_manager.get_color("link")
            from flow.utils.links import WebLinks

            billing_link = WebLinks.billing_settings()
            billing_reminder = (
                "\n\n[warning]Remember to configure billing to use GPU resources:[/warning]\n"
                f"[{link_color}]{billing_link}[/{link_color}]"
            )
        colors = get_colors()
        panel_styles = get_panel_styles()
        self.console.print(
            Panel(
                f"{format_text('success', completion_message)}\n\n"
                f"{format_text('body', 'Your configuration is ready for GPU workloads.')}\n"
                f"{format_text('muted', 'All credentials are securely stored and verified.')}"
                f"{billing_reminder}",
                title=f"{format_text('success', '✓ Success')}",
                title_align=panel_styles["success"]["title_align"],
                border_style=panel_styles["success"]["border_style"],
                padding=panel_styles["success"]["padding"],
                width=SPACING["panel_width"],
            )
        )

    def render_status_panel(
        self, content: Table, adapter: ProviderSetupAdapter, *, show_demo_hint: bool = False
    ) -> None:
        panel_styles = get_panel_styles()
        try:
            from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter as _TA

            term_w = _TA.get_terminal_width()
            desired_w = SPACING.get("panel_width", 60)
            panel_w = min(max(56, desired_w), max(40, term_w - 4))
        except Exception:
            panel_w = SPACING.get("panel_width", 60)
        self.console.print(
            Panel(
                content,
                title=f"{format_text('title', 'Configuration Status')}",
                title_align=panel_styles["secondary"]["title_align"],
                border_style=panel_styles["secondary"]["border_style"],
                padding=panel_styles["secondary"]["padding"],
                width=panel_w,
            )
        )

        try:
            import shutil as _shutil

            term_lines = _shutil.get_terminal_size().lines or 24
            if term_lines >= 22:
                self.console.print()
        except Exception:
            pass

        try:
            if (
                show_demo_hint
                and str(adapter.get_provider_name()).lower() == "mock"
                and not getattr(self, "_shown_demo_panel", False)
            ):
                self.console.print()
                self.console.print(self._create_demo_mode_panel())
                self._shown_demo_panel = True
        except Exception:
            pass

        try:
            if str(adapter.get_provider_name()).lower() != "mock":
                from flow.utils.links import WebLinks

                colors = get_colors()
                bullet = f"[{colors['primary']}]•[/{colors['primary']}]"
                ssh_lines = [
                    f"{bullet} [bold]Default SSH Key[/bold] lets you securely log into instances",
                    f"{bullet} Generate on Mithril (recommended) or use an existing",
                    f"{bullet} Generated private keys are saved to [accent]~/.flow/keys/[/accent]",
                    f"{bullet} More details: [accent]flow init --verbose[/accent]",
                    f"{bullet} Manage keys: [link]{WebLinks.ssh_keys()}[/link]",
                ]
                self.console.print(
                    Panel(
                        "\n".join(ssh_lines),
                        title=f"{format_text('subtitle', 'SSH ACCESS')}",
                        title_align=panel_styles["secondary"]["title_align"],
                        border_style=panel_styles["secondary"]["border_style"],
                        padding=panel_styles["secondary"]["padding"],
                        width=panel_w,
                    )
                )
        except Exception:
            pass

    def build_status_table(
        self,
        adapter: ProviderSetupAdapter,
        existing_config: dict[str, Any],
        session_config: dict[str, Any],
        validation_cache: dict[str, tuple[str, bool]],
        recently_updated: set[str],
    ) -> Table:
        colors = get_colors()
        fields = adapter.get_configuration_fields()
        row_vpad = 1 if getattr(DENSITY, "table_row_vpad", 0) > 0 else 0
        table = Table(show_header=True, box=None, padding=(row_vpad, 2))
        try:
            from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter as _TA

            term_w_for_table = _TA.get_terminal_width()
        except Exception:
            term_w_for_table = 100
        show_source_col = term_w_for_table >= 80
        table.add_column("Component", style=colors["accent"], min_width=15, justify="left")
        table.add_column("Status", min_width=12, justify="left")
        table.add_column("Value", style=colors["muted"], min_width=18, justify="left")
        if show_source_col:
            table.add_column("Source", style=colors["muted"], min_width=8, justify="left")

        required_fields = [f for f in fields if f.required]
        optional_fields = [f for f in fields if not f.required]
        numbered_fields = required_fields + optional_fields

        for idx, field in enumerate(numbered_fields):
            value = session_config.get(field.name, existing_config.get(field.name))
            status_display = None
            display_value = "[dim]—[/dim]"
            source_display = "[dim]—[/dim]"

            if value:
                if field.name == "api_key":
                    cache = validation_cache.get("api_key")
                    is_valid = cache[1] if cache and cache[0] == str(value) else False
                    if is_valid:
                        status_display = get_status_display(
                            "configured", "Verified", icon_style="check"
                        )
                    else:
                        status_display = get_status_display(
                            "invalid", "Invalid", icon_style="check"
                        )
                    try:
                        display_value = mask_strict_last4(str(value))
                    except Exception:
                        display_value = "••••"
                    source_display = "detected"
                elif field.name == "default_ssh_key":
                    # Do not call API here; show as configured and echo value
                    status_display = get_status_display(
                        "configured", "Configured", icon_style="check"
                    )
                    display_value = str(value)
                    source_display = "detected"
                else:
                    status_display = get_status_display(
                        "configured", "Configured", icon_style="check"
                    )
                    if getattr(field, "mask_display", False) and value:
                        display_value = mask_strict_last4(value)
                    else:
                        try:
                            from flow.cli.ui.presentation.terminal_adapter import (
                                TerminalAdapter as _TA,
                            )

                            term_w = _TA.get_terminal_width()
                            budget = max(12, min(30, term_w // 3))
                            display_value = _TA.intelligent_truncate(
                                str(value), budget, priority="middle"
                            )
                        except Exception:
                            display_value = str(value)
                    source_display = "detected"
            else:
                if field.required:
                    status_display = get_status_display("missing", "Missing", icon_style="check")
                else:
                    status_display = get_status_display("optional", "Optional", icon_style="check")
                display_value = "[dim]—[/dim]"
                source_display = "[dim]—[/dim]"

            display_name = field.display_name or field.name.replace("_", " ").title()

            if field.name in recently_updated and display_value and "[dim]" not in display_value:
                try:
                    success_color = theme_manager.get_color("success")
                    display_value = f"[{success_color}]{display_value}[/{success_color}]"
                except Exception:
                    pass
            if show_source_col:
                table.add_row(display_name, status_display, display_value, source_display)
            else:
                table.add_row(display_name, status_display, display_value)

        return table

    def _create_demo_mode_panel(self) -> Panel:
        from flow.utils.links import WebLinks

        colors = get_colors()
        panel_styles = get_panel_styles()
        bullet = f"[{colors['primary']}]•[/{colors['primary']}]"
        body_lines = [
            f"{bullet} [bold]Sandbox only — no real resources are created.[/bold]",
            f"{bullet} Provider: [accent]mock[/accent]",
            f"{bullet} Switch to real: [accent]flow init --provider mithril[/accent] or [accent]flow demo stop[/accent]",
            f"{bullet} SSH access: Your [bold]default SSH key[/bold] lets you securely log in",
            f"{bullet} Manage keys: [link]{WebLinks.ssh_keys()}[/link]",
        ]
        return Panel(
            "\n".join(body_lines),
            title=f"{format_text('subtitle', 'DEMO MODE')}",
            title_align=panel_styles["info"]["title_align"],
            border_style=theme_manager.get_color("warning"),
            padding=panel_styles["info"]["padding"],
            width=SPACING["panel_width"],
        )
