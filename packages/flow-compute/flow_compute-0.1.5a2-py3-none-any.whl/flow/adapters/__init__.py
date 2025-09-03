"""Adapters: concrete integrations that touch the outside world.

This package implements the ports defined in ``flow.protocols`` and is the
outer edge of the system. Adapters translate Flow's internal contracts into
provider- or tool-specific APIs (HTTP, SSH, logging, metrics, storage, etc.).

Guidelines:
  - Implements protocols; does not define domain concepts.
  - May depend on ``flow.protocols``, ``flow.domain`` (types), and ``flow.core``
    utilities. Must not be imported by ``flow.domain`` or ``flow.protocols``.
  - Keep imports local where possible to avoid heavy import-time costs.

Notable subpackages:
  - ``providers``: Cloud/back-end provider integrations and registries.
  - ``frontends``: Legacy adapter discovery (see ``flow.plugins`` for new).
  - ``http``/``transport``/``ssh``: Network and RPC transports.
  - ``logging``/``metrics``: Instrumentation hooks.
  - ``caching``/``resilience``/``startup``/``outbound``: Operational utilities.

This file exists so tooling that lacks full namespace support recognizes
``flow.adapters`` when building import graphs.
"""

__all__ = [
    "frontends",
    "http",
    "logging",
    "metrics",
    "providers",
    "transport",
]
