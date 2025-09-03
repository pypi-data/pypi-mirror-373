"""Application wiring for the interactive selector.

This module encapsulates prompt_toolkit Application creation and the
environment/session handling required to run the interactive selector
reliably across environments (including nested event loops and CPR quirks).
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from prompt_toolkit import Application
from prompt_toolkit.application import create_app_session
from prompt_toolkit.key_binding import KeyBindings

if TYPE_CHECKING:
    from flow.cli.ui.components.selector import InteractiveSelector


def _create_io_bindings() -> tuple[object | None, object | None, object | None]:
    """Create prompt_toolkit input/output objects with a best-effort /dev/tty binding.

    Returns a tuple of (pt_input, pt_output, dev_tty_handle).
    The dev_tty_handle should be kept by the caller and closed when done.
    """
    try:
        from prompt_toolkit.input import create_input  # type: ignore
        from prompt_toolkit.output import create_output  # type: ignore
    except Exception:
        return None, None, None

    pt_input = None
    pt_output = None
    dev_tty_handle = None

    # Prefer /dev/tty when explicitly forced or stdio isn't a TTY
    use_dev_tty = bool(os.environ.get("FLOW_FORCE_INTERACTIVE")) or not sys.stdin.isatty()
    if use_dev_tty:
        try:
            dev_tty_handle = open("/dev/tty", "r+")
            pt_input = create_input(stdin=dev_tty_handle)
            pt_output = create_output(stdout=dev_tty_handle)
        except Exception:
            # Fallback to default stdio
            dev_tty_handle = None
            pt_input = create_input()
            pt_output = create_output()
    else:
        try:
            pt_input = create_input()
            pt_output = create_output()
        except Exception:
            pt_input = pt_output = None

    return pt_input, pt_output, dev_tty_handle


def create_selector_application(selector: InteractiveSelector) -> Application:
    """Build a prompt_toolkit Application for the given selector.

    This function delegates keybinding and layout construction to the selector
    to preserve behavior, while centralizing Application wiring here.
    """
    kb = KeyBindings()

    # Delegate binding groups to the selector's helpers
    selector._bind_navigation(kb)  # type: ignore[attr-defined]
    selector._bind_selection(kb)  # type: ignore[attr-defined]
    selector._bind_search(kb)  # type: ignore[attr-defined]
    selector._bind_exit_and_help(kb)  # type: ignore[attr-defined]

    # Create layout via selector
    layout = selector._create_layout()  # type: ignore[attr-defined]

    # Robust I/O binding
    pt_input, pt_output, dev_tty_handle = _create_io_bindings()
    selector._dev_tty_handle = dev_tty_handle  # type: ignore[attr-defined]

    return Application(
        layout=layout,
        key_bindings=kb,
        full_screen=False,  # inline to avoid aggressive TTY state changes
        mouse_support=False,
        erase_when_done=True,
        refresh_interval=0.5,
        input=pt_input,
        output=pt_output,
    )


def run_selector(selector: InteractiveSelector) -> object | None:
    """Run the selector's Application with robust environment handling.

    Handles CPR suppression, nested event loops, and returns the selected result.
    """
    # Build application and start monitoring for updates
    selector.app = create_selector_application(selector)
    selector._start_monitoring()  # type: ignore[attr-defined]

    # Suppress CPR queries that can confuse certain terminals
    old_cpr = os.environ.get("PROMPT_TOOLKIT_NO_CPR")
    os.environ["PROMPT_TOOLKIT_NO_CPR"] = "1"

    # Hide the terminal cursor during interactive selection
    _out = getattr(selector.app, "output", None)

    def _supports(obj: object | None, name: str) -> bool:
        return obj is not None and callable(getattr(obj, name, None))

    def _write_escape(out: object, seq: str) -> None:
        if _supports(out, "write_raw"):
            out.write_raw(seq)  # type: ignore[attr-defined]
        elif _supports(out, "write"):
            out.write(seq)  # type: ignore[attr-defined]
        else:
            raise AttributeError("Output does not support write/write_raw")

    def _hide_cursor(out: object | None) -> bool:
        """Best-effort hide; returns True if we attempted successfully."""
        if out is None:
            return False
        try:
            if _supports(out, "hide_cursor"):
                out.hide_cursor()  # type: ignore[attr-defined]
                return True
            _write_escape(out, "\x1b[?25l")
            return True
        except Exception:
            return False

    def _show_cursor(out: object | None) -> None:
        """Best-effort restore of cursor visibility."""
        if out is None:
            return
        try:
            if _supports(out, "show_cursor"):
                out.show_cursor()  # type: ignore[attr-defined]
                return
            _write_escape(out, "\x1b[?25h")
        except Exception:
            pass

    _cursor_hidden = _hide_cursor(_out)

    try:
        # Prefer binding the session to the same input/output as the Application
        session_kwargs: dict[str, object] = {}
        try:
            if selector.app is not None and getattr(selector.app, "input", None) is not None:
                session_kwargs["input"] = selector.app.input  # type: ignore[attr-defined]
            if selector.app is not None and getattr(selector.app, "output", None) is not None:
                session_kwargs["output"] = selector.app.output  # type: ignore[attr-defined]
        except Exception:
            session_kwargs = {}

        with create_app_session(**session_kwargs):
            # Run synchronously when possible; otherwise offload to a worker thread
            import asyncio as _asyncio

            try:
                _loop = _asyncio.get_running_loop()
                _is_running = _loop.is_running()
            except RuntimeError:
                _is_running = False

            if _is_running:

                def _run_sync_app():
                    return selector.app.run() if selector.app else None

                with ThreadPoolExecutor(max_workers=1) as _ex:
                    future = _ex.submit(_run_sync_app)
                    result = future.result()
            else:
                result = selector.app.run() if selector.app else None
    finally:
        # Restore cursor visibility if we hid it
        if _cursor_hidden:
            _show_cursor(_out)
        # Restore CPR setting
        if old_cpr is None:
            os.environ.pop("PROMPT_TOOLKIT_NO_CPR", None)
        else:
            os.environ["PROMPT_TOOLKIT_NO_CPR"] = old_cpr

    return result if result is not None else selector.result
