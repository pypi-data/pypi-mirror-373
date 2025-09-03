"""Provider support messaging helpers for consistent CLI UX.

Centralizes "provider not supported" guidance so commands can emit clear,
actionable messages with consistent styling.
"""

from __future__ import annotations

from collections.abc import Iterable

from flow.cli.commands.base import console
from flow.cli.utils.theme_manager import theme_manager


def print_provider_not_supported(feature: str, *, tips: Iterable[str] | None = None) -> None:
    """Print a standardized provider-not-supported message.

    Args:
        feature: Human-readable feature name (e.g., "remote operations", "reservations").
        tips: Optional iterable of follow-up suggestions.
    """
    err = theme_manager.get_color("error")
    console.print(f"[{err}]Error:[/{err}] Provider does not support {feature} in this environment.")
    try:
        from flow.cli.commands.base import BaseCommand

        if tips:
            BaseCommand().show_next_actions(list(tips))
        else:
            BaseCommand().show_next_actions(
                [
                    "Switch provider: [accent]flow init --provider mithril[/accent]",
                    "See docs: [accent]flow docs[/accent]",
                ]
            )
    except Exception:
        pass


__all__ = ["print_provider_not_supported"]
