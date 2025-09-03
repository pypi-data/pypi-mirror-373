from __future__ import annotations

import logging as _log
import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import ensure_command_available
from flow.utils.paths import S3FS_CACHE_DIR, S3FS_PASSWD_FILE


class S3Section(ScriptSection):
    @property
    def name(self) -> str:
        return "s3_mounts"

    @property
    def priority(self) -> int:
        return 35

    def should_include(self, context: ScriptContext) -> bool:
        return any(
            k.startswith("S3_MOUNT_") and k.endswith("_BUCKET") for k in context.environment.keys()
        )

    def generate(self, context: ScriptContext) -> str:
        mount_count = int(context.environment.get("S3_MOUNTS_COUNT", "0"))
        if mount_count == 0:
            return ""

        mount_snippets: list[str] = []
        # Validate mount_count to avoid unreasonable loops
        if mount_count < 0 or mount_count > 1000:
            return ""
        for i in range(mount_count):
            mount_key = f"S3_MOUNT_{i}"
            bucket = context.environment.get(f"{mount_key}_BUCKET")
            path = context.environment.get(f"{mount_key}_PATH", "")
            target = context.environment.get(f"{mount_key}_TARGET")
            # Basic validation of bucket and target to reduce injection risk in rendered shell
            if bucket and target and isinstance(bucket, str) and isinstance(target, str):
                # Disallow newline or shell metacharacters in bucket/target
                import re as _re

                if _re.search(r"[\n\r`$]", bucket) or _re.search(r"[\n\r`$]", target):
                    continue
                s3_path = f"{bucket}:/{path}" if path else bucket
                if getattr(self, "template_engine", None):
                    try:
                        from pathlib import Path as _Path

                        mount_snippets.append(
                            self.template_engine.render_file(
                                _Path("sections/s3_mount_item.sh.j2"),
                                {
                                    "bucket": bucket,
                                    "path": path,
                                    "target": target,
                                    "index": i,
                                    "s3_path": s3_path,
                                },
                            ).strip()
                        )
                        continue
                    except Exception:
                        _log.debug(
                            "S3Section: template render failed; falling back to inline script",
                            exc_info=True,
                        )
                mount_snippets.append(self._generate_s3_mount(bucket, path, target, i))

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/s3_mount.sh.j2"),
                    {
                        "ensure_s3fs_cmd": ensure_command_available("s3fs"),
                        "mount_commands": "\n".join(mount_snippets),
                    },
                ).strip()
            except Exception:
                _log.debug(
                    "S3Section: template render failed for s3_mount.sh.j2; using inline",
                    exc_info=True,
                )

        mount_blob = "\n".join(mount_snippets)
        # Use double braces to avoid Python f-string interpreting shell variables
        # and to keep literal ${VAR} in the generated script
        return textwrap.dedent(
            f"""
            # S3 mounting via s3fs
            echo "Setting up S3 mounts"
            {ensure_command_available("s3fs")}
            # Configure credential file if static creds are provided
            if [ -n "${{AWS_ACCESS_KEY_ID:-}}" ] && [ -n "${{AWS_SECRET_ACCESS_KEY:-}}" ]; then
                umask 077
                echo "${{AWS_ACCESS_KEY_ID}}:${{AWS_SECRET_ACCESS_KEY}}" > {S3FS_PASSWD_FILE}
                chmod 600 {S3FS_PASSWD_FILE}
            fi
            echo 'user_allow_other' >> /etc/fuse.conf || true
            {mount_blob}
            echo "S3 mounts configured:"
            mount | grep s3fs
            rm -f {S3FS_PASSWD_FILE} || true
        """
        ).strip()

    def _generate_s3_mount(self, bucket: str, path: str, target: str, index: int) -> str:
        s3_path = f"{bucket}:/{path}" if path else bucket
        return textwrap.dedent(
            f"""
            mkdir -p "{target}"
            S3FS_AUTH_OPTS=""
            if [ "${{USE_IAM_ROLE}}" = "true" ]; then
                S3FS_AUTH_OPTS="-o iam_role=auto"
            else
                S3FS_AUTH_OPTS="-o passwd_file={S3FS_PASSWD_FILE}"
            fi
            RW_OPT="-o ro"
            if [ "${{S3_MOUNTS_RW_ALL:-}}" = "1" ] || [ "${{S3_MOUNT_{index}_RW:-}}" = "1" ]; then
                RW_OPT=""  # allow writes
            fi
            s3fs "{s3_path}" "{target}" \
                ${{S3FS_AUTH_OPTS}} \
                ${{RW_OPT}} \
                -o allow_other \
                -o use_cache={S3FS_CACHE_DIR} \
                -o retries=5 \
                -o connect_timeout=10 \
                -o readwrite_timeout=30
            if mountpoint -q "{target}"; then echo "OK: {target}"; else echo "ERROR: {target}" >&2; exit 1; fi
        """
        ).strip()


__all__ = ["S3Section"]
