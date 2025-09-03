"""Centralized CLI error handling utilities.

Provides a lightweight decorator that commands can use to route exceptions
through the owning BaseCommand instance's error handlers. This allows us to
remove broad try/except blocks in command bodies and keep output consistent.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

import click

from flow.errors import AuthenticationError

F = TypeVar("F", bound=Callable[..., Any])


def cli_error_guard(owner: Any) -> Callable[[F], F]:
    """Decorator factory that routes exceptions to a command owner's handlers.

    The owner is expected to expose `handle_error(Exception|str)` and
    `handle_auth_error()` methods (as provided by BaseCommand).
    """

    def _decorate(func: F) -> F:
        @functools.wraps(func)
        def _wrapped(*args: Any, **kwargs: Any):  # type: ignore[override]
            try:
                return func(*args, **kwargs)
            except click.Abort:
                # Graceful Ctrl+C/abort from Click prompts
                try:
                    from flow.cli.commands.base import console as _console  # lazy to avoid cycles

                    _console.print("[dim]Cancelled[/dim]")
                except Exception:
                    pass
                raise click.exceptions.Exit(130)
            except click.ClickException:
                # Let Click manage its own exceptions
                raise
            except click.exceptions.Exit:
                # Respect explicit exits from owners or Click
                raise
            except KeyboardInterrupt:
                # Graceful Ctrl+C
                try:
                    from flow.cli.commands.base import console as _console  # lazy to avoid cycles

                    _console.print("[dim]Cancelled[/dim]")
                except Exception:
                    pass
                raise click.exceptions.Exit(130)
            except AuthenticationError:
                # Route to owner's auth helper for rich guidance
                try:
                    owner.handle_auth_error()
                finally:
                    raise click.exceptions.Exit(1)
            except Exception as e:  # noqa: BLE001 - centralized, intentional
                # Default: rich error panel via owner
                owner.handle_error(e)
                # handle_error raises click.Exit; if it didn't, ensure exit
                raise click.exceptions.Exit(1)

        return _wrapped  # type: ignore[return-value]

    return _decorate


def handle_cli_exception(owner: Any | None, exc: Exception) -> None:
    """Best-effort top-level handler for wrapping CLI entry invocation.

    If an owner is provided, route through it; otherwise, convert to Click exit.
    Not strictly necessary when using the decorator on commands, but useful
    as a belt-and-suspenders around the CLI entrypoint.
    """
    if isinstance(exc, click.Abort):
        try:
            from flow.cli.commands.base import console as _console  # lazy to avoid cycles

            _console.print("[dim]Cancelled[/dim]")
        except Exception:
            pass
        raise click.exceptions.Exit(130)
    if isinstance(exc, click.ClickException) or isinstance(exc, click.exceptions.Exit):
        raise exc
    if isinstance(exc, KeyboardInterrupt):
        try:
            from flow.cli.commands.base import console as _console  # lazy to avoid cycles

            _console.print("[dim]Cancelled[/dim]")
        except Exception:
            pass
        raise click.exceptions.Exit(130)
    if owner is not None and isinstance(exc, AuthenticationError):
        owner.handle_auth_error()
        raise click.exceptions.Exit(1)
    if owner is not None:
        owner.handle_error(exc)
        raise click.exceptions.Exit(1)
    # No owner to render with; fail with a simple message
    raise click.ClickException(str(exc))
