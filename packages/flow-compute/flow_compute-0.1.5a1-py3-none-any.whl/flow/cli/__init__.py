"""CLI package for the `flow` command.

Provides the interactive and non-interactive command-line interface over the
Application layer. The CLI should be a thin wrapper: parse inputs, call
use-cases, print results. Keep business logic in ``flow.application``.

Structure:
  - ``commands``: user-facing commands and options
  - ``services``: non-UI helpers used by commands
  - ``utils``/``ui``: presentation helpers and TUI bits
"""

import sys
from pathlib import Path

# Legacy import aliasing removed in favor of canonical imports


def main():
    """Entry point for the CLI."""
    # Check Python version before importing anything that uses modern syntax
    if sys.version_info < (3, 10):
        print(
            f"Error: Flow SDK requires Python 3.10 or later. "
            f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.\n\n"
            f"Recommended: Install and use 'uv' for automatic Python version management:\n"
            f"  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            f"  uv tool install flow-compute\n\n"
            f"Or install without uv:\n"
            f"  pipx install flow-compute\n"
            f"  # macOS/Linux one-liner: curl -fsSL https://raw.githubusercontent.com/mithrilcompute/flow/main/scripts/install.sh | sh\n\n"
            f"Alternative: Upgrade your Python installation to 3.10 or later.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # Import after version check
    # Hide the terminal caret in interactive UIs (prompt_toolkit respects this)
    try:
        import os as _os

        _os.environ.setdefault("PROMPT_TOOLKIT_HIDE_CURSOR", "1")
    except Exception:
        pass

    from flow.cli.app import create_cli

    cli_group = create_cli()

    # Use the invoked executable name (e.g., "flow" or "flow-compute") for help/output,
    # but fall back to "flow" when run via `python -m` or other launchers.
    try:
        invoked_name = Path(sys.argv[0]).name
        if not invoked_name or invoked_name.startswith("python"):
            invoked_name = "flow"
    except Exception:
        invoked_name = "flow"

    cli_group(prog_name=invoked_name)


__all__ = ["main"]
