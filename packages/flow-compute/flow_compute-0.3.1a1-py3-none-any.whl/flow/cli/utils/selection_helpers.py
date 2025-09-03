"""Helpers for parsing index/range selections shared by logs/ssh/cancel commands."""

from __future__ import annotations

import re

from flow.cli.utils.selection import Selection, SelectionParseError
from flow.cli.utils.task_index_cache import TaskIndexCache


def parse_selection_to_task_ids(expr: str) -> tuple[list[str] | None, str | None]:
    """Parse an index/range expression to concrete task IDs via cache.

    Accepts bare numbers and ranges (preferred), e.g. "1-3,5", and the legacy
    leading-colon form, e.g. ":1-3,5".

    Returns (task_ids, error_msg). On error, (None, message).
    """
    expression = expr.strip()
    # Accept digits, commas, ranges, with optional legacy leading colon
    if not re.fullmatch(r":?[0-9,\-\s]+", expression):
        return None, None  # Not a selection grammar; caller may treat as name/ID

    try:
        if expression.startswith(":"):
            expression = expression[1:]
        selection = Selection.parse(expression)
    except SelectionParseError as e:
        return None, f"Selection error: {e}"

    idx_map = TaskIndexCache().get_indices_map()
    if not idx_map:
        return None, "No cached indices available. Run 'flow status' first."

    task_ids, errors = selection.to_task_ids(idx_map)
    if errors:
        return None, errors[0]

    return task_ids, None
