"""Deprecated CLI shim importing core masking utilities.

Use ``flow.sdk.helpers.masking`` instead of this module.
"""

import warnings

from flow.sdk.helpers.masking import *  # noqa: F403

warnings.warn(
    "flow.cli.utils.mask_utils is deprecated; use flow.sdk.helpers.masking",
    DeprecationWarning,
    stacklevel=2,
)
