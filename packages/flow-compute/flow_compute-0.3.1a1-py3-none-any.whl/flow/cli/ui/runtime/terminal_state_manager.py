"""Terminal state management for clean transitions between UI modes.

This module ensures proper terminal state handling to prevent escape sequences
and other artifacts when transitioning between different terminal interaction modes.
"""

import os
import sys
import termios
import tty
from contextlib import contextmanager


class TerminalStateManager:
    """Manages terminal state to prevent escape sequence artifacts."""

    def __init__(self):
        self.original_settings = None
        self.is_tty = sys.stdin.isatty() and sys.stdout.isatty()

    def save_state(self) -> list | None:
        """Save current terminal state."""
        if not self.is_tty:
            return None

        try:
            return termios.tcgetattr(sys.stdin)
        except Exception:
            return None

    def restore_state(self, state: list | None) -> None:
        """Restore terminal state."""
        if not self.is_tty or state is None:
            return

        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, state)
        except Exception:
            pass

    def flush_all(self) -> None:
        """Flush all streams and clear any pending input."""
        try:
            # Flush output streams
            sys.stdout.flush()
            sys.stderr.flush()

            # Clear input buffer if TTY
            if self.is_tty:
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass

    def consume_pending_input(self) -> None:
        """Consume any pending input to prevent escape sequences from appearing."""
        if not self.is_tty:
            return

        try:
            # Save current state
            old_settings = termios.tcgetattr(sys.stdin)

            # Set non-blocking mode temporarily
            tty.setcbreak(sys.stdin.fileno())

            # Read and discard any pending input
            import select

            consumed_chars = []
            while True:
                # Check if there's input available, with a short timeout
                ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not ready:
                    break
                # Read and discard one character
                char = sys.stdin.read(1)
                consumed_chars.append(char)

            # Debug output if we consumed anything
            if consumed_chars and os.environ.get("FLOW_DEBUG"):
                consumed = "".join(consumed_chars)
                # Convert to readable format
                readable = repr(consumed)
                print(f"[DEBUG] Consumed pending input: {readable}", file=sys.stderr)

            # Restore settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except Exception as e:
            if os.environ.get("FLOW_DEBUG"):
                print(f"[DEBUG] Error consuming input: {e}", file=sys.stderr)

    @contextmanager
    def clean_terminal_transition(self):
        """Context manager for clean terminal state transitions."""
        # Save current state
        saved_state = self.save_state()

        try:
            yield
        finally:
            # Ensure clean state for next operation
            self.flush_all()
            self.consume_pending_input()

            # Restore if we have saved state
            if saved_state:
                self.restore_state(saved_state)

            # Final flush
            self.flush_all()

    def reset_for_prompt(self) -> None:
        """Reset terminal to clean state for prompting."""
        if os.environ.get("FLOW_DEBUG"):
            print("[DEBUG] Resetting terminal for prompt", file=sys.stderr)

        # Flush everything
        self.flush_all()

        # Consume any pending input that might contain escape sequences
        self.consume_pending_input()

        # Ensure terminal is in cooked mode for prompt
        if self.is_tty:
            try:
                # Get current settings
                settings = termios.tcgetattr(sys.stdin)
                # Ensure ICANON (canonical mode) is set
                settings[3] |= termios.ICANON | termios.ECHO
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

                if os.environ.get("FLOW_DEBUG"):
                    print("[DEBUG] Terminal reset to canonical mode", file=sys.stderr)
            except Exception as e:
                if os.environ.get("FLOW_DEBUG"):
                    print(f"[DEBUG] Error resetting terminal: {e}", file=sys.stderr)


# Global instance for convenience
terminal_state = TerminalStateManager()
