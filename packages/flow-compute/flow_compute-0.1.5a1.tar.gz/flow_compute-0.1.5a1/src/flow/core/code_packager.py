"""Code packaging utilities for remote execution.

This module provides functionality to package local code directories into
compressed archives for upload to remote execution environments.
"""

import os
import tarfile
import tempfile
from pathlib import Path

from flow.core.ignore import build_exclude_patterns, should_exclude


class CodePackager:
    """Package local code into compressed archives for remote execution."""

    # Default patterns to exclude from packaging
    DEFAULT_EXCLUDES = {
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".gitignore",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "*.egg-info",
        ".DS_Store",
        ".venv",
        "venv",
        ".env",
        "node_modules",
        ".idea",
        ".vscode",
        "*.swp",
        "*.swo",
        "*~",
        ".cache",
    }

    def __init__(self, exclude_patterns: set[str] | None = None):
        """Initialize the packager with optional custom exclude patterns.

        Args:
            exclude_patterns: Additional patterns to exclude from packaging.
                             These are added to the default excludes.
        """
        self.exclude_patterns = self.DEFAULT_EXCLUDES.copy()
        if exclude_patterns:
            self.exclude_patterns.update(exclude_patterns)

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from packaging.

        Args:
            path: Path to check.

        Returns:
            True if the path should be excluded, False otherwise.
        """
        name = path.name

        # Check exact matches
        if name in self.exclude_patterns:
            return True

        # Check glob patterns and directory patterns
        for pattern in self.exclude_patterns:
            # Handle directory patterns like "data/"
            if pattern.endswith("/"):
                dir_name = pattern[:-1]
                # Check if this is the directory itself or inside it
                if name == dir_name or any(parent.name == dir_name for parent in path.parents):
                    return True
            # Handle glob patterns
            elif "*" in pattern and path.match(pattern):
                return True

        return False

    def create_package(self, source_dir: Path, output_path: Path | None = None) -> Path:
        """Create a compressed package of the source directory.

        Args:
            source_dir: Directory to package.
            output_path: Optional output path for the package. If not provided,
                        a temporary file will be created.

        Returns:
            Path to the created package.

        Raises:
            ValueError: If source_dir doesn't exist or isn't a directory.
        """
        source_dir = Path(source_dir).resolve()

        if not source_dir.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        if not source_dir.is_dir():
            raise ValueError(f"Source path is not a directory: {source_dir}")

        # Create output path if not provided
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".tar.gz", prefix="flow_code_")
            os.close(fd)
            output_path = Path(output_path)
        else:
            output_path = Path(output_path)

        # Build unified excludes (flowignore → gitignore → defaults)
        spec = build_exclude_patterns(source_dir)

        # Create tar.gz archive
        with tarfile.open(output_path, "w:gz") as tar:
            # Walk the directory tree
            for root, dirs, files in os.walk(source_dir):
                root_path = Path(root)

                # Filter directories to exclude
                dirs[:] = [
                    d for d in dirs if not should_exclude(root_path / d, source_dir, spec.patterns)
                ]

                # Add files
                for file in files:
                    file_path = root_path / file
                    if not should_exclude(file_path, source_dir, spec.patterns):
                        # Calculate relative path for archive
                        arcname = file_path.relative_to(source_dir)
                        tar.add(file_path, arcname=str(arcname))

        return output_path
