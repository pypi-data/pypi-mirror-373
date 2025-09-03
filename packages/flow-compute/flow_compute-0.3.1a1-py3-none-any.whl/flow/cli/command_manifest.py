"""Centralized manifest for Flow CLI commands.

Provides a single source of truth used by the root CLI loader and
the legacy commands registry to prevent drift between different
command listings.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CommandSpec:
    """Specification for a concrete CLI command backed by a module."""

    name: str
    module: str
    summary: str
    example: str | None = None
    hidden: bool = False


@dataclass(frozen=True)
class AliasSpec:
    """Alias mapping to an existing command module.

    The loader will import the target module and expose a wrapper command
    registered under `alias` that forwards all options/args.
    """

    alias: str
    target_module: str
    summary: str | None = None
    example: str | None = None
    hidden: bool = True


@dataclass(frozen=True)
class StubSpec:
    """Lightweight placeholder for deferred/coming-soon commands."""

    name: str
    note: str
    summary: str = "(coming soon)"
    hidden: bool = True


# Canonical command list (in desired help order)
COMMANDS: Final[list[CommandSpec]] = [
    CommandSpec("init", "init", "Configure credentials", "flow init"),
    CommandSpec("docs", "docs", "Show documentation links", "flow docs --verbose"),
    CommandSpec(
        "pricing", "pricing", "Market prices and recommendations", "flow pricing --gpu h100"
    ),
    CommandSpec("finops", "finops", "FinOps pricing config and tiers", "flow finops"),
    CommandSpec("status", "status", "List and monitor tasks", "flow status --watch"),
    CommandSpec("dev", "dev", "Development environment", "flow dev"),
    CommandSpec("run", "run", "Submit task from YAML or command", "flow run 'nvidia-smi'"),
    CommandSpec(
        "template", "template", "Generate YAML templates", "flow template task -o task.yaml"
    ),
    CommandSpec("grab", "grab", "Quick resource selection", "flow grab 8 h100"),
    CommandSpec("cancel", "cancel", "Cancel tasks", "flow cancel 1"),
    CommandSpec("ssh", "ssh", "SSH into task", "flow ssh 1"),
    CommandSpec("logs", "logs", "View task logs", "flow logs 1 -f"),
    CommandSpec("volumes", "volumes", "Manage volumes", "flow volumes get"),
    CommandSpec("mount", "mount", "Attach volumes", "flow mount 1 myvol:/data"),
    CommandSpec("ssh-keys", "ssh_keys", "Manage SSH keys", "flow ssh-keys get"),
    CommandSpec(
        "ports",
        "port_forward",
        "Manage ports and tunnels",
        "flow ports open 1 --port 8080,8888,3000-3002",
    ),
    CommandSpec("upload-code", "upload_code", "Upload code to task", "flow upload-code 1"),
    # Canonical command is singular 'reserve'; 'reservations' is an alias
    CommandSpec("reserve", "reserve", "Manage capacity reservations", "flow reserve list"),
    CommandSpec("theme", "theme", "Manage CLI color themes", "flow theme set modern"),
    CommandSpec("update", "update", "Update Flow SDK", "flow update"),
    CommandSpec("example", "example", "Run or show starters", "flow example gpu-test"),
    # Additional utilities that exist but are not prominently listed
    CommandSpec("completion", "completion", "Shell completion helpers", "flow completion install"),
    CommandSpec("alloc", "alloc", "Compact allocation view", "flow alloc --watch", hidden=True),
]


# Aliases for familiarity and convenience
ALIASES: Final[list[AliasSpec]] = [
    AliasSpec(
        alias="delete",
        target_module="cancel",
        summary="Cancel tasks (alias of 'cancel')",
        example="flow delete 1",
        hidden=True,
    ),
    AliasSpec(
        alias="port-forward",
        target_module="port_forward",
        summary="Manage ports and tunnels (alias of 'ports')",
        example="flow port-forward open 1 --port 8080",
        hidden=True,
    ),
    AliasSpec(
        alias="reservations",
        target_module="reserve",
        summary="Manage capacity reservations (alias of 'reserve')",
        example="flow reservations list",
        hidden=True,
    ),
]


# Deferred surfaces that should present a friendly placeholder
STUBS: Final[list[StubSpec]] = [
    StubSpec("tutorial", "Run 'flow init' to get started."),
    StubSpec("demo", "Demo mode will ship later."),
    StubSpec("daemon", "Local background agent (flowd) is not included in this release."),
    StubSpec("slurm", "Slurm integration is coming soon; follow updates in release notes."),
    StubSpec("colab", "Colab local runtime integration is coming soon."),
]


def iter_modules_from_commands(commands: Iterable[CommandSpec]) -> list[str]:
    """Return unique module names from command specs preserving order."""
    seen: set[str] = set()
    out: list[str] = []
    for c in commands:
        if c.module not in seen:
            out.append(c.module)
            seen.add(c.module)
    return out


__all__ = [
    "CommandSpec",
    "AliasSpec",
    "StubSpec",
    "COMMANDS",
    "ALIASES",
    "STUBS",
    "iter_modules_from_commands",
]
