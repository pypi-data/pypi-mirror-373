"""Mount adaptation service.

Converts high-level mount specs (e.g., S3 URLs) into environment variables and
attachment specs expected by startup scripts and bid payload.
"""

from __future__ import annotations

import os

from flow.core.mounts.planner import PlannedMount
from flow.sdk.models import TaskConfig


class MountsService:
    def inject_env_for_s3(self, config: TaskConfig) -> TaskConfig:
        """Propagate AWS creds from env into config.env if missing, used by s3fs."""
        env_updates = {}
        if "AWS_ACCESS_KEY_ID" not in (config.env or {}) and os.environ.get("AWS_ACCESS_KEY_ID"):
            env_updates["AWS_ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
        if "AWS_SECRET_ACCESS_KEY" not in (config.env or {}) and os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        ):
            env_updates["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_SECRET_ACCESS_KEY"]
        if "AWS_SESSION_TOKEN" not in (config.env or {}) and os.environ.get("AWS_SESSION_TOKEN"):
            env_updates["AWS_SESSION_TOKEN"] = os.environ["AWS_SESSION_TOKEN"]
        if env_updates:
            return config.model_copy(update={"env": {**(config.env or {}), **env_updates}})
        return config

    def apply_planned_mounts(self, config: TaskConfig, plans: list[PlannedMount]) -> TaskConfig:
        """Translate PlannedMounts into Mithril-ready config updates.

        - s3fs: set S3_MOUNT_* env vars consumed by startup script
        - bind: no-op here (handled by container/local paths)
        - volume: no-op here; attachment handled elsewhere
        """
        if not plans:
            return config
        env = dict(config.env or {})
        s3_index = 0
        for p in plans:
            if p.mount_type == "s3fs":
                prefix = f"S3_MOUNT_{s3_index}"
                # Best-effort parse of s3://bucket/path
                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(p.source)
                    bucket = parsed.netloc
                    path = parsed.path.lstrip("/")
                except Exception:
                    bucket, path = "", ""
                if bucket:
                    env[f"{prefix}_BUCKET"] = bucket
                    env[f"{prefix}_PATH"] = path
                    env[f"{prefix}_TARGET"] = p.target
                    s3_index += 1
        if s3_index > 0:
            env["S3_MOUNTS_COUNT"] = str(s3_index)
        if env != (config.env or {}):
            return config.model_copy(update={"env": env})
        return config
