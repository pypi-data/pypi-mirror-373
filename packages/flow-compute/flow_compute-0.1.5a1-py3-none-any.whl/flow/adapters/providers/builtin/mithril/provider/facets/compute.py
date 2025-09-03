"""Compute facet - handles task submission and configuration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.sdk.models import Task, TaskConfig

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class ComputeFacet:
    """Handles compute operations - task submission and configuration."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize compute facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx

        # Import selection facet for region/instance selection
        from flow.adapters.providers.builtin.mithril.provider.facets.selection import SelectionFacet

        self.selection = SelectionFacet(ctx)

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Prepare task configuration with defaults and validation.

        Args:
            config: Raw task configuration

        Returns:
            Prepared task configuration
        """
        prepared = config.model_copy()

        # Apply SSH keys from provider config if not specified
        if not prepared.ssh_keys and self.ctx.config.provider_config.get("ssh_keys"):
            prepared.ssh_keys = self.ctx.config.provider_config["ssh_keys"]

        # Apply default region if not specified
        if not prepared.region:
            default_region = self.ctx.mithril_config.region
            if default_region:
                prepared.region = default_region

        # Apply default instance type if not specified
        if not prepared.instance_type:
            default_type = self.ctx.config.provider_config.get("default_instance_type")
            if default_type:
                prepared.instance_type = default_type

        # Ensure num_instances is set
        if not prepared.num_instances:
            prepared.num_instances = 1

        # Apply environment variables
        if not prepared.env:
            prepared.env = {}

        # Add provider-specific environment
        prepared.env.update(
            {
                "_FLOW_PROVIDER": "mithril",
                "_FLOW_PROJECT_ID": self.ctx.get_project_id(),
            }
        )

        return prepared

    @handle_mithril_errors("Submit task")
    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Task:
        """Submit a new task.

        Args:
            instance_type: Type of instance to use
            config: Task configuration
            volume_ids: Optional volume IDs to attach
            allow_partial_fulfillment: Whether to allow partial node allocation
            chunk_size: Optional chunk size for distributed tasks

        Returns:
            Submitted task
        """
        # Use submission service for the actual submission
        return self.ctx.submission.submit(
            instance_type,
            config,
            volume_ids=volume_ids,
            allow_partial_fulfillment=allow_partial_fulfillment,
            chunk_size=chunk_size,
        )

    def find_optimal_auction(
        self,
        config: TaskConfig,
        use_catalog: bool = True,
    ) -> Any:
        """Find optimal auction for task configuration.

        Args:
            config: Task configuration with requirements
            use_catalog: Whether to use instance catalog

        Returns:
            Optimal auction or None
        """
        # Resolve instance type if specified
        instance_type = config.instance_type
        if instance_type and not instance_type.startswith("it_"):
            instance_type = self.ctx.resolve_instance_type(instance_type)

        # Use auction finder
        params = {
            "instance_type": instance_type,
            "region": config.region,
            "limit": 50,
        }

        # Add price constraint if specified
        max_price = getattr(config, "max_price", None)
        if max_price:
            params["max_price"] = max_price

        # Query auctions
        auctions = self.ctx.auction_finder.find_auctions(**params)

        if not auctions:
            return None

        # Sort by price and return best
        auctions.sort(key=lambda a: float(a.get("price", 999999)))
        return auctions[0]

    def package_local_code(self, config: TaskConfig) -> TaskConfig:
        """Package local code for upload.

        Args:
            config: Task configuration

        Returns:
            Updated configuration with packaged code
        """
        return self.ctx.code_upload.package_local_code(config)

    def should_use_scp_upload(self, config: TaskConfig) -> bool:
        """Check if SCP upload should be used.

        Args:
            config: Task configuration

        Returns:
            True if SCP upload should be used
        """
        return self.ctx.code_upload.should_use_scp_upload(config)
