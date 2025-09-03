from __future__ import annotations

"""Terminal input and confirmation utilities for the setup wizard.

This module centralizes platform-dependent I/O handling and fallbacks.
It intentionally contains no business logic or rendering concerns.
"""

import os
import re
import sys

from flow.sdk.helpers.masking import mask_strict_last4


def _drain_stdin() -> None:
    try:
        if not sys.stdin.isatty():
            return
        import select

        r, _, _ = select.select([sys.stdin], [], [], 0)
        while r:
            try:
                os.read(sys.stdin.fileno(), 1024)
            except Exception:
                break
            r, _, _ = select.select([sys.stdin], [], [], 0)
    except Exception:
        pass


def prompt_text_with_escape(
    label: str, *, is_password: bool = False, default: str | None = None
) -> str | None:
    """Prompt for text input where ESC returns None (go back).

    Tries prompt_toolkit first; falls back to robust TTY handling.
    """
    # Attempt prompt_toolkit path
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input import create_input
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.output import create_output

        kb = KeyBindings()
        cancelled = {"value": False}

        @kb.add("escape")
        def _esc(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        @kb.add("c-[")
        def _ctrl_lbracket(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        @kb.add("c-g")
        def _ctrl_g(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        pt_input = create_input()
        pt_output = create_output()
        session = PromptSession(input=pt_input, output=pt_output)
        prompt_text = f"\n{label}: " if not default else f"\n{label} ({default}): "

        def _bottom_toolbar():
            if not is_password:
                return ""
            try:
                from prompt_toolkit.application.current import get_app  # type: ignore

                buf_text = get_app().current_buffer.text
            except Exception:
                buf_text = ""
            if not buf_text:
                return ""
            try:
                if len(buf_text) >= 10:
                    masked = mask_strict_last4(buf_text)
                elif len(buf_text) >= 4:
                    masked = "••••"
                else:
                    return ""
            except Exception:
                return ""
            count = len(buf_text)
            return f"Received: {masked}  ({count} chars)"

        with create_app_session(input=pt_input, output=pt_output):
            value = session.prompt(
                prompt_text,
                is_password=is_password,
                default=(default or ""),
                key_bindings=kb,
                bottom_toolbar=_bottom_toolbar,
            )
        if cancelled["value"]:
            return None
        return value
    except Exception:
        pass

    # Fallback path: robust TTY handling
    # If not a TTY, use plain input() with a 'back' sentinel
    if not sys.stdin.isatty():
        try:
            prompt_display = f"\n{label}: " if not default else f"\n{label} ({default}): "
            _drain_stdin()
            resp = input(prompt_display)
            if resp is None:
                return None
            resp = resp.strip()
            if resp.lower() in {"back", "b"}:
                return None
            if not resp and default is not None:
                return default
            return resp
        except Exception:
            return None

    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_attrs = termios.tcgetattr(fd)
        new_attrs = termios.tcgetattr(fd)
        if is_password:
            new_attrs[3] = new_attrs[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
        tty.setcbreak(fd)

        _drain_stdin()
        prompt_display = f"\n{label}: " if not default else f"\n{label} ({default}): "
        sys.stdout.write(prompt_display)
        sys.stdout.flush()

        buf: list[str] = []

        def _render_status_line(clear: bool = False) -> None:
            if not is_password:
                return
            try:
                current_text = "".join(buf)
                count = len(current_text)
                sys.stdout.write("\x1b7")  # save cursor
                sys.stdout.write("\x1b[1B")  # move cursor down 1 line
                sys.stdout.write("\r")  # move to column 1
                sys.stdout.write("\x1b[2K")  # clear entire line
                if not clear:
                    if count >= 10:
                        try:
                            preview = mask_strict_last4(current_text)
                        except Exception:
                            preview = "••••"
                        msg = f"Received: {preview}  ({count} chars)"
                    elif count >= 4:
                        msg = f"Received: ••••  ({count} chars)"
                    else:
                        msg = ""
                    if msg:
                        sys.stdout.write(msg)
                sys.stdout.write("\x1b8")  # restore cursor
                sys.stdout.flush()
            except Exception:
                pass

        while True:
            ch = os.read(fd, 1)
            if not ch:
                break
            c = ch.decode(errors="ignore")
            if c in ("\n", "\r"):
                _render_status_line(clear=True)
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if c == "\x1b":  # ESC
                sys.stdout.write("\n")
                sys.stdout.flush()
                buf = []
                return None
            if c == "\x7f":  # backspace
                if buf:
                    buf.pop()
                    if not is_password:
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    else:
                        _render_status_line()
                continue
            if ord(c) < 32:
                continue
            buf.append(c)
            if not is_password:
                sys.stdout.write(c)
                sys.stdout.flush()
            else:
                _render_status_line()

        val = "".join(buf).strip()
        if not val and default is not None:
            return default
        return val
    except Exception:
        return None
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSANOW, old_attrs)  # type: ignore[name-defined]
        except Exception:
            pass


def confirm_with_escape(question: str, default: bool = True) -> bool | None:
    """Confirm where ESC returns None (go back)."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input import create_input
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.output import create_output

        kb = KeyBindings()
        cancelled = {"value": False}

        @kb.add("escape")
        def _esc(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        @kb.add("c-[")
        def _ctrl_lbracket(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        @kb.add("c-g")
        def _ctrl_g(event):  # type: ignore
            cancelled["value"] = True
            event.app.exit(result=None)

        pt_input = create_input()
        pt_output = create_output()
        session = PromptSession(input=pt_input, output=pt_output)
        suffix = "[Y/n]" if default else "[y/N]"
        prompt_text = f"\n{question} {suffix} "
        with create_app_session(input=pt_input, output=pt_output):
            value = session.prompt(prompt_text, key_bindings=kb)
        if cancelled["value"]:
            return None
        if not value.strip():
            return default
        v = value.strip().lower()
        if v in {"y", "yes"}:
            return True
        if v in {"n", "no"}:
            return False
        return default
    except Exception:
        pass

    # Fallback without prompt_toolkit
    try:

        def _strip_markup(text: str) -> str:
            try:
                return re.sub(r"\[/?.*?\]", "", text)
            except Exception:
                return text

        suffix = "[Y/n]" if default else "[y/N]"
        clean_q = _strip_markup(question).strip() or "Are you sure?"
        while True:
            _drain_stdin()
            try:
                resp = input(f"\n{clean_q} {suffix} (type 'back' to return): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return default
            if not resp:
                return default
            if resp in {"y", "yes"}:
                return True
            if resp in {"n", "no"}:
                return False
            if resp in {"back", "b"}:
                _drain_stdin()
                return None
            print("Please enter Y, N, or 'back'")
    except Exception:
        return default


_NOISE_FULL_RE = re.compile(r"^\x1b\[[0-9;?]*[A-Za-z]$")
_NOISE_ANY_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def readline_sanitized(prompt_text: str) -> str | None:
    """Read a line while ignoring stray terminal escape reports."""
    try:
        import fcntl
        import select
        import termios
        import tty

        fd = sys.stdin.fileno()
        if not sys.stdin.isatty():
            return input(prompt_text)

        old_attrs = termios.tcgetattr(fd)
        new_attrs = termios.tcgetattr(fd)
        new_attrs[3] = new_attrs[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
        tty.setcbreak(fd)

        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

        try:
            sys.stdout.write(prompt_text)
            sys.stdout.flush()
            buf: list[str] = []
            while True:
                r, _, _ = select.select([fd], [], [], 0.5)
                if not r:
                    continue
                try:
                    ch = os.read(fd, 1)
                except BlockingIOError:
                    continue
                if not ch:
                    return ""
                c = ch.decode(errors="ignore")
                if c in {"\n", "\r"}:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return "".join(buf)
                if c == "\x7f":
                    if buf:
                        buf.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue
                if c == "\x1b":
                    seq = c
                    for _ in range(16):
                        r2, _, _ = select.select([fd], [], [], 0.01)
                        if not r2:
                            break
                        try:
                            ch2 = os.read(fd, 1)
                        except BlockingIOError:
                            break
                        if not ch2:
                            break
                        seq += ch2.decode(errors="ignore")
                        if _NOISE_ANY_RE.search(seq):
                            break
                    continue
                if c.isdigit() or c in {" ", ",", "-"}:
                    buf.append(c)
                    sys.stdout.write(c)
                    sys.stdout.flush()
                    continue
        finally:
            try:
                fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
                termios.tcsetattr(fd, termios.TCSANOW, old_attrs)
            except Exception:
                pass
    except Exception:
        try:
            return input(prompt_text)
        except EOFError:
            return None


def simple_choice_prompt(prompt_text: str, choices: list, default: str | None = None) -> str:
    while True:
        if default:
            prompt_display = f"{prompt_text} [{'/' .join(choices)}] ({default}): "
        else:
            prompt_display = f"{prompt_text} [{'/' .join(choices)}]: "
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            response = input(prompt_display).strip()
            if not response and default:
                return default
            if response in choices:
                return response
            print("Please select one of the available options")
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(1)
