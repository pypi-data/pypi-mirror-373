"""Version utilities for Flow SDK.

Provides a single source of truth for the SDK version that is lightweight to
import from both runtime code and CLI entry points.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version
from pathlib import Path

# Canonical package name as published on PyPI
PACKAGE_NAME = "flow-compute"


def _read_version_from_pyproject(pyproject_path: Path) -> str | None:
    """Best-effort read of project.version from a pyproject.toml file.

    Avoids adding a dependency on tomli/tomllib for Python 3.10 by using a
    minimal parse that looks for the first 'version = "..."' under [project].
    """
    try:
        if not pyproject_path.exists():
            return None
        in_project_table = False
        for raw_line in pyproject_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                in_project_table = line == "[project]"
                continue
            if in_project_table and line.startswith("version"):
                # e.g., version = "0.0.19"
                try:
                    _, value = line.split("=", 1)
                    value = value.strip().strip("'\"")
                    if value:
                        return value
                except Exception:
                    return None
        return None
    except Exception:
        return None


def get_version() -> str:
    """Return the installed package version or a sensible fallback.

    - First tries importlib.metadata for the installed distribution.
    - Falls back to reading pyproject.toml when running from a source checkout.
    - Ultimately returns "0.0.0+unknown" if neither is available.
    """
    try:
        return metadata_version(PACKAGE_NAME)
    except PackageNotFoundError:
        # Likely running from source; try to read pyproject.toml near repo root
        try:
            this_file = Path(__file__).resolve()
            # src/flow/_version.py -> repo_root/pyproject.toml
            pyproject = this_file.parents[2] / "pyproject.toml"
            parsed = _read_version_from_pyproject(pyproject)
            if parsed:
                return parsed
        except Exception:
            pass
        return "0.0.0+unknown"
    except Exception:
        return "0.0.0+unknown"


# Public constant for convenient imports
__version__ = get_version()
