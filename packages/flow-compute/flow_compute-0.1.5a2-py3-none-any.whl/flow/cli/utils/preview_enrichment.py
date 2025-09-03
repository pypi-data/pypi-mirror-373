from __future__ import annotations

import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

_DETAIL_TTL_SECONDS: float = 15.0
_detail_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_inflight: set[str] = set()


def _now() -> float:
    return time.time()


def _ssh_key_fingerprint_sha256(key_path: str) -> str | None:
    """Return short SHA256 fingerprint for an SSH key if possible.

    Tries `<key>.pub` first, then the private key. Returns None on failure.
    Keeps timeouts very small to avoid affecting UX.
    """
    if not key_path:
        return None
    try_paths = []
    try:
        p = Path(key_path)
        try_paths = [str(p.with_suffix(p.suffix + ".pub")), str(p)]
    except Exception:
        try_paths = [f"{key_path}.pub", key_path]

    for candidate in try_paths:
        try:
            if not os.path.exists(candidate):
                continue
            out = subprocess.run(
                ["ssh-keygen", "-lf", candidate, "-E", "sha256"],
                capture_output=True,
                text=True,
                check=False,
                timeout=0.6,
            )
            if out.returncode == 0 and out.stdout:
                # Typical: "2048 SHA256:abc... user@host (RSA)"
                parts = out.stdout.strip().split()
                if len(parts) >= 2 and parts[1].startswith("SHA256:"):
                    return parts[1].replace("SHA256:", "")
        except Exception:
            continue
    return None


def _fetch_details(flow_client: Any, task_id: str, task_obj: Any) -> None:
    try:
        provider = getattr(flow_client, "provider", None)
        ssh_key_path = None
        try:
            # Use the flow client API to resolve the SSH key path for preview.
            # This mirrors the path used by remote ops and keeps project scoping consistent.
            if flow_client is not None:
                ssh_key_path, _ = flow_client.get_task_ssh_connection_info(task_id)
        except Exception:
            ssh_key_path = None

        details: dict[str, Any] = {
            "ssh_host": getattr(task_obj, "ssh_host", None),
            "ssh_user": getattr(task_obj, "ssh_user", None),
            "ssh_port": getattr(task_obj, "ssh_port", 22) or 22,
            "ssh_key_path": ssh_key_path,
            "ssh_key_fp": _ssh_key_fingerprint_sha256(ssh_key_path) if ssh_key_path else None,
            # Heuristic mounts/volumes surface from task.extra
            "mounts": list((getattr(task_obj, "extra", {}) or {}).get("mounts", []) or []),
            "ip": getattr(task_obj, "public_ip", None)
            or getattr(task_obj, "ip_address", None)
            or getattr(task_obj, "ssh_host", None),
        }
        _detail_cache[task_id] = (_now(), details)
        # Nudge prompt_toolkit UI to refresh so custom preview renderers update immediately
        try:
            from prompt_toolkit.application.current import get_app  # type: ignore

            app = get_app(return_none=True)
            if app:
                app.invalidate()
        except Exception:
            # Best-effort; ignore if prompt_toolkit is not active
            pass
    finally:
        _inflight.discard(task_id)


def get_preview_details(flow_client: Any, task_obj: Any) -> dict[str, Any] | None:
    """Return cached preview details, kick off async fetch if stale/missing.

    This function never blocks. It returns None when details are not ready yet.
    """
    task_id = getattr(task_obj, "task_id", None) or getattr(task_obj, "id", None)
    if not task_id:
        return None

    cached = _detail_cache.get(task_id)
    if cached and (_now() - cached[0]) < _DETAIL_TTL_SECONDS:
        return cached[1]

    if task_id not in _inflight:
        _inflight.add(task_id)
        threading.Thread(
            target=_fetch_details, args=(flow_client, task_id, task_obj), daemon=True
        ).start()

    return None
