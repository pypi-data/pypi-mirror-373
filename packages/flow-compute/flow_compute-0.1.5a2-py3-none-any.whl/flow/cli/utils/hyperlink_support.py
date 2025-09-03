"""Terminal hyperlink support detection and implementation.

Provides utilities for detecting terminal hyperlink capabilities and
creating clickable links with graceful fallback.
"""

import os
import sys
from urllib.parse import quote


class HyperlinkSupport:
    """Detect and implement terminal hyperlink support using OSC 8."""

    # Known terminals with hyperlink support
    HYPERLINK_TERMINALS = {
        "iTerm.app",
        "iTerm2.app",
        "Terminal.app",  # macOS Terminal (10.15+)
        "WezTerm",
        "kitty",
        "alacritty",  # with config
        "gnome-terminal",
        "konsole",
        "terminator",
        "Windows Terminal",
        "ConEmu",
        "Hyper",
        "terminology",
    }

    # Environment variables that indicate hyperlink support
    HYPERLINK_ENV_VARS = {
        "VTE_VERSION": 5000,  # VTE terminals support from version 0.50.0
        "TERM_PROGRAM": ["iTerm.app", "WezTerm", "Hyper"],
        "TERMINAL_EMULATOR": ["Windows Terminal"],
    }

    def __init__(self):
        """Initialize hyperlink support detector."""
        self._support_cached = None

    def supports_hyperlinks(self) -> bool:
        """Check if terminal supports OSC 8 hyperlinks.

        Returns:
            True if hyperlinks are supported
        """
        # Use cached result if available
        if self._support_cached is not None:
            return self._support_cached

        # Explicit control via env vars
        # Back-compat disable
        if os.environ.get("FLOW_NO_HYPERLINKS") == "1":
            self._support_cached = False
            return False
        # Tri-state: '1/true/on' => enable, '0/false/off' => disable
        hv = (os.environ.get("FLOW_HYPERLINKS") or "").strip().lower()
        if hv in {"1", "true", "yes", "on"}:
            self._support_cached = True
            return True
        if hv in {"0", "false", "no", "off"}:
            self._support_cached = False
            return False

        # Not supported in non-TTY environments
        if not sys.stdout.isatty():
            self._support_cached = False
            return False

        # Check terminal program
        term_program = os.environ.get("TERM_PROGRAM", "")
        if term_program in self.HYPERLINK_TERMINALS:
            self._support_cached = True
            return True

        # Check VTE version
        vte_version = os.environ.get("VTE_VERSION", "")
        if vte_version.isdigit() and int(vte_version) >= self.HYPERLINK_ENV_VARS["VTE_VERSION"]:
            self._support_cached = True
            return True

        # Check for Windows Terminal
        if os.environ.get("WT_SESSION"):
            self._support_cached = True
            return True

        # Check TERM variable for known terminals
        term = os.environ.get("TERM", "")
        if any(known in term for known in ["kitty", "alacritty", "wezterm"]):
            self._support_cached = True
            return True

        # Default to no support
        self._support_cached = False
        return False

    # Back-compat alias used across the CLI codebase
    def is_supported(self) -> bool:  # pragma: no cover - thin alias
        """Alias for supports_hyperlinks().

        Returns:
            True if hyperlinks are supported
        """
        return self.supports_hyperlinks()

    def create_link(self, text: str, url: str, params: str | None = None) -> str:
        """Create hyperlink with graceful fallback.

        Args:
            text: Display text for the link
            url: Target URL
            params: Optional OSC 8 parameters (e.g., "id=xyz")

        Returns:
            Hyperlinked text or plain text fallback
        """
        if not self.supports_hyperlinks():
            # Fallback: show text only or text with URL. If the caller passed the
            # URL as both the text and the target (common in CLIs), avoid
            # duplicating it as "url (url)" and show a single URL.
            if url.startswith("flow://"):
                # Internal commands, just show text
                return text
            if (text or "").strip() == (url or "").strip():
                return url
            # External URLs, show descriptive text plus the URL
            return f"{text} ({url})"

        # Build OSC 8 hyperlink
        # Format: ESC]8;params;uri ESC\text ESC]8;; ESC\
        if params:
            link_start = f"\033]8;{params};{url}\033\\"
        else:
            link_start = f"\033]8;;{url}\033\\"

        link_end = "\033]8;;\033\\"

        return f"{link_start}{text}{link_end}"

    def create_task_link(
        self, task_id: str, text: str | None = None, copy_on_click: bool = True
    ) -> str:
        """Create hyperlink for task ID.

        Args:
            task_id: Full task ID
            text: Display text (may be truncated)
            copy_on_click: If True, create a copy link. If False, logs link.

        Returns:
            Hyperlinked task ID
        """
        if text is None:
            text = task_id

        if copy_on_click:
            # For copy links, we'll use a special URL that indicates copy intent
            # This could be handled by a wrapper script or terminal integration
            url = f"flow://copy/{quote(task_id)}"
        else:
            # Traditional logs link
            url = f"flow://logs/{quote(task_id)}"

        return self.create_link(text, url, f"id=task-{task_id}")

    def create_ssh_link(self, host: str, port: int = 22, text: str | None = None) -> str:
        """Create SSH hyperlink.

        Args:
            host: SSH host/IP address
            port: SSH port (default 22)
            text: Display text (defaults to host)

        Returns:
            Hyperlinked SSH address
        """
        if text is None:
            text = host

        # Standard SSH URL format
        if port != 22:
            url = f"ssh://{host}:{port}"
        else:
            url = f"ssh://{host}"

        return self.create_link(text, url, f"id=ssh-{host}")

    def create_file_link(
        self, file_path: str, line: int | None = None, text: str | None = None
    ) -> str:
        """Create file hyperlink.

        Args:
            file_path: Path to file
            line: Optional line number
            text: Display text (defaults to file path)

        Returns:
            Hyperlinked file path
        """
        if text is None:
            text = file_path

        # File URL with optional line number
        url = f"file://{os.path.abspath(file_path)}"
        if line:
            url += f"#{line}"

        return self.create_link(text, url, f"id=file-{os.path.basename(file_path)}")

    def strip_hyperlinks(self, text: str) -> str:
        """Strip hyperlinks from text, leaving only display text.

        Args:
            text: Text potentially containing hyperlinks

        Returns:
            Text with hyperlinks removed
        """
        # Remove OSC 8 sequences
        import re

        # Pattern: ESC]8;[params];[url]ESC\[text]ESC]8;;ESC\
        pattern = r"\033\]8;[^;]*;[^\033]*\033\\([^\033]*)\033\]8;;\033\\"
        return re.sub(pattern, r"\1", text)

    def extract_hyperlinks(self, text: str) -> list[tuple[str, str]]:
        """Extract hyperlinks from text.

        Args:
            text: Text containing hyperlinks

        Returns:
            List of (display_text, url) tuples
        """
        import re

        links = []

        # Pattern to match OSC 8 hyperlinks
        pattern = r"\033\]8;[^;]*;([^\033]*)\033\\([^\033]*)\033\]8;;\033\\"

        for match in re.finditer(pattern, text):
            url = match.group(1)
            display_text = match.group(2)
            links.append((display_text, url))

        return links

    def _supports_osc52_copy(self) -> bool:
        """Check if terminal supports OSC 52 clipboard operations.

        Returns:
            True if OSC 52 is supported
        """
        term_program = os.environ.get("TERM_PROGRAM", "")
        # Known terminals with OSC 52 support
        return term_program in ["iTerm.app", "iTerm2.app", "Terminal.app", "kitty", "alacritty"]

    def _create_osc52_copy_link(self, text_to_copy: str, display_text: str) -> str:
        """Create a link that copies text via OSC 52 when clicked.

        Args:
            text_to_copy: Text to copy to clipboard
            display_text: Text to display

        Returns:
            Text with embedded OSC 52 copy sequence
        """
        # OSC 52 format: ESC]52;c;base64-encoded-text ESC\
        import base64

        encoded = base64.b64encode(text_to_copy.encode()).decode()

        # Combine hyperlink with OSC 52 copy
        # When clicked, it will copy to clipboard
        copy_sequence = f"\033]52;c;{encoded}\033\\"

        # Return display text with copy sequence that activates on interaction
        # This is a bit of a hack but works in supported terminals
        return f"{copy_sequence}{display_text}"


# Global hyperlink support instance
hyperlink_support = HyperlinkSupport()
