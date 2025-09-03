"""Status command query shaping and filtering.

Provides helpers to parse timespecs, shape query DTOs, and filter task lists.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StatusQuery:
    task_identifier: str | None
    show_all: bool
    state: str | None
    limit: int
    since: datetime | None
    until: datetime | None


def parse_timespec(value: str | None) -> datetime | None:
    from flow.cli.utils.time_spec import parse_timespec as _parse

    return _parse(value)


def filter_by_time(
    tasks: Iterable[object], since: datetime | None, until: datetime | None
) -> list[object]:
    from flow.cli.utils.status_utils import filter_tasks_by_time

    return list(filter_tasks_by_time(list(tasks), since, until))
