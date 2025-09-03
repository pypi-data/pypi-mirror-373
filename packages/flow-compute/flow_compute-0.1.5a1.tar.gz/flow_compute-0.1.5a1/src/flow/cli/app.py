"""Flow CLI application module.

Main CLI entry point and command registration for Flow.
"""

import os
import sys
import threading
from collections import OrderedDict
from collections.abc import Callable

import click

# Apply console patching early to ensure all Console instances respect settings
from flow.cli.ui.facade import TerminalAdapter
from flow.cli.utils.icons import prefix_with_flow_icon

# Optional: "did you mean" suggestions (no-op if not installed)
try:
    from click_didyoumean import DYMGroup as _DYMGroup
except Exception:  # pragma: no cover - optional dependency
    _DYMGroup = click.Group  # type: ignore

# Optional: Trogon TUI decorator (no-op if not installed)
try:
    from trogon import tui as _tui
except Exception:  # pragma: no cover - optional dependency

    def _tui(*_args, **_kwargs):  # type: ignore
        def _decorator(f):
            return f

        return _decorator


class OrderedGroup(click.Group):
    """Custom Click Group that maintains command order."""

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, click.Command] | None = None,
        **attrs: object,
    ) -> None:
        super().__init__(name, commands, **attrs)
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Return command names preserving insertion order."""
        return list(self.commands.keys())


class OrderedDYMGroup(_DYMGroup):
    """Click Group with insertion-order listing and did-you-mean suggestions."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Return command names preserving insertion order."""
        return list(self.commands.keys())


class LazyDYMGroup(OrderedDYMGroup):
    """Lazy-loading Click Group.

    Stores loader callables for commands and imports them only when invoked.
    Also allows fast help rendering without importing every command.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        # Optional short help map to avoid importing modules on --help
        self._help_summaries: dict[str, str] = {}
        # Optional example map for golden-path usage snippets
        self._examples: dict[str, str] = {}
        # Hidden commands not shown in grouped help
        self._hidden: set[str] = set()
        # Guard against double-loading from concurrent help/resolve
        self._cmd_lock = threading.Lock()

    def add_lazy_command(
        self,
        name: str,
        loader: Callable[[], click.Command | click.Group],
        help_summary: str | None = None,
        example: str | None = None,
        hidden: bool | None = None,
    ) -> None:
        # Store a callable that returns a click.Command when invoked
        self.commands[name] = loader
        if help_summary:
            self._help_summaries[name] = help_summary
        if example:
            self._examples[name] = example
        if hidden:
            self._hidden.add(name)

    def get_command(
        self, ctx: click.Context | None, cmd_name: str
    ) -> click.Command | click.Group | None:
        cmd_obj = self.commands.get(cmd_name)
        if cmd_obj is None:
            return None
        # If it's a callable loader, resolve and replace
        if callable(cmd_obj) and not isinstance(cmd_obj, click.Command):
            with self._cmd_lock:
                # Re-check under lock in case another thread resolved it
                current = self.commands.get(cmd_name)
                if isinstance(current, (click.Command, click.Group)):
                    return current
                try:
                    resolved = cmd_obj()
                    if isinstance(resolved, (click.Command, click.Group)):
                        # Prefix help text for the resolved command and all of its subcommands
                        try:
                            self._prefix_help_recursive(resolved)
                        except Exception:
                            pass
                        self.commands[cmd_name] = resolved
                        return resolved
                except Exception as e:  # pragma: no cover - avoid breaking help
                    # Optionally log in debug mode; hide command from help
                    if os.environ.get("FLOW_DEBUG"):
                        try:
                            sys.stderr.write(
                                f"[flow-debug] failed to load command '{cmd_name}': {e}\n"
                            )
                        except Exception:
                            pass
                    return None
        return cmd_obj

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        # Group commands into lifecycle sections without importing heavy modules
        groups: dict[str, list[str]] = {
            "Getting started": ["init", "docs"],
            "Run": ["run", "dev", "example", "grab"],
            "Observe": ["status", "logs"],
            "Manage": [
                "cancel",
                "ssh",
                "ssh-keys",
                "volumes",
                "mount",
                "upload-code",
                "reservations",
            ],
            "Advanced": ["update", "theme"],
        }

        listed = set()
        for title, names in groups.items():
            rows: list[tuple[str, str]] = []
            for name in names:
                if name not in self.commands or name in self._hidden:
                    continue
                listed.add(name)
                help_text = self._help_summaries.get(name, "")
                example = self._examples.get(name)
                if example:
                    help_text = f"{help_text}  e.g., {example}"
                # Prefix help strings with icon for consistent branding
                rows.append((name, prefix_with_flow_icon(help_text) if help_text else help_text))
            if rows:
                with formatter.section(prefix_with_flow_icon(title)):
                    formatter.write_dl(rows)

        # Any remaining commands not categorized
        remaining = [
            n for n in self.list_commands(ctx) if n not in listed and n not in self._hidden
        ]
        if remaining:
            rows = []
            for name in remaining:
                help_text = self._help_summaries.get(name, "")
                example = self._examples.get(name)
                if example:
                    help_text = f"{help_text}  e.g., {example}"
                rows.append((name, prefix_with_flow_icon(help_text) if help_text else help_text))
            with formatter.section(prefix_with_flow_icon("Other")):
                formatter.write_dl(rows)

    def _prefix_help_recursive(self, cmd: click.Command | click.Group) -> None:
        """Prefix help text with icon for a command and all nested subcommands.

        Works for both click.Command and click.Group trees.
        """
        try:
            help_text = getattr(cmd, "help", None)
            if isinstance(help_text, str) and help_text.strip():
                cmd.help = prefix_with_flow_icon(help_text)
        except Exception:
            pass
        # For Groups, recurse into subcommands
        try:
            if isinstance(cmd, click.Group):
                for sub in getattr(cmd, "commands", {}).values():
                    if isinstance(sub, (click.Command, click.Group)):
                        self._prefix_help_recursive(sub)
        except Exception:
            pass


def print_version(ctx: click.Context, param: click.Option | None, value: bool) -> None:
    """Print version and exit.

    Args:
        ctx: Click context.
        param: Bound option (unused).
        value: Whether the option was provided.
    """
    if not value or ctx.resilient_parsing:
        return
    try:
        from flow._version import get_version

        v = get_version()
    except Exception as e:
        # Do not explode on import issues; offer optional debug
        if os.environ.get("FLOW_DEBUG"):
            try:
                click.echo(f"warning: failed to load version: {e}", err=True)
            except Exception:
                pass
        v = "0.0.0+unknown"
    click.echo(f"flow, version {v}")
    ctx.exit()


def open_pricing(ctx: click.Context, param: click.Option | None, value: bool) -> None:
    """Invoke the pricing command and exit when --pricing is used at root.

    Provides a convenient alias so `flow --pricing` behaves like `flow pricing`.
    """
    if not value or ctx.resilient_parsing:
        return
    try:
        grp = ctx.command
        if isinstance(grp, click.Group):
            cmd = grp.get_command(ctx, "pricing")
            if isinstance(cmd, click.Command):
                # Ensure program name is set for consistent help rendering
                ctx.info_name = ctx.info_name or (sys.argv[0].split("/")[-1] or "flow")
                ctx.invoke(cmd)
                ctx.exit()
    except Exception:
        # Do not fail root CLI if alias resolution has issues
        pass


# TUI decorator is optional; if trogon is unavailable, _tui is a no-op
@_tui()
@click.group(
    cls=LazyDYMGroup,
    context_settings={
        "max_content_width": TerminalAdapter.get_terminal_width(),
        # Add a short help alias for consistency with common CLIs
        "help_option_names": ["-h", "--help"],
    },
    invoke_without_command=True,
)
@click.option(
    "-V",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
@click.option(
    "--pricing",
    is_flag=True,
    callback=open_pricing,
    expose_value=False,
    is_eager=True,
    help="Show pricing info (alias of 'pricing').",
    hidden=True,
)
@click.pass_context
def cli(
    ctx: click.Context,
) -> None:
    """❊ Flow CLI - Submit and manage GPU tasks.

    Flow CLI helps you provision GPU instances/clusters, run workloads from YAML or command,
    and monitor/manage tasks end-to-end.

    \b
    ❊ Quickstart:
      1) flow init                          # Configure API key
      2) flow example gpu-test              # Verify GPU access
      3) flow run 'nvidia-smi'              # Launch a job via command

    \b
    ❊ Core commands:

    \b
      ❊ Setup & dev:
        flow init                   # Configure credentials
        flow dev                    # Persistent dev VM

    \b
      ❊ Run & starters:
        flow run <file.yaml>        # Submit a task from YAML or command
        flow example gpu-test       # GPU check starter
        flow reserve ...            # Reserve capacity (create/list/show)

    \b
      ❊ Observe & manage:
        flow status                 # List and filter tasks
        flow logs <task_id>         # Stream logs
        flow ssh <task_id>          # SSH into a running task
        flow cancel <pattern>       # Cancel by id/name/pattern

    \b
      ❊ Storage:
        flow volumes ...            # Manage persistent volumes
        flow mount ...              # Attach volumes to tasks
        flow upload-code <task_id>  # Sync local code to a running task
        flow ssh-keys ...           # Manage SSH keys

    \b
      ❊ Utilities:
        flow update                 # Update Flow SDK

    \b
    ❊ Power-user tips:
      - Manage themes via 'flow theme' (e.g., flow theme list; flow theme set modern)
      - Enable completion: run 'flow completion install' for your shell
      - FLOW_TELEMETRY=1 to write JSONL usage metrics locally and improve defaults over time
      - Configure credentials via 'flow init'
    """
    # Mark origin as CLI for this process (does not override explicit env)
    try:
        from flow.cli.utils.origin import set_cli_origin_env

        set_cli_origin_env()
    except Exception:
        pass

    # Set up theme and hyperlink preferences
    import os

    # Kick off non-blocking background prefetch early for UX wins
    # Avoid skewing unit tests and non-interactive sessions with extra API calls
    try:
        # Auto-simple mode: in CI or non-TTY, default to quiet/no animations
        try:
            is_ci = bool(os.environ.get("CI"))
            if (not sys.stdout.isatty()) or is_ci:
                if os.environ.get("FLOW_NO_ANIMATION", "").strip() == "":
                    os.environ["FLOW_NO_ANIMATION"] = "1"
                # Disable prefetch unless user explicitly opted in
                if os.environ.get("FLOW_PREFETCH", "").strip() == "":
                    os.environ["FLOW_PREFETCH"] = "0"
        except Exception:
            pass
        # Respect explicit opt-out
        if os.environ.get("FLOW_PREFETCH", "1").strip() not in {"0", "false", "no"}:
            # Only prefetch when attached to a TTY and not under pytest
            if sys.stdout.isatty() and os.environ.get("PYTEST_CURRENT_TEST", "") == "":
                # Local import to avoid import cycles during CLI bootstrap
                from flow.cli.utils.prefetch import start_prefetch_for_command

                start_prefetch_for_command()
    except Exception:
        # Best-effort; never block or fail CLI startup due to prefetch
        pass

    # Demo mode disabled for initial release
    # try:
    #     from flow.cli.utils.mode import load_persistent_demo_env
    #     load_persistent_demo_env()
    # except Exception:
    #     pass

    # Store settings in context for child commands
    ctx.ensure_object(dict)

    # If no subcommand was provided, show help instead of erroring.
    # Help output will use any persisted theme (config) or FLOW_THEME env if set.
    if ctx.invoked_subcommand is None:
        # Ensure help reflects the invoked name (flow or flow-compute)
        ctx.info_name = ctx.info_name or (sys.argv[0].split("/")[-1] or "flow")
        click.echo(ctx.get_help())
        ctx.exit(0)


def setup_cli() -> click.Group:
    """Set up the CLI by registering all available commands.

    This function discovers and registers all command modules with the
    main CLI group. It supports both individual commands and command groups.

    Returns:
        The configured CLI group with all commands registered.

    Raises:
        TypeError: If a command module returns an invalid command type.
    """

    # Register lazy loaders to avoid importing all command modules at startup
    # Helper to create a loader for a module
    def _loader(mod_name: str):
        def _load():
            from importlib import import_module

            module = import_module(f"flow.cli.commands.{mod_name}")
            return module.command.get_command()

        return _load

    # Lightweight "coming soon" stubs for deferred commands
    def _coming_soon_loader(cmd_name: str, note: str | None = None):
        def _load():
            @click.command(
                name=cmd_name, help="This feature will be available in an upcoming release"
            )
            def _cmd() -> None:
                msg = f"Coming soon: '{cmd_name}'."
                if note:
                    msg += f" {note}"
                click.echo(msg)

            return _cmd

        return _load

    # Register commands from centralized manifest
    try:
        from flow.cli.command_manifest import COMMANDS

        if isinstance(cli, LazyDYMGroup):
            for spec in COMMANDS:
                try:
                    cli.add_lazy_command(
                        spec.name,
                        _loader(spec.module),
                        spec.summary,
                        spec.example,
                        spec.hidden or None,
                    )
                except Exception:
                    # Skip broken/optional commands silently
                    pass
    except Exception:
        # If manifest is unavailable for any reason, fail soft (commands may be incomplete)
        pass

    # Register command aliases (hidden in help) ---------------------------------
    def _alias_loader(alias_name: str, target_mod_name: str):
        def _load():
            from importlib import import_module as _import_module

            import click as _click

            try:
                module = _import_module(f"flow.cli.commands.{target_mod_name}")
                base_cmd = module.command.get_command()
            except Exception:
                return None

            @_click.command(
                name=alias_name,
                help=getattr(base_cmd, "help", None),
                context_settings=getattr(base_cmd, "context_settings", None),
                params=getattr(base_cmd, "params", None),
                epilog=getattr(base_cmd, "epilog", None),
                short_help=getattr(base_cmd, "short_help", None),
                add_help_option=getattr(base_cmd, "add_help_option", True),
            )
            @_click.pass_context
            def _alias(ctx: _click.Context, **kwargs):  # type: ignore[no-redef]
                return ctx.invoke(base_cmd, **kwargs)

            # Clarify that this is an alias in help text while preserving options
            try:
                if isinstance(_alias.help, str) and _alias.help.strip():
                    _alias.help = f"{_alias.help}\n\nAlias of '{base_cmd.name}'."
            except Exception:
                pass

            return _alias

        return _load

    try:
        if isinstance(cli, LazyDYMGroup):
            from flow.cli.command_manifest import ALIASES

            for alias_spec in ALIASES:
                if cli.commands.get(alias_spec.alias) is None:
                    try:
                        cli.add_lazy_command(
                            alias_spec.alias,
                            _alias_loader(alias_spec.alias, alias_spec.target_module),
                            alias_spec.summary or "",
                            alias_spec.example,
                            alias_spec.hidden,
                        )
                    except Exception:
                        pass
    except Exception:
        pass

    # Register hidden stubs for deferred commands so invoking them prints a friendly message
    try:
        if isinstance(cli, LazyDYMGroup):
            from flow.cli.command_manifest import STUBS

            for stub in STUBS:
                if cli.commands.get(stub.name) is None:
                    try:
                        cli.add_lazy_command(
                            stub.name,
                            _coming_soon_loader(stub.name, stub.note),
                            stub.summary,
                            None,
                            stub.hidden,
                        )
                    except Exception:
                        pass
    except Exception:
        pass

    return cli


def create_cli() -> click.Group:
    """Create the CLI without triggering heavy imports at module import time.

    This defers command registration until runtime, so invocations like
    `flow --version` do not import every command module.
    """
    cli_group = setup_cli()

    # Enable automatic shell completion (optional dependency)
    try:
        from auto_click_auto import enable_click_shell_completion
        from auto_click_auto.constants import ShellType

        # Enable completion for both aliases by program name detection. When the CLI
        # is invoked as `flow-compute`, Click will use that as the program name, and
        # completion still works. We set the default to "flow" for generation.
        enable_click_shell_completion(
            program_name="flow",
            shells={ShellType.BASH, ShellType.ZSH, ShellType.FISH},
        )
    except ImportError:
        # auto-click-auto not installed, fall back to manual completion
        pass

    return cli_group


def main() -> int:
    """Entry point for the Flow CLI application.

    This function provides a unified interface on top of single-responsibility
    command modules, orchestrating all CLI commands through a central entry point.

    Returns:
        Exit code from the CLI execution.
    """
    # Initialize centralized logging from YAML (idempotent, respects env)
    try:
        from flow.utils.logging_config import initialize_logging

        # Only initialize when explicitly requested or when running CLI (default True here)
        # This avoids affecting host apps when Flow is imported as a library.
        if os.environ.get("FLOW_LOG_INIT", "1") == "1":
            initialize_logging()
    except Exception:
        # Never fail CLI due to logging setup
        pass

    # Fast-path version without building CLI or importing commands
    argv = sys.argv[1:]
    if any(a in ("--version", "-V") for a in argv):
        try:
            from flow._version import get_version as _get_version

            v = _get_version()
        except Exception:
            v = "0.0.0+unknown"
        import click as _click

        _click.echo(f"flow, version {v}")
        return 0

    # Quick config check on startup (now disabled by default; enable by setting FLOW_SKIP_CONFIG_CHECK=0)
    if os.environ.get("FLOW_SKIP_CONFIG_CHECK") == "0":
        # Only check for commands that need config (not init, help, etc)
        if len(sys.argv) > 1 and sys.argv[1] not in ["init", "--help", "-h", "--version"]:
            try:
                # Try to load config without auto_init to see if it's configured
                from flow.application.config.config import Config

                Config.from_env(require_auth=True)
            except ValueError:
                # Config missing - provide helpful guidance
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print("[warning]⚠ Flow SDK is not configured[/warning]\n")
                console.print("To get started, run: [accent]flow init[/accent]")
                console.print("Or set MITHRIL_API_KEY environment variable\n")
                # Documentation link (with hyperlink support when available)
                try:
                    from flow.cli.utils.hyperlink_support import hyperlink_support as _hs
                    from flow.utils.links import DocsLinks as _Docs

                    docs_url = _Docs.root()
                    if _hs.is_supported():
                        docs_link = _hs.create_link("Docs", docs_url)
                        console.print(
                            f"Documentation: {docs_link}  [dim](or run 'flow docs')[/dim]"
                        )
                    else:
                        console.print(f"Documentation: {docs_url}  [dim](or run 'flow docs')[/dim]")
                except Exception:
                    pass
                console.print("For help: [dim]flow --help[/dim]")
                return 1

    cli_group = create_cli()

    # Opt-in usage telemetry wrapper
    try:
        from flow.cli.utils.telemetry import Telemetry

        telemetry = Telemetry()
        if telemetry.enabled:
            # Command name is first argv or "help"
            cmd_name = sys.argv[1] if len(sys.argv) > 1 else "help"
            with telemetry.track_command(cmd_name):
                return cli_group()
        else:
            return cli_group()
    except Exception:
        # Never fail due to telemetry
        return cli_group()


if __name__ == "__main__":
    cli()

# Ensure subcommands are registered when this module is imported so that
# tests importing `cli` directly can invoke subcommands without calling
# create_cli()/setup_cli() explicitly.
try:
    # Safe to call multiple times; loaders are lightweight and idempotent
    setup_cli()
    # Eagerly ensure 'example' is available even if lazy registration fails in some environments
    try:
        if "example" not in cli.commands or not isinstance(
            cli.get_command(None, "example"), click.Command
        ):
            from flow.cli.commands import example as _example_mod  # type: ignore

            cmd = _example_mod.command.get_command()
            if isinstance(cmd, click.Command):
                cli.add_command(cmd, name="example")
    except Exception:
        pass
except Exception:
    # Never block import due to optional/missing commands in certain envs
    pass
