from __future__ import annotations

import shlex
import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.utils.paths import WORKSPACE_DIR


class CodeUploadSection(ScriptSection):
    @property
    def name(self) -> str:
        return "code_upload"

    @property
    def priority(self) -> int:
        return 35

    def should_include(self, context: ScriptContext) -> bool:
        return context.upload_code and context.code_archive is not None

    def generate(self, context: ScriptContext) -> str:
        if not context.upload_code or not context.code_archive:
            return ""
        _safe_ws = shlex.quote(WORKSPACE_DIR)
        return textwrap.dedent(
            rf"""
            echo "Extracting uploaded code to {WORKSPACE_DIR}..."
            mkdir -p {_safe_ws}
            cd {_safe_ws}
            # Harden extraction: prevent absolute paths and traversal outside workspace
            ARCHIVE_CONTENT="{context.code_archive}"
            if [ -z "$ARCHIVE_CONTENT" ]; then
              echo "No archive content provided" >&2; exit 1; fi
            TMP_ARCHIVE=$(mktemp -t flow_code_XXXXXX.tar.gz)
            echo "$ARCHIVE_CONTENT" | base64 -d > "$TMP_ARCHIVE"
            # Validate tarball entries: reject absolute paths and parent directory traversal
            if tar -tzf "$TMP_ARCHIVE" | grep -E "^(\/|.*(\.|\.\.)($|\/))" >/dev/null 2>&1; then
              echo "Unsafe archive contents detected (absolute paths or traversal)" >&2
              rm -f "$TMP_ARCHIVE"
              exit 1
            fi
            # Extract safely
            tar --no-same-owner --no-overwrite-dir -xzf "$TMP_ARCHIVE" -C {_safe_ws}
            rm -f "$TMP_ARCHIVE"
            # Permissions: directories 755, files 644 by default
            find {_safe_ws} -type d -exec chmod 755 {{}} +
            find {_safe_ws} -type f -exec chmod 644 {{}} +
        """
        ).strip()


__all__ = ["CodeUploadSection"]
