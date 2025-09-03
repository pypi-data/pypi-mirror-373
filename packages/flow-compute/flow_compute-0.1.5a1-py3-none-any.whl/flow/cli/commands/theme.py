"""Theme management commands for Flow CLI.

Provides commands to set, get, and list CLI color themes, persisting the
selection to ~/.flow/config.yaml for future sessions.
"""

import os
from pathlib import Path

import click
import yaml

from flow.cli.commands.base import BaseCommand
from flow.cli.ui.components import (
    InteractiveSelector,
    SelectionItem,
)
from flow.cli.ui.components import (
    map_rich_to_prompt_toolkit_color as _map_rich_to_prompt_toolkit_color,
)
from flow.cli.utils.theme_manager import theme_manager


def _read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    try:
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


class ThemeCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "theme"

    @property
    def help(self) -> str:
        return "Manage CLI color themes (set, get, list)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def theme_group() -> None:
            pass

        @theme_group.command("list", help="List available themes")
        def list_cmd() -> None:
            console = theme_manager.create_console()
            names = theme_manager.list_themes()
            console.print("Available themes:\n  - " + "\n  - ".join(names))

        @theme_group.command("get", help="Show the currently configured theme")
        def get_cmd() -> None:
            console = theme_manager.create_console()
            current = theme_manager.current_theme_name or theme_manager.detect_terminal_theme()
            console.print(f"Current theme: [accent]{current}[/accent]")

        @theme_group.command("set", help="Persist a default theme (overrides auto-detect)")
        @click.argument("name", required=True)
        def set_cmd(name: str) -> None:
            console = theme_manager.create_console()
            # Validate theme name
            available = set(theme_manager.list_themes())
            if name not in available:
                raise click.BadParameter(
                    f"Unknown theme '{name}'. Use 'flow theme list' to see options."
                )

            config_path = Path.home() / ".flow" / "config.yaml"
            cfg = _read_config(config_path)
            cfg["theme"] = name
            _write_config(config_path, cfg)

            # Apply immediately in this process too
            theme_manager.load_theme(name)
            console.print(f"Saved default theme: [accent]{name}[/accent]")

        @theme_group.command("clear", help="Remove persisted theme and return to auto-detect")
        def clear_cmd() -> None:
            console = theme_manager.create_console()
            config_path = Path.home() / ".flow" / "config.yaml"
            cfg = _read_config(config_path)
            if "theme" in cfg:
                cfg.pop("theme", None)
                _write_config(config_path, cfg)
                console.print("Cleared persisted theme. Using auto-detect.")
            else:
                console.print("No persisted theme set. Using auto-detect.")

        # Note: previously had alias `unset`; removed to avoid duplicate ways.

        @theme_group.command("choose", help="Interactively choose a theme with live preview")
        def choose_cmd() -> None:
            console = theme_manager.create_console()
            # Force interactive selector by default, matching setup wizard behavior
            # Users can still disable with FLOW_NONINTERACTIVE=1
            os.environ.setdefault("FLOW_FORCE_INTERACTIVE", "true")

            # Build items from available themes
            names = theme_manager.list_themes()

            # Helper to obtain theme color dict without mutating global state
            def _get_theme_colors(theme_name: str) -> dict[str, str]:
                try:
                    if theme_name in theme_manager.THEMES:  # type: ignore[attr-defined]
                        return theme_manager.THEMES[theme_name].colors  # type: ignore[attr-defined]
                    # Attempt to load a custom theme file non-destructively
                    try:
                        custom = theme_manager._load_custom_theme(theme_name)  # type: ignore[attr-defined]
                        if custom:
                            return custom.colors
                    except Exception:
                        pass
                except Exception:
                    pass
                # Fallback to current theme colors
                try:
                    return (theme_manager.current_theme or theme_manager.load_theme()).colors
                except Exception:
                    return {}

            # Minimal HTML builder (prompt_toolkit subset)
            def _style(text: str, fg: str | None = None, bg: str | None = None) -> str:
                attrs: list[str] = []
                if fg:
                    attrs.append(f"fg='{fg}'")
                if bg:
                    attrs.append(f"bg='{bg}'")
                if attrs:
                    return f"<style {' '.join(attrs)}>{text}</style>"
                return text

            # Reduce composite rich style strings like "underline #2563EB" to a color token
            def _primary_color_token(value: str | None) -> str | None:
                if not value:
                    return None
                try:
                    parts = [p for p in str(value).split() if p]
                    # Prefer a hex token if present
                    for p in parts:
                        if p.startswith("#"):
                            return p
                    # Otherwise last token is typically the color name
                    return parts[-1]
                except Exception:
                    return value

            # Preview renderer for selector
            def render_preview(item: SelectionItem[str]) -> str:
                colors = _get_theme_colors(item.value)
                # Map Rich colors to prompt_toolkit equivalents
                default = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("default", "white")) or "white"
                )
                muted = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("muted", "bright_black")) or "bright_black"
                )
                accent = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("accent", "cyan")) or "cyan"
                )
                link = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("link", colors.get("accent", "cyan"))) or accent
                )
                success = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("success", "green")) or "green"
                )
                warning = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("warning", "yellow")) or "yellow"
                )
                error = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("error", "red")) or "red"
                )
                border = _map_rich_to_prompt_toolkit_color(
                    _primary_color_token(colors.get("border", muted)) or muted
                )
                sel_bg = (
                    _map_rich_to_prompt_toolkit_color(
                        _primary_color_token(colors.get("selected_bg", None)) or "bright_black"
                    )
                    if colors.get("selected_bg")
                    else None
                )
                sel_fg = (
                    _map_rich_to_prompt_toolkit_color(
                        _primary_color_token(colors.get("selected_fg", None)) or "white"
                    )
                    if colors.get("selected_fg")
                    else None
                )

                lines: list[str] = []
                lines.append(_style(f"<b>Flow Theme: {item.value}</b>", fg=default))
                lines.append("")
                lines.append(_style("accent", fg=accent) + "  " + _style("link", fg=link))
                lines.append(
                    _style("success", fg=success)
                    + "  "
                    + _style("warning", fg=warning)
                    + "  "
                    + _style("error", fg=error)
                )
                lines.append(_style("muted caption", fg=muted))
                # Selected row sample
                sel_sample = _style("▸ selected row", fg=(sel_fg or default), bg=(sel_bg or border))
                lines.append(sel_sample)
                # Border rule
                try:
                    rule = "" + ("─" * 38)
                except Exception:
                    rule = "--------------------------------------"
                lines.append(_style(rule, fg=border))
                return "\n".join(lines)

            def theme_to_selection(name: str) -> SelectionItem[str]:
                return SelectionItem(
                    value=name,
                    id=name,
                    title=name,
                    subtitle=None,
                    status=None,
                )

            selector = InteractiveSelector(
                items=names,
                item_to_selection=theme_to_selection,
                title="Select Theme",
                allow_multiple=False,
                allow_back=False,
                show_preview=True,
                preview_renderer=render_preview,
            )

            result = selector.select()
            if result is None or not isinstance(result, str):
                return

            # Persist and apply
            name = result
            available = set(theme_manager.list_themes())
            if name not in available:
                console.print(f"[error]Unknown theme '{name}'[/error]")
                return
            config_path = Path.home() / ".flow" / "config.yaml"
            cfg = _read_config(config_path)
            cfg["theme"] = name
            _write_config(config_path, cfg)
            theme_manager.load_theme(name)
            console.print(f"Using theme: [accent]{name}[/accent]")

        return theme_group


# Export command instance
command = ThemeCommand()
