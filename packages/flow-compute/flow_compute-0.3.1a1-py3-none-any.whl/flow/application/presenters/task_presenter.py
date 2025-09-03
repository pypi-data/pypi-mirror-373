"""Deprecated: moved to flow.cli.ui.presentation.task_presenter.

This legacy module remains temporarily to ease migration.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "flow.cli.ui.presentation.task_presenter is deprecated; "
    "use flow.cli.ui.presentation.task_presenter instead",
    DeprecationWarning,
    stacklevel=2,
)

from flow.cli.ui.presentation.task_presenter import (  # noqa: F401
    DisplayOptions,
    TaskPresenter,
    TaskSummary,
)
