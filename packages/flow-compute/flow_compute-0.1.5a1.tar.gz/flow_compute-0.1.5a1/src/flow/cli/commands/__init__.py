"""Flow CLI commands registry (backed by a centralized manifest).

Each command lives in its own module and exposes a module-level `command`
object implementing `BaseCommand`. The list of root-level commands is loaded
from `flow.cli.command_manifest` to avoid duplication with the CLI app loader.
Missing or optional commands are skipped gracefully.
"""

from importlib import import_module
from typing import List

from flow.cli.command_manifest import COMMANDS, iter_modules_from_commands
from flow.cli.commands.base import BaseCommand

# Single source of truth for module names derived from the manifest.
_COMMAND_MODULE_NAMES = iter_modules_from_commands(COMMANDS)


def get_commands() -> list[BaseCommand]:
    """Discover and return all available CLI command objects.

    Imports each known module defensively and collects its `command` attribute
    if present. Any ImportError or missing `command` is ignored to ensure the
    CLI remains usable even when optional features are unavailable.
    """
    discovered: list[BaseCommand] = []
    base_package = __name__

    for module_name in _COMMAND_MODULE_NAMES:
        try:
            module = import_module(f"{base_package}.{module_name}")
        except Exception:
            # Optional or unavailable module; skip
            continue

        cmd = getattr(module, "command", None)
        if cmd is not None:
            discovered.append(cmd)

    return discovered


__all__ = ["BaseCommand", "get_commands"]
