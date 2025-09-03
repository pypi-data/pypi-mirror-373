"""Dev command package.

This package modularizes the legacy monolithic `dev.py` implementation into
separate components for improved maintainability and testability.

Exports:
- `command`: Click command instance for CLI registration
- `DevVMManager`: VM lifecycle manager
- `DevContainerExecutor`: Command execution on the dev VM
"""

from flow.cli.commands.dev.command import command
from flow.cli.commands.dev.vm_manager import DevVMManager
from flow.cli.commands.dev.executor import DevContainerExecutor

__all__ = ["command", "DevVMManager", "DevContainerExecutor"]
