"""Docs command for Flow CLI.

Provides quick access to documentation links sourced from centralized
link definitions in `flow.utils.links`. Keeps URLs consistent across the
codebase and allows terminals with hyperlink support to render
clickable links.
"""

from __future__ import annotations

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.hyperlink_support import hyperlink_support
from flow.cli.utils.theme_manager import theme_manager


class DocsCommand(BaseCommand):
    """Show documentation links."""

    @property
    def name(self) -> str:
        return "docs"

    @property
    def help(self) -> str:
        return "Show links to the Flow/Mithril documentation"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option(
            "--verbose",
            "verbose",
            is_flag=True,
            help="Show additional popular documentation links",
        )
        def docs(verbose: bool) -> None:
            """Print documentation links from the centralized link module."""
            from flow.utils.links import DocsLinks  # Local import to avoid early import cycles

            def link(label: str, url: str) -> str:
                try:
                    if hyperlink_support.is_supported():
                        return hyperlink_support.create_link(label, url)
                except Exception:
                    pass
                return f"{label}: {url}"

            accent = theme_manager.get_color("accent")
            console.print(f"[bold {accent}]Flow Documentation[/bold {accent}]")

            # Root docs
            console.print(link("Docs", DocsLinks.root()))

            # Common starting points (keep compute quickstart only)

            if verbose:
                # Popular deep links when requested
                try:
                    console.print(link("Compute quickstart", DocsLinks.compute_quickstart()))
                except Exception:
                    pass
                try:
                    console.print(link("Spot bids", DocsLinks.spot_bids()))
                except Exception:
                    pass
                try:
                    console.print(
                        link("Spot auction mechanics", DocsLinks.spot_auction_mechanics())
                    )
                except Exception:
                    pass
                try:
                    console.print(link("Startup scripts", DocsLinks.startup_scripts()))
                except Exception:
                    pass
                # Replace regions with ephemeral storage and add persistent storage
                try:
                    console.print(link("Ephemeral storage", DocsLinks.ephemeral_storage()))
                except Exception:
                    pass
                try:
                    console.print(link("Persistent storage", DocsLinks.persistent_storage()))
                except Exception:
                    pass

            # Hint when not verbose
            if not verbose:
                from flow.cli.ui.presentation.next_steps import (
                    render_next_steps_panel as _render_ns,
                )

                _render_ns(console, ["flow docs --verbose"], title="Next Steps")

        return docs


# Export command instance
command = DocsCommand()
