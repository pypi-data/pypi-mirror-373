"""Thin Mithril API client wrappers.

Provides minimal, typed wrappers over ``HttpClientPort`` so higher layers do not
handcraft URLs/params everywhere. Error handling continues to be centralized via
``api.handlers``; these methods just perform the requests.
"""

from __future__ import annotations

from typing import Any

from flow.protocols.http import HttpClientProtocol


class MithrilApiClient:
    """Mithril API client wrapping ``HttpClientProtocol``.

    Args:
        http: Initialized HTTP client bound to Mithril base URL
    """

    def __init__(self, http: HttpClientProtocol) -> None:
        self._http = http

    # --------------- Identity ---------------
    def get_me(self) -> Any:
        """GET /v2/me to fetch current user profile."""
        return self._http.request(method="GET", url="/v2/me")

    def get_user(self, user_id: str) -> Any:
        """GET /v2/users/{id} to fetch a user profile."""
        return self._http.request(method="GET", url=f"/v2/users/{user_id}")

    # --------------- Users/Teams (v1 IAM) ---------------
    def get_user_teammates(self, user_id: str) -> Any:
        """GET /users/{user_id}/teammates (v1 IAM service, not under /v2).

        Notes:
            - This endpoint is served by the IAM/Platform stack on v1 paths.
            - Use the same base_url; the path omits the /v2 prefix.
        """
        from flow.adapters.providers.builtin.mithril.core.constants import (
            V1_USERS_TEAMMATES_PATH_TEMPLATE,
        )

        path = V1_USERS_TEAMMATES_PATH_TEMPLATE.format(user_id=user_id)
        return self._http.request(method="GET", url=path)

    # --------------- Volumes ---------------
    def create_volume(self, payload: dict[str, Any]) -> dict:
        """POST /v2/volumes to create a volume.

        Args:
            payload: JSON body with volume fields

        Returns:
            Response dict from API
        """
        return self._http.request(method="POST", url="/v2/volumes", json=payload)

    def delete_volume(self, volume_id: str) -> None:
        """DELETE /v2/volumes/{id}.

        Args:
            volume_id: Volume identifier
        """
        self._http.request(method="DELETE", url=f"/v2/volumes/{volume_id}")

    def list_volumes(self, params: dict[str, Any]) -> Any:
        """GET /v2/volumes with pagination and sorting.

        Args:
            params: Query parameters

        Returns:
            Raw response (list or dict with 'data')
        """
        return self._http.request(method="GET", url="/v2/volumes", params=params)

    # --------------- Projects ---------------
    def list_projects(self) -> Any:
        return self._http.request(method="GET", url="/v2/projects")

    # --------------- Instances ---------------
    def list_instances(self, params: dict[str, Any]) -> Any:
        return self._http.request(method="GET", url="/v2/instances", params=params)

    def list_spot_instances(self, params: dict[str, Any]) -> Any:
        """GET /v2/spot/instances to fetch spot instances (by id/project)."""
        return self._http.request(method="GET", url="/v2/spot/instances", params=params)

    # --------------- Spot Availability ---------------
    def list_spot_availability(self, params: dict[str, Any]) -> Any:
        return self._http.request(method="GET", url="/v2/spot/availability", params=params)

    # --------------- Bids ---------------
    def create_bid(self, payload: dict[str, Any]) -> Any:
        return self._http.request(method="POST", url="/v2/spot/bids", json=payload)

    def list_bids(self, params: dict[str, Any]) -> Any:
        return self._http.request(method="GET", url="/v2/spot/bids", params=params)

    def get_bid(self, bid_id: str) -> Any:
        """GET /v2/spot/bids/{id} to fetch bid/task details.

        Args:
            bid_id: Bid identifier

        Returns:
            Response dict from API containing bid details
        """
        return self._http.request(method="GET", url=f"/v2/spot/bids/{bid_id}")

    def delete_bid(self, bid_id: str) -> None:
        """DELETE /v2/spot/bids/{id} to cancel a bid/task."""
        self._http.request(method="DELETE", url=f"/v2/spot/bids/{bid_id}")

    def cancel_bid(self, bid_id: str) -> None:
        """Alias of delete_bid for semantic clarity in callers.

        Historically higher-level services referred to this operation as
        "cancel_bid". Provide a stable alias to avoid AttributeError while
        preserving the HTTP DELETE behavior.
        """
        self.delete_bid(bid_id)

    def patch_bid(self, bid_id: str, payload: dict[str, Any]) -> Any:
        """PATCH /v2/spot/bids/{id} to update bid fields (pause, volumes, etc.)."""
        return self._http.request(method="PATCH", url=f"/v2/spot/bids/{bid_id}", json=payload)

    # --------------- Catalog ---------------
    def list_instance_types(self, params: dict[str, Any]) -> Any:
        return self._http.request(method="GET", url="/v2/instance-types", params=params)

    # --------------- Legacy/Misc ---------------
    def list_legacy_auctions(self, params: dict[str, Any]) -> Any:
        """GET /auctions for legacy compatibility in certain test/mocks.

        Args:
            params: Query parameters (e.g., {"instance_type": "it_..."})

        Returns:
            Raw response (list or dict with 'auctions')
        """
        return self._http.request(method="GET", url="/auctions", params=params)

    # --------------- SSH Keys ---------------
    def list_ssh_keys(self, params: dict[str, Any] | None = None) -> Any:
        """GET /v2/ssh-keys to list SSH keys.

        Args:
            params: Optional query parameters (e.g., project scope)

        Returns:
            Raw response containing SSH key entries
        """
        return self._http.request(method="GET", url="/v2/ssh-keys", params=params or {})

    # --------------- API Keys ---------------
    def list_api_keys(self) -> Any:
        """GET /v2/api-keys to list API keys for the current user.

        Returns:
            Raw list response with API key entries
        """
        return self._http.request(method="GET", url="/v2/api-keys")

    def create_api_key(self, payload: dict[str, Any]) -> Any:
        """POST /v2/api-keys to create a new API key.

        Args:
            payload: JSON body, e.g., {"name": "CI Key"}

        Returns:
            Raw response including the newly created key material
        """
        return self._http.request(method="POST", url="/v2/api-keys", json=payload)

    def revoke_api_key(self, key_fid: str) -> None:
        """DELETE /v2/api-keys/{key_fid} to revoke an API key.

        Args:
            key_fid: Platform key identifier (e.g., apikey_abc123)
        """
        self._http.request(method="DELETE", url=f"/v2/api-keys/{key_fid}")

    # --------------- Reservations ---------------
    def create_reservation(self, payload: dict[str, Any]) -> Any:
        """POST /v2/reservation to create a reservation (aligns with OpenAPI)."""
        return self._http.request(method="POST", url="/v2/reservation", json=payload)

    def list_reservations(self, params: dict[str, Any] | None = None) -> Any:
        """GET /v2/reservation to list reservations (optionally filter by project/region)."""
        return self._http.request(method="GET", url="/v2/reservation", params=params or {})

    def get_reservation(self, reservation_id: str) -> Any:
        """GET /v2/reservation/{id} to fetch reservation details (preferred path)."""
        return self._http.request(method="GET", url=f"/v2/reservation/{reservation_id}")

    def list_reservation_instances(self, reservation_id: str) -> Any:
        """GET /v2/reservations/{id}/instances to list instances in a reservation.

        Note: Instance subresource path may remain under the plural namespace in current API.
        """
        return self._http.request(method="GET", url=f"/v2/reservations/{reservation_id}/instances")

    def get_reservation_availability(self, params: dict[str, Any]) -> Any:
        """GET /v2/reservation/availability to fetch availability slots.

        Expected params: project, instance_type, region, earliest_start_time, latest_end_time
        """
        return self._http.request(method="GET", url="/v2/reservation/availability", params=params)

    # --------------- Volumes: file operations ---------------
    def upload_volume_file(self, volume_id: str, payload: dict[str, Any]) -> Any:
        """POST /volumes/{id}/upload to upload a file into a volume."""
        return self._http.request(method="POST", url=f"/volumes/{volume_id}/upload", json=payload)

    def download_volume_file(self, volume_id: str, params: dict[str, Any]) -> Any:
        """GET /volumes/{id}/download to download a file from a volume."""
        return self._http.request(method="GET", url=f"/volumes/{volume_id}/download", params=params)

    def list_volume_files(self, volume_id: str, params: dict[str, Any]) -> Any:
        """GET /volumes/{id}/list to list files under a path inside a volume."""
        return self._http.request(method="GET", url=f"/volumes/{volume_id}/list", params=params)

    # --------------- SSH Keys (extended) ---------------
    def create_ssh_key(self, payload: dict[str, Any]) -> Any:
        """POST /v2/ssh-keys to create an SSH key (server-side or with provided public key)."""
        return self._http.request(method="POST", url="/v2/ssh-keys", json=payload)

    def delete_ssh_key(self, key_id: str) -> None:
        """DELETE /v2/ssh-keys/{id} to delete a key."""
        self._http.request(method="DELETE", url=f"/v2/ssh-keys/{key_id}")

    def patch_ssh_key(self, key_id: str, payload: dict[str, Any]) -> Any:
        """PATCH /v2/ssh-keys/{id} to update SSH key fields (e.g., required flag)."""
        return self._http.request(method="PATCH", url=f"/v2/ssh-keys/{key_id}", json=payload)

    # --------------- Legacy endpoints (compat) ---------------
    def list_auctions(self, params: dict[str, Any]) -> Any:
        """GET /auctions (legacy/testing path) to fetch auction listings."""
        return self._http.request(method="GET", url="/auctions", params=params)

    def create_legacy_bid(self, payload: dict[str, Any]) -> Any:
        """POST /bids (legacy/testing path) to submit a bid.

        Note: Prefer create_bid() against /v2/spot/bids when possible.
        """
        return self._http.request(method="POST", url="/bids", json=payload)
