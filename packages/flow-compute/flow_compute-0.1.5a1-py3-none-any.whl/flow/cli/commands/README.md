# Flow CLI Commands

This directory contains modular Flow CLI commands. Each command lives in its own file and follows a consistent Click-based pattern with shared styling and error handling.

## Quick Guide: Add a Command

1) Create a module: `src/flow/cli/commands/mycmd.py`

2) Implement the pattern and export `command`:
```python
import click
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.error_handling import cli_error_guard

class MyCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "mycmd"  # CLI name; use hyphens for multi-word (e.g., "ssh-keys")

    @property
    def help(self) -> str:
        return "Short human help shown in `flow --help`"

    def get_command(self) -> click.Command:
        # Keep heavy imports inside function/callbacks to keep CLI startup fast
        @click.command(name=self.name, help=self.help)
        @click.option("--flag", is_flag=True, help="Example flag")
        @cli_error_guard(self)  # Unified error handling & auth guidance
        def mycmd(flag: bool):
            console.print("Hello from mycmd")
        return mycmd

command = MyCommand()
```

3) Register it lazily for top-level CLI exposure in `src/flow/cli/app.py` (inside `setup_cli()`):
```python
# (cli_name, module_name, help_summary, example)
lazy_commands.append(("mycmd", "mycmd", "What it does", "flow mycmd --flag"))
```

4) Optional: categorize it in grouped help. In `LazyDYMGroup.format_commands`, add the CLI name (e.g., `"mycmd"`) under a relevant section (Run/Observe/Manage/Advanced) or it will appear under “Other”.

5) Optional: if your CLI name uses a hyphen, keep the module underscored and map it, e.g. `( "ssh-keys", "ssh_keys", ... )`.

## Command Rules & Patterns

- Click: return a `click.Command` or `click.Group` from `get_command()`; export `command = <YourCommand>()`.
- Errors: decorate the Click callback with `@cli_error_guard(self)`; call `self.handle_error(...)` or raise `flow.errors.FlowError` subclasses with `suggestions` to surface guidance. Auth issues should call `self.handle_auth_error()`.
- Imports: avoid heavy imports or API calls at module import time. Import the SDK/client and other heavy modules inside `get_command()` or inside the callback.
- Output: use the theme-aware `console` (from `base`) instead of `print`; for panels, use `flow.cli.commands.feedback.feedback`.
- Progress: if your command renders its own progress UI, override `manages_own_progress = True` on your class to suppress default spinners from mixins.
- Completion: wire `shell_complete=...` to helpers from `flow.cli.utils.shell_completion` for args/options where relevant.
- JSON mode: where it makes sense, provide a `--json` flag. Also be mindful that users can set `FLOW_CLI_ERRORS=json` and `FLOW_SIMPLE_OUTPUT=1` for machine/CI output.
- Naming: CLI flags are kebab-case (`--max-price-per-hour`), module/identifiers are snake_case.

## Progress & JSON Output (Authoring Rules)

- Use AnimatedEllipsisProgress (AEP) for short waits like lookups/resolution/fetch. Prefer `start_immediately=True` for instant feedback and set `transient=True` so the line is cleared when done.
- Stop AEP before rendering large tables or multi-line output to avoid Live/print interleaving. A common pattern is: open AEP, perform network fetch, close AEP, then render.
- Use StepTimeline for multi-step flows (e.g., run/dev/ssh/upload). Close the timeline before handing terminal control to remote shells or other Live displays.
- In `--json` mode, never show progress spinners or interactive UI. If JSON requires an identifier, validate early and exit with a machine-readable error instead of opening selectors/spinners.
- Prefer `console.print` for output (including JSON) so Live regions can safely redirect output when active; avoid raw `print` unless intentionally bypassing Rich.

## Command Groups

If your command has subcommands, return a `click.Group` from `get_command()` and add subcommands in that function. See `volumes.py` for a compact example.

## Shared Components You Can Use

- `flow.cli.commands.base.BaseCommand`: common error/auth handlers and `console`.
- `flow.cli.commands.feedback.feedback`: success/error/info panels with consistent styling.
- `flow.cli.utils.theme_manager.theme_manager`: colors and `create_console()`.
- `flow.cli.ui.facade.*`: higher-level presenters (tables/views) for common UIs.
- `flow.cli.commands.utils`: small helpers like `display_config`, `wait_for_task`.
- `flow.cli.utils.shell_completion`: completions for files, tasks, keys, volumes.

## Testing Snippet

```python
from click.testing import CliRunner
from flow.cli.app import cli, setup_cli

def test_mycmd_runs():
    setup_cli()  # registers lazy loaders
    runner = CliRunner()
    result = runner.invoke(cli, ["mycmd", "--flag"])  # or: command.get_command()
    assert result.exit_code == 0
```

## Architecture Notes

- Single Responsibility: one command per module.
- Consistent Interface: inherit `BaseCommand` and expose `command`.
- Maintainability: lazy registration in `app.py` keeps startup fast and optional deps optional.

The original monolithic app has been decomposed into these modules for readability, testability, and incremental evolution of the CLI.
