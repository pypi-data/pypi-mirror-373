"""Reservations facet - handles reservation operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.adapters.providers.builtin.mithril.core.constants import DEFAULT_REGION
from flow.errors import ValidationError
from flow.sdk.models import Reservation, Task, TaskConfig

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class ReservationsFacet:
    """Handles reservation operations."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize reservations facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx
        self._logger = getattr(ctx, "logger", logger)

    @handle_mithril_errors("Create reservation")
    def create_reservation(
        self, instance_type: str, config: TaskConfig, volume_ids: list[str] | None = None
    ) -> Reservation:
        """Create a new reservation.

        Args:
            instance_type: Type of instance to reserve
            config: Task configuration with reservation details
            volume_ids: Optional volume IDs to attach

        Returns:
            Created reservation

        Raises:
            ValidationError: If reservation parameters are invalid
        """
        from flow.sdk.models import ReservationSpec

        # Resolve instance type
        instance_type_id = self.ctx.resolve_instance_type(instance_type)

        # Copy config for adjustments
        adjusted = config.model_copy()
        project_id = self.ctx.get_project_id()

        # Process data mounts if present
        if adjusted.data_mounts:
            from flow.core.data.mount_processor import MountProcessor

            mp = MountProcessor()
            resolved_mounts = mp.process_mounts(adjusted, self.ctx)  # type: ignore[arg-type]
            mount_vols, mount_env = self.ctx.mount_adapter.adapt_mounts(resolved_mounts)

            # Add mount volumes to volume list
            volume_ids = list(volume_ids or []) + [v.volume_id for v in mount_vols if v.volume_id]

            # Add mount environment variables
            if mount_env:
                adjusted = adjusted.model_copy(update={"env": {**adjusted.env, **mount_env}})

        # Package code if needed
        if adjusted.upload_code and not self.ctx.code_upload.should_use_scp_upload(adjusted):
            adjusted = self.ctx.code_upload.package_local_code(adjusted)

        # Add distributed environment for multi-node
        distributed_env = {
            "_FLOW_MITHRIL_API_KEY": self.ctx.mithril_config.api_key,
            "_FLOW_MITHRIL_API_URL": self.ctx.http.base_url,
            "_FLOW_MITHRIL_PROJECT": project_id,
        }

        if adjusted.num_instances and adjusted.num_instances > 1:
            distributed_env.update({"FLOW_DISTRIBUTED_AUTO": "1", "FLOW_RDV_TIMEOUT_SEC": "600"})

        adjusted = adjusted.model_copy(update={"env": {**adjusted.env, **distributed_env}})

        # Build startup script
        prep = self.ctx.script_prep.build_and_prepare(adjusted)
        startup_script = prep.content

        # Extract reservation parameters
        region = adjusted.region or self.ctx.mithril_config.region or DEFAULT_REGION
        quantity = adjusted.num_instances or 1

        # Validate required fields
        start_time = getattr(adjusted, "scheduled_start_time", None)
        duration_hours = getattr(adjusted, "reserved_duration_hours", None)

        if not start_time or not duration_hours:
            raise ValidationError(
                "Reservation requires scheduled_start_time and reserved_duration_hours"
            )

        # Resolve SSH keys
        ssh_keys = self.ctx.ssh_keys_svc.resolve_keys(
            adjusted.ssh_keys
        ) or self.ctx.ssh_keys_svc.resolve_keys(self.ctx.mithril_config.ssh_keys)

        # Create reservation spec
        spec = ReservationSpec(
            name=getattr(adjusted, "name", None),
            project_id=project_id,
            instance_type=instance_type_id,
            region=region,
            quantity=quantity,
            start_time_utc=start_time,
            duration_hours=int(duration_hours),
            ssh_keys=ssh_keys,
            volumes=volume_ids or [],
            startup_script=startup_script,
        )

        return self.ctx.reservations.create(spec)

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        """List reservations.

        Args:
            params: Optional filter parameters

        Returns:
            List of reservations
        """
        p = dict(params or {})
        p.setdefault("project", self.ctx.get_project_id())
        return self.ctx.reservations.list(p)

    def get_reservation(self, reservation_id: str) -> Reservation:
        """Get a specific reservation.

        Args:
            reservation_id: Reservation ID

        Returns:
            Reservation details
        """
        return self.ctx.reservations.get(reservation_id)

    def get_reservation_availability(
        self,
        instance_type: str,
        num_nodes: int,
        duration_hours: float,
        *,
        region: str | None = None,
        earliest_start_time: str | None = None,
        latest_end_time: str | None = None,
        mode: str | None = None,
    ) -> list[dict[str, Any]]:
        """Check availability for a reservation.

        Args:
            instance_type: Type of instance to check
            num_nodes: Number of nodes needed
            duration_hours: Duration needed in hours
            earliest_start_time: Earliest start time in ISO format
            latest_end_time: Latest end time in ISO format

        Returns:
            List of availability windows
        """
        # Resolve instance type to provider ID/FID
        instance_type_id = self.ctx.resolve_instance_type(instance_type)

        # Build params matching Mithril v2 API (see OpenAPI /v2/reservation/availability)
        params: dict[str, Any] = {
            "project": self.ctx.get_project_id(),
            "instance_type": instance_type_id,
            "region": region or DEFAULT_REGION,
        }

        # Set mode based on parameters provided
        # - Use explicit mode if provided
        # - Use "slots" when time window is specified
        # - Otherwise let API use its default (latest_end_time)
        if mode:
            params["mode"] = mode
        elif earliest_start_time or latest_end_time:
            params["mode"] = "slots"
        # If no mode and no time window, API will use default mode

        # Include time window parameters when provided
        if earliest_start_time:
            params["earliest_start_time"] = earliest_start_time
        if latest_end_time:
            params["latest_end_time"] = latest_end_time

        # Align parameters with selected mode per OpenAPI
        effective_mode = str(params.get("mode", "latest_end_time"))
        if effective_mode == "latest_end_time":
            # This mode expects start_time (not earliest/latest); map when provided
            if earliest_start_time:
                params["start_time"] = earliest_start_time
        elif effective_mode == "check":
            # This mode expects start_time and end_time; map when both provided
            if earliest_start_time and latest_end_time:
                params["start_time"] = earliest_start_time
                params["end_time"] = latest_end_time
        
        # Always include quantity when num_nodes is specified
        if num_nodes:
            params["quantity"] = int(max(1, num_nodes))
        
        # Include duration_hours for all modes - API may use it for filtering
        if duration_hours:
            params["duration_hours"] = duration_hours

        # Optional diagnostic logging when enabled
        try:
            import os as _os

            if _os.getenv("FLOW_RESERVE_DEBUG"):
                self._logger.info(
                    f"[reserve.availability] params={{{'project': params.get('project'), 'instance_type': params.get('instance_type'), 'region': params.get('region'), 'mode': params.get('mode'), 'earliest': params.get('earliest_start_time'), 'latest': params.get('latest_end_time'), 'start': params.get('start_time'), 'end': params.get('end_time'), 'qty': params.get('quantity'), 'duration_hours': params.get('duration_hours')}}}"
                )
        except Exception:
            pass

        resp = self.ctx.api.get_reservation_availability(params)
        return resp.get("data", resp) if isinstance(resp, dict) else resp

    def submit_task_from_reservation(self, reservation: Reservation, config: TaskConfig) -> Task:
        """Submit a task using a reservation.

        Args:
            reservation: Reservation to use
            config: Task configuration

        Returns:
            Submitted task
        """
        # Build task from reservation
        task = self.ctx.task_service.build_task_from_reservation(reservation, config)

        # Attach provider reference if possible
        try:
            task._provider = self.ctx  # type: ignore[attr-defined]
        except Exception:
            pass

        return task
