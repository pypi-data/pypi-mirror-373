"""Interactive selection components for Flow CLI.

This package provides reusable components for interactive resource selection
with proper separation of concerns between models, rendering, state management,
and keyboard interaction.
"""

# Convenience helpers (implemented here to ensure they exist)
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.sdk.models import Task, Volume

from flow.cli.ui.components.formatters.task_formatter import TaskFormatter
from flow.cli.ui.components.formatters.volume_formatter import VolumeFormatter
from flow.cli.ui.components.models import SelectionItem
from flow.cli.ui.components.renderer import map_rich_to_prompt_toolkit_color
from flow.cli.ui.components.selector import InteractiveSelector


def select_task(tasks: Iterable["Task"], **kwargs):  # type: ignore[name-defined]
    from flow.cli.ui.components.selector_api import Selector

    items = [TaskFormatter.to_selection_item(t) for t in tasks]
    return Selector.select_one(items, title=kwargs.get("title", "Select a task"))


def select_volume(volumes: Iterable["Volume"], **kwargs):  # type: ignore[name-defined]
    from flow.cli.ui.components.selector_api import Selector

    items = [VolumeFormatter.to_selection_item(v) for v in volumes]
    if kwargs.get("multiselect", False):
        return Selector.select_many(items, title=kwargs.get("title", "Select volumes"))
    return Selector.select_one(items, title=kwargs.get("title", "Select a volume"))


__all__ = [
    "SelectionItem",
    "InteractiveSelector",
    "select_task",
    "select_volume",
    "map_rich_to_prompt_toolkit_color",
]
