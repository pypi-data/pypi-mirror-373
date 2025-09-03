from __future__ import annotations

from collections.abc import Iterable, Sequence

import click


class EnvItem(click.ParamType):
    name = "KEY=VALUE"

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            text = str(value)
        except Exception:
            self.fail("Invalid env item", param, ctx)
        if "=" not in text:
            self.fail("Expected KEY=VALUE (e.g., FOO=bar)", param, ctx)
        key, val = text.split("=", 1)
        key = key.strip()
        if not key:
            self.fail("KEY cannot be empty in KEY=VALUE", param, ctx)
        return (key, val)


def parse_ports_expression(expression: str) -> list[int]:
    import re

    tokens = re.split(r"[\s,]+", (expression or "").strip())
    parsed: list[int] = []
    for token in tokens:
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            try:
                start = int(left.strip())
                end = int(right.strip())
            except Exception:
                raise ValueError(f"Invalid range format: '{token}'")
            if start > end:
                start, end = end, start
            if end - start + 1 > 2000:
                raise ValueError(f"Range too large (max 2000): '{token}'")
            parsed.extend(range(start, end + 1))
        else:
            try:
                parsed.append(int(token))
            except Exception:
                raise ValueError(f"Invalid port number: '{token}'")
    return sorted(set(parsed))


class PortsExpr(click.ParamType):
    """Parses comma/space/range expressions into a list of ports.

    Example: "8080,8888 3000-3002" -> [3000, 3001, 3002, 8080, 8888]
    """

    name = "PORTS"

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            ports = parse_ports_expression(str(value))
        except ValueError as ve:
            raise click.BadParameter(str(ve))
        return ports


def merge_ports_expr(values: Sequence[Sequence[int]]) -> list[int]:
    merged: list[int] = []
    for seq in values or ():
        merged.extend(seq or [])
    return sorted(set(int(p) for p in merged))


def validate_ports_range(
    ports: Iterable[int], *, min_port: int, max_port: int, allowed_extras: set[int] | None = None
) -> list[int]:
    allowed_extras = allowed_extras or set()
    cleaned: list[int] = []
    for p in ports or ():
        pi = int(p)
        if pi in allowed_extras:
            cleaned.append(pi)
            continue
        if pi < min_port or pi > max_port:
            raise click.BadParameter(
                f"Invalid port {pi}. Allowed: {', '.join(map(str, sorted(allowed_extras)))} or {min_port}-{max_port}"
            )
        cleaned.append(pi)
    return sorted(set(cleaned))


class PortNumber(click.ParamType):
    """Validates a single port number in range 1-65535 by default."""

    name = "PORT"

    def __init__(self, *, min_port: int = 1, max_port: int = 65535):
        self.min_port = int(min_port)
        self.max_port = int(max_port)

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            pi = int(value)
        except Exception:
            raise click.BadParameter("Port must be an integer")
        if pi < self.min_port or pi > self.max_port:
            raise click.BadParameter(f"Port must be in range {self.min_port}-{self.max_port}")
        return pi
