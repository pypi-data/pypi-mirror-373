"""Console patching to ensure theme and color settings are respected globally.

This module patches Rich's Console class to automatically apply Flow's theme
and color settings from environment variables, ensuring consistency across
all Console instances in the codebase.
"""

import functools
import os

from rich.console import Console as RichConsole


def _patch_console_init():
    """Patch Console.__init__ to respect Flow's global settings."""
    original_init = RichConsole.__init__

    @functools.wraps(original_init)
    def patched_init(self, *args, **kwargs):
        # Apply NO_COLOR environment variable if set
        if os.environ.get("NO_COLOR") and "no_color" not in kwargs:
            kwargs["no_color"] = True

        # Apply theme if color is enabled and theme not already set
        if not kwargs.get("no_color") and "theme" not in kwargs:
            theme_name = os.environ.get("FLOW_THEME")
            if theme_name:
                # Import here to avoid circular dependencies
                from flow.cli.utils.theme_manager import theme_manager

                # Load the requested theme
                theme = theme_manager.load_theme(theme_name)
                if theme:
                    kwargs["theme"] = theme.to_rich_theme()

        # Call original init
        original_init(self, *args, **kwargs)

    RichConsole.__init__ = patched_init


# Apply patch when module is imported
_patch_console_init()
