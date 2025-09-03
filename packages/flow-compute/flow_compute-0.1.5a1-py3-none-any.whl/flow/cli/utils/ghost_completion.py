"""Ghost text completion for Flow CLI.

Provides inline completion previews (ghost text) that show what would be
completed if the user pressed TAB, similar to modern IDEs and shells.

The ghost text appears in gray/dimmed text after the cursor, giving users
confidence about what will happen before they commit to the completion.
"""

import select
import sys
import termios
import tty
from collections.abc import Callable
from dataclasses import dataclass

from rich.console import Console


@dataclass
class CompletionCandidate:
    """A potential completion with metadata."""

    value: str
    display: str
    description: str | None = None
    type: str = "plain"  # plain, file, dir, command, option
    priority: int = 0


class GhostCompleter:
    """Provides ghost text completion for interactive CLI input.

    This creates a readline-like experience with inline completion
    previews that appear as dimmed text after the cursor.
    """

    def __init__(self, completion_func: Callable[[str], list[CompletionCandidate]]):
        self.completion_func = completion_func
        self.console = Console()
        self.history = []
        self.history_index = -1

    def read_with_ghost_completion(self, prompt: str = "> ", initial_text: str = "") -> str | None:
        """Read user input with ghost completion preview.

        Returns the entered text or None if cancelled (Ctrl-C).
        """
        if not sys.stdin.isatty():
            # Fallback for non-interactive mode
            try:
                return input(prompt)
            except EOFError:
                return None

        # Set up terminal
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin)
            return self._interactive_read(prompt, initial_text)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _interactive_read(self, prompt: str, initial_text: str) -> str | None:
        """Interactive reading with ghost completion."""
        buffer = list(initial_text)
        cursor_pos = len(buffer)
        ghost_text = ""

        # Display initial state
        self._redraw(prompt, buffer, cursor_pos, ghost_text)

        while True:
            # Check for input
            if select.select([sys.stdin], [], [], 0.01)[0]:
                char = sys.stdin.read(1)

                # Handle special keys
                if char == "\x03":  # Ctrl-C
                    print("\n")
                    return None
                elif char == "\r" or char == "\n":  # Enter
                    print("\n")
                    result = "".join(buffer)
                    if result:
                        self.history.append(result)
                    return result
                elif char == "\x7f" or char == "\x08":  # Backspace
                    if cursor_pos > 0:
                        buffer.pop(cursor_pos - 1)
                        cursor_pos -= 1
                elif char == "\t":  # Tab - accept ghost completion
                    if ghost_text:
                        buffer.extend(list(ghost_text))
                        cursor_pos = len(buffer)
                        ghost_text = ""
                elif char == "\x1b":  # Escape sequence
                    next_chars = sys.stdin.read(2)
                    if next_chars == "[A":  # Up arrow - history
                        if self.history and self.history_index > -len(self.history):
                            self.history_index -= 1
                            buffer = list(self.history[self.history_index])
                            cursor_pos = len(buffer)
                    elif next_chars == "[B":  # Down arrow - history
                        if self.history_index < -1:
                            self.history_index += 1
                            if self.history_index == -1:
                                buffer = []
                            else:
                                buffer = list(self.history[self.history_index])
                            cursor_pos = len(buffer)
                    elif next_chars == "[C":  # Right arrow
                        if cursor_pos < len(buffer):
                            cursor_pos += 1
                        elif ghost_text:
                            # Accept one word of ghost text
                            words = ghost_text.split(" ", 1)
                            word = words[0]
                            buffer.extend(list(word))
                            if len(words) > 1 and words[1]:
                                buffer.append(" ")
                            cursor_pos = len(buffer)
                    elif next_chars == "[D":  # Left arrow
                        if cursor_pos > 0:
                            cursor_pos -= 1
                elif char.isprintable():
                    # Insert character
                    buffer.insert(cursor_pos, char)
                    cursor_pos += 1

                # Update ghost text
                current_text = "".join(buffer)
                ghost_text = self._get_ghost_text(current_text)

                # Redraw
                self._redraw(prompt, buffer, cursor_pos, ghost_text)

    def _get_ghost_text(self, current_text: str) -> str:
        """Get ghost completion text for current input."""
        if not current_text:
            return ""

        candidates = self.completion_func(current_text)
        if not candidates:
            return ""

        # Sort by priority
        candidates.sort(key=lambda c: (-c.priority, c.value))

        # Find best match
        best = candidates[0]
        if best.value.startswith(current_text):
            return best.value[len(current_text) :]

        return ""

    def _redraw(self, prompt: str, buffer: list[str], cursor_pos: int, ghost_text: str):
        """Redraw the current line with ghost text."""
        # Clear line
        sys.stdout.write("\r\033[K")

        # Write prompt
        sys.stdout.write(prompt)

        # Write buffer
        text = "".join(buffer)
        sys.stdout.write(text)

        # Write ghost text in gray
        if ghost_text:
            sys.stdout.write("\033[90m" + ghost_text + "\033[0m")

        # Move cursor to correct position
        if cursor_pos < len(buffer):
            move_back = len(buffer) - cursor_pos
            if ghost_text:
                move_back += len(ghost_text)
            sys.stdout.write(f"\033[{move_back}D")

        sys.stdout.flush()


class FlowGhostCompleter(GhostCompleter):
    """Ghost completer specifically for Flow CLI commands."""

    def __init__(self):
        super().__init__(self._get_flow_completions)
        self.commands = {
            "cancel": {
                "description": "Cancel running tasks",
                "options": ["--yes", "--all", "--help"],
            },
            "logs": {"description": "View task logs", "options": ["--follow", "--tail", "--help"]},
            "ssh": {"description": "SSH into running task", "options": ["--help"]},
            "status": {
                "description": "Show task status",
                "options": ["--json", "--verbose", "--help"],
            },
            "run": {"description": "Run a task", "options": ["--watch", "--detach", "--help"]},
            "init": {"description": "Initialize Flow configuration", "options": ["--help"]},
            "volumes": {
                "description": "Manage volumes",
                "subcommands": ["list", "create", "delete"],
                "options": ["--help"],
            },
            "example": {
                "description": "Show example configurations",
                "options": ["--show", "--help"],
            },
        }

    def _get_flow_completions(self, text: str) -> list[CompletionCandidate]:
        """Get completion candidates for Flow commands."""
        parts = text.split()

        if not parts:
            # Complete command names
            return [
                CompletionCandidate(
                    value=cmd,
                    display=cmd,
                    description=info.get("description"),
                    type="command",
                    priority=10,
                )
                for cmd, info in self.commands.items()
            ]

        # Check if we're completing a command
        if len(parts) == 1 and not text.endswith(" "):
            prefix = parts[0]
            return [
                CompletionCandidate(
                    value=cmd,
                    display=cmd,
                    description=info.get("description"),
                    type="command",
                    priority=10 if cmd.startswith(prefix) else 5,
                )
                for cmd, info in self.commands.items()
                if cmd.startswith(prefix)
            ]

        # Command is complete, check for subcommands or options
        cmd = parts[0]
        if cmd in self.commands:
            cmd_info = self.commands[cmd]

            # If we're starting a new word
            if text.endswith(" "):
                candidates = []

                # Add subcommands
                if "subcommands" in cmd_info:
                    candidates.extend(
                        [
                            CompletionCandidate(value=sub, display=sub, type="command", priority=10)
                            for sub in cmd_info["subcommands"]
                        ]
                    )

                # Add options
                candidates.extend(
                    [
                        CompletionCandidate(value=opt, display=opt, type="option", priority=5)
                        for opt in cmd_info.get("options", [])
                    ]
                )

                # Add task IDs for task-specific commands
                if cmd in ["cancel", "logs", "ssh"]:
                    # In real implementation, would fetch from API
                    candidates.append(
                        CompletionCandidate(
                            value="task-",
                            display="task-abc123",
                            description="Running GPU task",
                            type="plain",
                            priority=8,
                        )
                    )

                return candidates

        return []


def create_flow_ghost_completer() -> FlowGhostCompleter:
    """Create a ghost completer for Flow CLI."""
    return FlowGhostCompleter()


# Example usage for testing
if __name__ == "__main__":
    completer = create_flow_ghost_completer()

    print("Flow CLI with ghost completion")
    print("Try typing 'can' and see the ghost text appear!")
    print("Press TAB to accept, Right arrow to accept one word")
    print("Ctrl-C to exit\n")

    while True:
        result = completer.read_with_ghost_completion("flow> ")
        if result is None:
            break
        print(f"You entered: {result}")
