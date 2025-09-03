"""Terminal adaptation utilities for responsive CLI displays."""

import os
import shutil
from enum import Enum
from typing import Any


class TableDensity(Enum):
    """Table density modes for different use cases."""

    COMPACT = "compact"  # Maximum information, minimal spacing
    NORMAL = "normal"  # Balanced approach
    COMFORTABLE = "comfortable"  # Extra spacing for readability


class TerminalBreakpoints:
    """Standard terminal width breakpoints for responsive design."""

    NARROW = 60  # Mobile-like, minimal columns
    COMPACT = 80  # Standard terminal, core columns
    NORMAL = 100  # Comfortable viewing, most columns
    WIDE = 120  # Wide terminal, all columns
    ULTRA_WIDE = 140  # Ultra-wide, extended information


class TerminalAdapter:
    """Handles terminal-specific display adaptations.

    This adapter provides responsive display capabilities, adjusting output
    based on terminal width and other constraints.
    """

    @staticmethod
    def get_terminal_width() -> int:
        """Get terminal width with robust fallbacks for different environments.

        Returns:
            Terminal width in columns with intelligent fallbacks
        """
        try:
            # Primary method
            width = shutil.get_terminal_size().columns
            if width > 0:
                return width
        except Exception:
            pass

        # Fallback methods for different environments
        for env_var in ["COLUMNS", "TERM_COLS"]:
            try:
                width = int(os.environ.get(env_var, 0))
                if width > 0:
                    return width
            except (ValueError, TypeError):
                continue

        # Environment-specific fallbacks
        if os.environ.get("CI"):
            return 100  # CI environment
        elif os.environ.get("TERM") == "dumb":
            return 80  # Dumb terminal
        else:
            return 120  # Modern terminal default

    @staticmethod
    def get_responsive_layout(width: int | None = None) -> dict[str, Any]:
        """Get complete responsive layout configuration based on terminal width.

        Args:
            width: Terminal width (auto-detected if not provided)

        Returns:
            Complete layout configuration dictionary
        """
        if width is None:
            width = TerminalAdapter.get_terminal_width()

        if width < TerminalBreakpoints.NARROW:
            return {
                "columns": ["name", "status"],
                "name_width": 15,
                "status_width": 8,
                "show_table_title": False,
                "use_compact_status": True,
                "density": TableDensity.COMPACT,
                "show_borders": False,
            }
        elif width < TerminalBreakpoints.COMPACT:
            return {
                "columns": ["name", "status", "created"],
                "name_width": 20,
                "status_width": 14,
                "created_width": 15,
                "show_table_title": True,
                "use_compact_status": False,
                "density": TableDensity.COMPACT,
                "show_borders": True,
            }
        elif width < TerminalBreakpoints.NORMAL:
            return {
                "columns": ["name", "status", "gpu", "ip", "created"],
                "name_width": 20,
                "status_width": 14,
                "gpu_width": 10,
                "ip_width": 15,
                "created_width": 15,
                "show_table_title": True,
                "use_compact_status": False,
                "density": TableDensity.NORMAL,
                "show_borders": True,
            }
        elif width < TerminalBreakpoints.WIDE:
            return {
                "columns": ["name", "status", "gpu", "ip", "created", "duration"],
                "name_width": 25,
                "status_width": 15,
                "gpu_width": 15,
                "ip_width": 15,
                "created_width": 15,
                "duration_width": 10,
                "show_table_title": True,
                "use_compact_status": False,
                "density": TableDensity.NORMAL,
                "show_borders": True,
            }
        else:  # WIDE and above
            return {
                "columns": ["name", "status", "gpu", "ip", "created", "duration"],
                "name_width": 30,
                "status_width": 15,
                "gpu_width": 18,
                "ip_width": 15,
                "created_width": 15,
                "duration_width": 12,
                "show_table_title": True,
                "use_compact_status": False,
                "density": TableDensity.COMFORTABLE,
                "show_borders": True,
            }

    @staticmethod
    def get_responsive_columns(min_width: int = 60) -> dict[str, bool]:
        """Determine which columns to show based on terminal width.

        Args:
            min_width: Minimum width before hiding optional columns

        Returns:
            Dictionary of column visibility flags
        """
        layout = TerminalAdapter.get_responsive_layout()
        columns = layout["columns"]

        return {
            "essential": True,
            "name": "name" in columns,
            "status": "status" in columns,
            "gpu": "gpu" in columns,
            "created": "created" in columns,
            "duration": "duration" in columns,
            "task_id": len(columns) >= 5,
            "extended": len(columns) >= 6,
        }

    @staticmethod
    def is_simple_output() -> bool:
        """Whether to favor simple, low-chrome output.

        True for non-TTY or CI environments, or when FLOW_SIMPLE_OUTPUT is set.
        Keeps UX focused without extra flags.
        """
        try:
            import os as _os
            import sys as _sys

            val = (_os.getenv("FLOW_SIMPLE_OUTPUT", "") or "").strip().lower()
            if val in {"1", "true", "yes", "on"}:
                return True
            if not _sys.stdout.isatty():
                return True
            if _os.getenv("CI"):
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def intelligent_truncate(
        text: str, max_width: int, priority: str = "end", suffix: str = "..."
    ) -> str:
        """Intelligent text truncation preserving important information.

        Args:
            text: Text to truncate
            max_width: Maximum width
            priority: Truncation strategy ("start", "end", "middle")
            suffix: Suffix to append when truncating

        Returns:
            Intelligently truncated text
        """
        if len(text) <= max_width:
            return text

        if max_width <= len(suffix):
            return text[:max_width]

        if priority == "start":
            # Keep beginning (useful for task names)
            return text[: max_width - len(suffix)] + suffix
        elif priority == "end":
            # Keep end (useful for IDs)
            return suffix + text[-(max_width - len(suffix)) :]
        elif priority == "middle":
            # Keep start and end (useful for file paths)
            start_len = (max_width - len(suffix)) // 2
            end_len = max_width - len(suffix) - start_len
            if end_len > 0:
                return text[:start_len] + suffix + text[-end_len:]
            else:
                return text[:start_len] + suffix

        return text[: max_width - len(suffix)] + suffix

    @staticmethod
    def truncate_text(text: str, max_width: int, suffix: str = "...") -> str:
        """Simple text truncation for backward compatibility.

        Args:
            text: Text to truncate
            max_width: Maximum width
            suffix: Suffix to append when truncating

        Returns:
            Truncated text
        """
        return TerminalAdapter.intelligent_truncate(text, max_width, "start", suffix)

    @staticmethod
    def calculate_optimal_column_widths(
        terminal_width: int,
        required_columns: list[str],
        optional_columns: list[str],
        content_samples: dict[str, list[str]],
    ) -> dict[str, int]:
        """Calculate optimal column widths based on actual content.

        Args:
            terminal_width: Available terminal width
            required_columns: Columns that must be shown
            optional_columns: Columns that can be hidden if needed
            content_samples: Sample content for width calculation

        Returns:
            Dictionary mapping column names to optimal widths
        """
        # Reserve space for borders and padding (3 chars per column + 1)
        all_columns = required_columns + optional_columns
        table_overhead = len(all_columns) * 3 + 1
        available_width = terminal_width - table_overhead

        # Calculate minimum required widths based on content
        min_widths = {}
        for col in all_columns:
            samples = content_samples.get(col, [col])  # Use column name as fallback
            # Take max of first 10 samples for performance
            sample_widths = [len(str(s)) for s in samples[:10]]
            min_widths[col] = max(sample_widths) if sample_widths else len(col)

        # Ensure minimum viable widths
        min_viable_widths = {
            "name": 15,
            "status": 8,
            "gpu": 10,
            "created": 10,
            "duration": 8,
        }

        for col in all_columns:
            min_widths[col] = max(min_widths[col], min_viable_widths.get(col, 8))

        # Calculate total minimum width needed
        min_total = sum(min_widths[col] for col in required_columns)

        # If we can't fit required columns, use emergency fallback
        if min_total > available_width:
            return TerminalAdapter._emergency_column_widths(required_columns, available_width)

        # Distribute remaining width intelligently
        remaining_width = available_width - min_total
        widths = {col: min_widths[col] for col in required_columns}

        # Add optional columns if we have space
        for col in optional_columns:
            needed = min_widths[col]
            if remaining_width >= needed:
                widths[col] = needed
                remaining_width -= needed

        # Distribute any extra width to flexible columns
        flexible_cols = ["name"]  # Name column gets extra space
        if remaining_width > 0 and flexible_cols:
            for col in flexible_cols:
                if col in widths:
                    widths[col] += remaining_width // len(flexible_cols)

        return widths

    @staticmethod
    def _emergency_column_widths(columns: list[str], available_width: int) -> dict[str, int]:
        """Emergency column width calculation when space is extremely limited.

        Args:
            columns: List of column names
            available_width: Available width

        Returns:
            Emergency width allocation
        """
        # Ultra-compact mode: distribute equally with minimums
        min_width = max(available_width // len(columns), 5)
        return dict.fromkeys(columns, min_width)

    @staticmethod
    def calculate_column_widths(
        available_width: int, columns: list[tuple[str, int, bool]]
    ) -> dict[str, int]:
        """Calculate optimal column widths based on available space.

        Args:
            available_width: Total available terminal width
            columns: List of (name, preferred_width, is_flexible) tuples

        Returns:
            Dictionary mapping column names to allocated widths
        """
        # This is the legacy method - delegate to the new implementation
        required_columns = [name for name, _, _ in columns]
        content_samples = {name: [name] for name, _, _ in columns}  # Basic fallback

        return TerminalAdapter.calculate_optimal_column_widths(
            available_width, required_columns, [], content_samples
        )

    @staticmethod
    def should_use_compact_mode() -> bool:
        """Determine if compact display mode should be used.

        Returns:
            True if terminal is narrow enough to warrant compact mode
        """
        return TerminalAdapter.get_terminal_width() < TerminalBreakpoints.NORMAL

    @staticmethod
    def get_density_config(density: TableDensity) -> dict[str, Any]:
        """Get table configuration for different density modes.

        Args:
            density: Desired table density mode

        Returns:
            Configuration dictionary for the density mode
        """
        configs = {
            TableDensity.COMPACT: {
                "row_spacing": 0,
                "column_padding": 1,
                "show_borders": False,
                "truncate_aggressively": True,
                "box_style": None,  # No borders for maximum compactness
            },
            TableDensity.NORMAL: {
                "row_spacing": 0,
                "column_padding": 2,
                "show_borders": True,
                "truncate_aggressively": False,
                "box_style": "rounded",
            },
            TableDensity.COMFORTABLE: {
                "row_spacing": 1,
                "column_padding": 3,
                "show_borders": True,
                "truncate_aggressively": False,
                "box_style": "rounded",
            },
        }
        return configs.get(density, configs[TableDensity.NORMAL])
