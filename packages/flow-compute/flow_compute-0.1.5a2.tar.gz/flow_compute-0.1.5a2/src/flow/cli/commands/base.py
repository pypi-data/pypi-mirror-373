"""Base command interface for Flow CLI.

Defines the contract for all CLI commands to ensure consistency.

Example implementation:
    class MyCommand(BaseCommand):
        @property
        def name(self) -> str:
            return "mycommand"

        @property
        def help(self) -> str:
            return "Do something useful"

        def get_command(self) -> click.Command:
            @click.command(name=self.name, help=self.help)
            def mycommand():
                console.print("Hello!")
            return mycommand
"""

import os
from abc import ABC, abstractmethod

import click
from rich.markup import escape

from flow.cli.commands.feedback import feedback
from flow.cli.ui.presentation.next_steps import render_next_steps_panel
from flow.cli.utils.theme_manager import theme_manager

console = theme_manager.create_console()


class BaseCommand(ABC):
    """Abstract base for CLI commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name for CLI usage."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help text for the command."""
        pass

    @abstractmethod
    def get_command(self) -> click.Command:
        """Create and return click command."""
        pass

    @property
    def manages_own_progress(self) -> bool:
        """Whether this command manages its own progress display.

        Commands that return True will not have the default "Looking up task..."
        animation shown by the task selector mixin. This prevents flickering
        when commands have their own progress indicators.

        Returns:
            False by default, override to return True if command has custom progress
        """
        return False

    def handle_error(self, error: Exception | str, exit_code: int = 1) -> None:
        """Display error and exit.

        Args:
            error: Exception to display
            exit_code: Process exit code
        """
        # Many FlowError messages already include a formatted "Suggestions:" block.
        # Avoid printing suggestions twice by detecting this case.
        message_text = str(error)

        # Gracefully handle user-initiated cancellation (Ctrl+C/abort)
        try:
            import click as _click

            if (not isinstance(error, str)) and (
                isinstance(error, KeyboardInterrupt) or isinstance(error, _click.Abort)
            ):
                console.print("[dim]Cancelled[/dim]")
                raise _click.exceptions.Exit(130)
        except Exception:
            pass
        # When the caller passed only the stringified exception and it is empty,
        # treat it as a cancelled/aborted prompt instead of showing an error panel.
        if isinstance(error, str) and message_text.strip() == "":
            try:
                import click as _click

                console.print("[dim]Cancelled[/dim]")
                raise _click.exceptions.Exit(130)
            except Exception:
                # As a fallback, exit with 130 without extra output
                raise SystemExit(130)

        # Strong, opinionated routing for auth misconfiguration
        if (
            isinstance(error, ValueError)
            and (
                ("Authentication not configured" in message_text)
                or ("MITHRIL_API_KEY" in message_text)
            )
        ) or ("Authentication not configured" in message_text):
            self.handle_auth_error()
            return

        # Optional JSON error mode for machine-readability (controlled via env)
        try:
            output_mode = os.environ.get("FLOW_CLI_ERRORS", "").strip().lower()
        except Exception:
            output_mode = ""

        if output_mode == "json":
            import json as _json

            payload: dict[str, object] = {
                "error": str(message_text),
            }
            try:
                if hasattr(error, "suggestions") and error.suggestions:
                    payload["suggestions"] = list(error.suggestions)  # type: ignore[arg-type]
            except Exception:
                pass
            try:
                if hasattr(error, "error_code") and error.error_code:
                    payload["error_code"] = error.error_code
            except Exception:
                pass
            try:
                if hasattr(error, "status_code") and error.status_code:
                    payload["status_code"] = error.status_code
            except Exception:
                pass
            try:
                if hasattr(error, "request_id") and error.request_id:
                    payload["request_id"] = error.request_id
            except Exception:
                pass
            console.print(_json.dumps(payload))
            raise click.exceptions.Exit(exit_code)

        # Human-readable error panel
        try:
            subtitle_text = None
            if (
                ("Suggestions:" not in message_text)
                and hasattr(error, "suggestions")
                and error.suggestions
            ):
                # Join suggestions into a compact subtitle; bullets rendered by Feedback
                subtitle_text = "\n".join(str(s) for s in error.suggestions)
            feedback.error(message=escape(message_text), title="Error", subtitle=subtitle_text)
        except Exception:
            from flow.cli.utils.theme_manager import theme_manager as _tm

            console.print(
                f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {escape(message_text)}"
            )

        # Optionally show request/correlation ID if available
        try:
            request_id = getattr(error, "request_id", None)
            if request_id:
                console.print(f"[dim]Request ID:[/dim] {escape(str(request_id))}")
        except Exception:
            pass

        # Display suggestions only if not already embedded in the message
        if (
            ("Suggestions:" not in message_text)
            and hasattr(error, "suggestions")
            and error.suggestions
        ):
            # Already shown in panel subtitle when feedback.error succeeded
            pass

        # Optional diagnostics mode (power users / CI): show structured context
        try:
            if os.environ.get("FLOW_CLI_DIAGNOSTICS", "").strip() in {
                "1",
                "true",
                "TRUE",
                "yes",
                "on",
            }:
                diag: list[str] = []
                try:
                    status_code = getattr(error, "status_code", None)
                    if status_code:
                        diag.append(f"status={status_code}")
                except Exception:
                    pass
                try:
                    request_id = getattr(error, "request_id", None)
                    if request_id:
                        diag.append(f"request_id={request_id}")
                except Exception:
                    pass
                if diag:
                    console.print("[dim]Diagnostics:[/dim] " + ", ".join(escape(s) for s in diag))
        except Exception:
            pass

        # Friendly support guidance for all CLI errors
        try:
            console.print(
                "\n[dim]Need help?[/dim] Email [link]mailto:support@mithril.ai[/link] or ask the team in Slack."
            )
            console.print(
                "[dim]Include the full error and Request ID (if shown). For richer context, re-run with[/dim] "
                "[accent]FLOW_CLI_DIAGNOSTICS=1[/accent] [dim]or[/dim] [accent]FLOW_CLI_ERRORS=json[/accent] [dim]and paste the output.[/dim]"
            )
        except Exception:
            pass

        raise click.exceptions.Exit(exit_code)

    def handle_auth_error(self) -> None:
        """Display top-tier authentication guidance and exit.

        Provides actionable, shell-aware steps and CI-friendly options.
        """
        from flow.cli.utils.theme_manager import theme_manager as _tm

        console.print(
            f"[{_tm.get_color('error')}]Authentication not configured[/{_tm.get_color('error')}]\n"
        )

        console.print("[dim]Quick fixes:[/dim]")
        console.print("  1) Run [accent]flow init[/accent] (recommended interactive setup)")
        console.print("  2) Or set [accent]MITHRIL_API_KEY[/accent] in your environment")

        # Suggest a shell-specific one-liner
        shell = os.environ.get("SHELL", "").lower()
        if "fish" in shell:
            example = 'set -x MITHRIL_API_KEY "fkey_XXXXXXXXXXXXXXXX"'
        elif "powershell" in shell or "pwsh" in shell:
            example = '$env:MITHRIL_API_KEY = "fkey_XXXXXXXXXXXXXXXX"'
        elif os.name == "nt":  # Windows CMD
            example = 'set MITHRIL_API_KEY="fkey_XXXXXXXXXXXXXXXX"'
        else:  # bash/zsh/sh
            example = 'export MITHRIL_API_KEY="fkey_XXXXXXXXXXXXXXXX"'

        console.print(f"     e.g., [accent]{example}[/accent]")

        # Helpful links and non-interactive options
        # Provider-aware hint for obtaining API keys
        try:
            import os as _os

            provider_name = (_os.environ.get("FLOW_PROVIDER") or "mithril").lower()
        except Exception:
            provider_name = "mithril"

        if provider_name == "mithril":
            from flow.utils.links import WebLinks

            console.print(f"\n[dim]Get an API key:[/dim] [link]{WebLinks.api_keys()}[/link]")
        else:
            console.print("\n[dim]Get an API key in your provider's console[/dim]")
        console.print(
            "[dim]CI/non-interactive:[/dim] [accent]flow init --api-key $MITHRIL_API_KEY --yes[/accent]"
        )
        console.print("[dim]Inspect current config:[/dim] [accent]flow init --show[/accent]")

        # Centralized docs links and the new docs command
        try:
            from flow.cli.utils.hyperlink_support import hyperlink_support as _hs
            from flow.utils.links import DocsLinks as _Docs

            doc_url = _Docs.root()
            if _hs.is_supported():
                doc_link = _hs.create_link("Docs", doc_url)
                console.print(
                    f"[dim]Documentation:[/dim] {doc_link}  [dim](or run 'flow docs')[/dim]"
                )
            else:
                console.print(
                    f"[dim]Documentation:[/dim] {doc_url}  [dim](or run 'flow docs')[/dim]"
                )
        except Exception:
            pass

        raise click.exceptions.Exit(1)

    def show_next_actions(
        self, recommendations: list, title: str | None = None, max_items: int | None = None
    ) -> None:
        """Display next action recommendations.

        Args:
            recommendations: List of recommended commands/actions
        """
        if not recommendations:
            return

        # Use shared renderer for consistency with status view
        render_next_steps_panel(
            console,
            [str(r) for r in recommendations],
            title=title or "Next steps",
            max_items=(max_items if isinstance(max_items, int) and max_items > 0 else 3),
        )
