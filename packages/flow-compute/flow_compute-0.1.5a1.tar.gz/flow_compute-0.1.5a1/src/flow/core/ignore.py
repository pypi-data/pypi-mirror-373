from __future__ import annotations

"""Unified ignore pattern builder for code packaging and transfer.

This module centralizes how we determine which files to exclude during
code packaging and rsync-based transfers. It prefers a project-level
`.flowignore` file when present, falling back to `.gitignore` for
familiar behavior in repositories that don't yet define `.flowignore`.

Patterns use simple glob matching semantics and are consumed by both the
packager and transfer layers to ensure consistent behavior across paths.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExcludeSpec:
    """Represents a concrete set of exclude patterns and their origin."""

    patterns: list[str]
    source: str  # one of: "flowignore", "gitignore", "defaults"


DEFAULT_EXCLUDES: tuple[str, ...] = (
    ".git/",
    ".git",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".coverage",
    "*.egg-info/",
    ".DS_Store",
    ".venv",
    "venv",
    "node_modules/",
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
    "*~",
    ".rsync-partial/",
)


def _read_ignore_file(path: Path) -> list[str]:
    patterns: list[str] = []
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
    except Exception:
        # Best-effort: return what we have
        return patterns
    return patterns


def build_exclude_patterns(base: Path | None = None) -> ExcludeSpec:
    """Return exclude patterns and their source for a project tree.

    Order of precedence:
      1) .flowignore if present
      2) .gitignore if present
      3) defaults only
    """
    base_dir = (base or Path.cwd()).resolve()
    flowignore = base_dir / ".flowignore"
    gitignore = base_dir / ".gitignore"

    if flowignore.exists():
        return ExcludeSpec(patterns=[*DEFAULT_EXCLUDES, *_read_ignore_file(flowignore)], source="flowignore")
    if gitignore.exists():
        try:
            logger.info(
                "Using .gitignore as fallback for upload excludes (no .flowignore found). "
                "Add a .flowignore to make code upload behavior explicit."
            )
        except Exception:
            pass
        return ExcludeSpec(patterns=[*DEFAULT_EXCLUDES, *_read_ignore_file(gitignore)], source="gitignore")
    return ExcludeSpec(patterns=list(DEFAULT_EXCLUDES), source="defaults")


def should_exclude(path: Path, base: Path, patterns: Iterable[str]) -> bool:
    """Return True if the given path should be excluded.

    Matching is performed against the absolute and relative paths to handle
    common glob patterns. Directory patterns (ending with '/') match the
    directory itself and any content under it.
    """
    from pathlib import PurePath

    rel = PurePath(path.relative_to(base)) if path.is_absolute() else PurePath(path)
    abs_path = PurePath(path)

    for pat in patterns:
        # Directory pattern: match directory or anything under it
        if pat.endswith("/"):
            dir_pat = pat[:-1]
            if rel.match(dir_pat) or any(p.name == dir_pat for p in path.parents):
                return True
            if abs_path.match(dir_pat):
                return True
            continue
        if rel.match(pat) or abs_path.match(pat):
            return True
    return False
