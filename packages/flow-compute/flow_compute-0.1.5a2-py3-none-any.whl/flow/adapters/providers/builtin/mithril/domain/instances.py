"""Instance-related helpers and services for the Mithril provider.

Provides instance fetch and normalization utilities and an orchestration
method to build `Instance` models for a task's bid.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from flow.adapters.providers.builtin.mithril.adapters.models import MithrilAdapter
from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.models import MithrilBid, MithrilInstance
from flow.errors import ResourceNotFoundError
from flow.sdk.models import Instance, InstanceStatus


class InstanceService:
    """Service to fetch and adapt instance data for tasks."""

    def __init__(self, api: MithrilApiClient, get_project_id: Callable[[], str]) -> None:
        self._api = api
        self._get_project_id = get_project_id

    def get_instance(self, instance_id: str) -> dict:
        """Fetch detailed instance information by ID.

        Prefer the project-scoped /v2/instances view (authoritative, up-to-date),
        then fall back to /v2/spot/instances. If both return documents, prefer a
        non-terminated one; otherwise return the project view.
        """
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:
            try:
                import os as _os

                debug = _os.environ.get("FLOW_SSH_DEBUG") == "1"
            except Exception:
                debug = False

        project_doc: dict | None = None
        spot_doc: dict | None = None

        # 1) Project-scoped authoritative view: page by project and filter locally by fid/id
        try:
            project_id = self._get_project_id()
        except Exception:
            project_id = None

        if project_id:
            try:
                next_cursor: str | None = None
                for _ in range(10):
                    params = {"project": project_id}
                    # Prefer newest first when supported
                    params["sort_by"] = "created_at"
                    params["sort_dir"] = "desc"
                    if next_cursor:
                        params["next_cursor"] = next_cursor
                    resp_proj = self._api.list_instances(params)
                    items = (
                        resp_proj.get("data", resp_proj)
                        if isinstance(resp_proj, dict)
                        else resp_proj
                    )
                    if isinstance(items, list):
                        for d in items:
                            if not isinstance(d, dict):
                                continue
                            fid = d.get("fid") or d.get("id")
                            if fid == instance_id:
                                project_doc = d
                                break
                    if project_doc is not None:
                        break
                    next_cursor = (
                        resp_proj.get("next_cursor") if isinstance(resp_proj, dict) else None
                    )
                    if not next_cursor:
                        break
            except Exception:
                project_doc = None

        # 2) Spot view fallback
        try:
            resp_spot = self._api.list_spot_instances({"id": instance_id})
            items = resp_spot.get("data", resp_spot) if isinstance(resp_spot, dict) else resp_spot
            if isinstance(items, list) and items:
                # If multiple, prefer the first live one
                def _is_live(x: dict) -> bool:
                    st = str(x.get("status", "")).lower()
                    return not ("termin" in st or "cancel" in st)

                lives = [x for x in items if isinstance(x, dict) and _is_live(x)]
                spot_doc = (lives[0] if lives else items[0]) if items else None
        except Exception:
            spot_doc = None

        if debug:
            print(
                f"[get_instance] id={instance_id} proj_status={(project_doc or {}).get('status')} proj_ssh={(project_doc or {}).get('ssh_destination')} spot_status={(spot_doc or {}).get('status')} spot_ssh={(spot_doc or {}).get('ssh_destination')}"
            )

        if not project_doc and not spot_doc:
            raise ResourceNotFoundError(f"Instance {instance_id} not found")

        def _is_live(doc: dict | None) -> bool:
            if not isinstance(doc, dict):
                return False
            st = str(doc.get("status", "")).lower()
            return not ("termin" in st or "cancel" in st)

        # Prefer live doc if any; otherwise project view
        if _is_live(project_doc):
            return project_doc
        if _is_live(spot_doc) and not _is_live(project_doc):
            return spot_doc
        return project_doc or spot_doc

    def list_project_instances_by_bid(self, bid_id: str, max_pages: int = 3) -> list[dict]:
        """List all instance docs in the current project that belong to a bid.

        Spec-compliant: pages /v2/instances?project=<proj> and filters locally by .bid == bid_id.
        """
        project_id = self._get_project_id()
        docs: list[dict] = []
        next_cursor: str | None = None
        for _ in range(max_pages):
            params: dict[str, str] = {"project": project_id}
            if next_cursor:
                params["next_cursor"] = next_cursor
            resp = self._api.list_instances(params)
            items = resp.get("data", resp) if isinstance(resp, dict) else resp
            if isinstance(items, list):
                for d in items:
                    if isinstance(d, dict) and (
                        d.get("bid") == bid_id or d.get("bid_id") == bid_id
                    ):
                        docs.append(d)
            next_cursor = resp.get("next_cursor") if isinstance(resp, dict) else None
            if not next_cursor:
                break

        def _key(doc: dict) -> str:
            return str(doc.get("created_at", ""))

        docs = sorted(docs, key=_key)

        # Fallback: some deployments expose instances only under /v2/spot/instances
        # Try that path when project-scoped listing yields nothing.
        if not docs:
            try:
                resp = self._api.list_spot_instances({"bid": bid_id})
                items = resp.get("data", resp) if isinstance(resp, dict) else resp
                if isinstance(items, list):
                    # Normalize schema differences and filter by bid
                    norm: list[dict] = []
                    for d in items:
                        if not isinstance(d, dict):
                            continue
                        if d.get("bid") != bid_id and d.get("bid_id") != bid_id:
                            continue
                        norm.append(d)
                    # Keep newest-first consistent with project view
                    docs = sorted(norm, key=_key)
            except Exception:
                pass

        return docs

    def list_for_bid(self, bid: dict, task_id: str) -> list[Instance]:
        """Build `Instance` models for all instance IDs in the bid."""
        instances: list[Instance] = []
        instance_ids = bid.get("instances", [])
        for instance_id in instance_ids:
            if isinstance(instance_id, str):
                try:
                    data = self.get_instance(instance_id)
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**data), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception:
                    instances.append(
                        Instance(
                            instance_id=instance_id,
                            task_id=task_id,
                            status=InstanceStatus.PENDING,
                            created_at=datetime.now(),
                        )
                    )
            elif isinstance(instance_id, dict):
                try:
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**instance_id), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception:
                    # Skip malformed instance dicts gracefully
                    continue
        return instances
