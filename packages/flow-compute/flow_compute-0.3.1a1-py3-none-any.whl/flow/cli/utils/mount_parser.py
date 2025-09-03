"""Deprecated: CLI shim for mount parser.

Do not import this module from core or providers. Use
``flow.core.mounts.parser.MountParser`` instead.
"""

import warnings


class MountParser:  # pragma: no cover - thin shim
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "flow.cli.utils.mount_parser.MountParser is deprecated; "
            "use flow.core.mounts.parser.MountParser",
            DeprecationWarning,
            stacklevel=2,
        )

    def __getattr__(self, name):
        from flow.core.mounts.parser import MountParser as _CoreParser

        return getattr(_CoreParser(), name)
