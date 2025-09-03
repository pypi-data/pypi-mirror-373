"""Mithril provider context - builds and holds all dependencies.

This module is responsible for wiring up all services and dependencies
that the provider facets need, providing a single source of truth.
"""

from __future__ import annotations

import logging
import os
from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from flow.adapters.http.client import HttpClient
from flow.adapters.providers.builtin.mithril.adapters.mounts import MithrilMountAdapter
from flow.adapters.providers.builtin.mithril.adapters.runtime import (
    ScriptSizeConfig,
    ScriptSizeHandler,
)
from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.bidding.finder import AuctionFinder
from flow.adapters.providers.builtin.mithril.bidding.manager import BidManager
from flow.adapters.providers.builtin.mithril.core.constants import DEFAULT_REGION, USER_CACHE_TTL
from flow.adapters.providers.builtin.mithril.core.errors import MithrilError
from flow.adapters.providers.builtin.mithril.domain.bids import BidsService
from flow.adapters.providers.builtin.mithril.domain.code_upload import CodeUploadService
from flow.adapters.providers.builtin.mithril.domain.instance_types import InstanceTypeResolver
from flow.adapters.providers.builtin.mithril.domain.instances import InstanceService
from flow.adapters.providers.builtin.mithril.domain.logs import LogService
from flow.adapters.providers.builtin.mithril.domain.pricing import PricingService
from flow.adapters.providers.builtin.mithril.domain.region import RegionSelector
from flow.adapters.providers.builtin.mithril.domain.reservations import ReservationsService
from flow.adapters.providers.builtin.mithril.domain.script_prep import ScriptPreparationService
from flow.adapters.providers.builtin.mithril.domain.ssh_access import SshAccessService
from flow.adapters.providers.builtin.mithril.domain.ssh_keys import SSHKeyService
from flow.adapters.providers.builtin.mithril.domain.submission import SubmissionService
from flow.adapters.providers.builtin.mithril.domain.task_query import TaskQueryService
from flow.adapters.providers.builtin.mithril.domain.tasks import TaskService
from flow.adapters.providers.builtin.mithril.domain.users import UsersService
from flow.adapters.providers.builtin.mithril.domain.volume_attach import VolumeAttachService
from flow.adapters.providers.builtin.mithril.domain.volumes import VolumeService
from flow.adapters.providers.builtin.mithril.resources import ProjectResolver
from flow.adapters.providers.builtin.mithril.resources.ssh import SSHKeyManager
from flow.adapters.providers.builtin.mithril.storage import StorageConfig, create_storage_backend
from flow.adapters.startup.builder import AdapterStartupBuilder
from flow.application.config.config import Config
from flow.protocols.http import HttpClientProtocol
from flow.sdk.models import User
from flow.utils.ttl_cache import TTLCache

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class MithrilContext:
    """Central context holding all dependencies for Mithril provider.

    This class is responsible for:
    1. Building and wiring all services
    2. Managing shared state (project ID, caches)
    3. Providing helper methods used across facets
    """

    config: Config
    http: HttpClientProtocol
    mithril_config: Any  # MithrilConfig
    startup_builder: Any
    mount_adapter: MithrilMountAdapter

    # Core services (populated in build())
    api: MithrilApiClient = field(init=False)
    pricing: PricingService = field(init=False)
    region: RegionSelector = field(init=False)
    instances: InstanceService = field(init=False)
    task_service: TaskService = field(init=False)
    task_query: TaskQueryService = field(init=False)
    bids: BidsService = field(init=False)
    volumes: VolumeService = field(init=False)
    volume_attach: VolumeAttachService = field(init=False)
    users: UsersService = field(init=False)
    ssh_key_mgr: SSHKeyManager = field(init=False)
    ssh_keys_svc: SSHKeyService = field(init=False)
    ssh_access: SshAccessService = field(init=False)
    instance_types: InstanceTypeResolver = field(init=False)
    log_service: LogService = field(init=False)
    submission: SubmissionService = field(init=False)
    script_size: ScriptSizeHandler = field(init=False)
    code_upload: CodeUploadService = field(init=False)
    script_prep: ScriptPreparationService = field(init=False)
    reservations: ReservationsService = field(init=False)
    project_resolver: ProjectResolver = field(init=False)

    # Additional services for bidding
    auction_finder: AuctionFinder = field(init=False)
    bid_manager: BidManager = field(init=False)

    # Internal state
    _project_id: str | None = field(default=None, init=False)
    _user_cache: TTLCache[str, User] = field(init=False)

    @classmethod
    def build(
        cls,
        config: Config,
        http_client: HttpClientProtocol | None = None,
        startup_script_builder: Any | None = None,
    ) -> MithrilContext:
        """Build a fully wired context.

        Args:
            config: Provider configuration
            http_client: Optional HTTP client override
            startup_script_builder: Optional startup script builder override

        Returns:
            Fully initialized context

        Raises:
            ValueError: If provider is not 'mithril'
        """
        if config.provider != "mithril":
            raise ValueError(f"Expected provider='mithril', got: {config.provider}")

        # Extract Mithril config
        from flow.application.config.config import MithrilConfig

        mithril_config = MithrilConfig.from_dict(config.provider_config)

        # Build HTTP client if not provided
        if http_client is None:
            headers = config.get_headers() if hasattr(config, "get_headers") else {}
            http_client = HttpClient(base_url=mithril_config.api_url, headers=headers)

        # Create context
        ctx = cls(
            config=config,
            http=http_client,
            mithril_config=mithril_config,
            startup_builder=startup_script_builder
            or AdapterStartupBuilder(health_config=config.health_config),
            mount_adapter=MithrilMountAdapter(),
        )

        # Wire core services
        ctx.api = MithrilApiClient(ctx.http)
        ctx.pricing = PricingService(ctx.api)
        ctx.region = RegionSelector(ctx.api, ctx.pricing)
        ctx.instances = InstanceService(ctx.api, ctx.get_project_id)
        ctx.instance_types = InstanceTypeResolver()

        # Task services (SSH resolver attached later if available)
        ctx.task_service = TaskService(ctx.http, ctx.pricing, ctx.instances, ssh_resolver=None)

        # Try to attach SSH endpoint resolver
        with suppress(Exception):
            from flow.adapters.providers.builtin.mithril.domain.ssh_endpoint_resolver import (
                SshEndpointResolver,
            )

            ssh_resolver = SshEndpointResolver(ctx.api, ctx.get_project_id, ctx.instances)
            with suppress(Exception):
                if hasattr(ctx.task_service, "set_ssh_resolver"):
                    ctx.task_service.set_ssh_resolver(ssh_resolver)  # type: ignore[attr-defined]
                else:
                    ctx.task_service._ssh_resolver = ssh_resolver

        # User services
        ctx.users = UsersService(ctx.api, cache_ttl_seconds=USER_CACHE_TTL)
        ctx._user_cache = TTLCache(ttl_seconds=USER_CACHE_TTL, max_entries=1024)

        # SSH services
        ctx.ssh_key_mgr = SSHKeyManager(ctx.api)
        ctx.ssh_keys_svc = SSHKeyService(ctx.ssh_key_mgr, ctx.mithril_config)
        ctx.ssh_access = SshAccessService(ctx.ssh_key_mgr)

        # Volume services
        ctx.volumes = VolumeService(
            ctx.api, default_region=ctx.mithril_config.region or DEFAULT_REGION
        )

        # Log service (remote ops set by SSH facet later)
        ctx.log_service = LogService(None, cache_ttl=5.0, max_entries=100)

        # Task query service
        ctx.task_query = TaskQueryService(
            api=ctx.api, task_service=ctx.task_service, get_project_id=ctx.get_project_id
        )

        # Code upload service
        ctx.code_upload = CodeUploadService(ctx)  # type: ignore[arg-type]

        # Bidding services
        ctx.auction_finder = AuctionFinder(ctx.api)
        ctx.bid_manager = BidManager(ctx.api)
        ctx.bids = BidsService(
            api=ctx.api,
            region_selector=ctx.region,
            pricing=ctx.pricing,
            resolve_instance_type=ctx.resolve_instance_type,
            get_project_id=ctx.get_project_id,
        )

        # Script preparation
        ctx.script_prep = ScriptPreparationService(
            ctx.startup_builder, ctx._build_script_size_handler()
        )

        # Reservations
        ctx.reservations = ReservationsService(ctx.api)

        # Volume attachment (remote ops and SSH readiness set by SSH facet)
        ctx.volume_attach = VolumeAttachService(
            api_client=ctx.api,
            volumes=ctx.volumes,
            bids=ctx.bids,
            get_project_id=ctx.get_project_id,
            get_task_by_id=lambda tid: ctx.task_query.get_task(tid),
            make_remote_ops=lambda: None,  # Set by SSH facet
            is_instance_ssh_ready=lambda task: False,  # Set by SSH facet
        )

        # Submission service
        ctx.submission = SubmissionService(ctx)  # type: ignore[arg-type]

        # Project resolver
        ctx.project_resolver = ProjectResolver(ctx.api)

        return ctx

    # ---- Helper methods (were private methods on provider) ----

    def get_project_id(self) -> str:
        """Get the current project ID, resolving if needed.

        Returns:
            Project ID

        Raises:
            MithrilError: If project cannot be resolved
        """
        if self._project_id:
            return self._project_id

        # Check environment first
        env_project = os.environ.get("MITHRIL_PROJECT_ID")
        if env_project:
            self._project_id = env_project
            try:
                if os.environ.get("FLOW_STATUS_DEBUG"):
                    logging.getLogger("flow.status.provider").info(
                        f"mithril.ctx.project_id: from env MITHRIL_PROJECT_ID={env_project}"
                    )
            except Exception:
                pass
            return env_project

        # Check config
        if self.mithril_config.project:
            with suppress(Exception):
                self._project_id = self.project_resolver.resolve(self.mithril_config.project)
                if self._project_id:
                    try:
                        if os.environ.get("FLOW_STATUS_DEBUG"):
                            logging.getLogger("flow.status.provider").info(
                                f"mithril.ctx.project_id: resolved from config project={self.mithril_config.project} -> id={self._project_id}"
                            )
                    except Exception:
                        pass
                    return self._project_id

        # Try to auto-resolve
        with suppress(Exception):
            resolved = self.project_resolver.resolve_project()
            if resolved:
                self._project_id = resolved
                try:
                    if os.environ.get("FLOW_STATUS_DEBUG"):
                        logging.getLogger("flow.status.provider").info(
                            f"mithril.ctx.project_id: auto-resolved id={resolved}"
                        )
                except Exception:
                    pass
                return resolved

        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.provider").info(
                    "mithril.ctx.project_id: missing project → raising configuration error"
                )
        except Exception:
            pass
        raise MithrilError(
            "Project is required but not configured. Set MITHRIL_PROJECT_ID or configure project."
        )

    def resolve_instance_type(self, spec: str) -> str:
        """Resolve user-friendly instance spec to provider ID.

        Args:
            spec: User input like "a100", "4xa100", etc.

        Returns:
            Provider-specific instance type ID
        """
        return self.instance_types.resolve(spec)

    def _build_script_size_handler(self) -> ScriptSizeHandler:
        """Build script size handler with appropriate storage backend.

        Returns:
            Configured script size handler
        """
        # Derive script-size config from provider config (env > YAML via loader)
        ss_cfg_dict: dict[str, Any] = {}
        try:
            raw = (
                self.config.provider_config.get("script_size")
                if isinstance(self.config.provider_config, dict)
                else None
            )
            if isinstance(raw, dict):
                ss_cfg_dict = dict(raw)
                # Map YAML 'enable_split_storage' to handler's 'enable_split'
                if "enable_split_storage" in ss_cfg_dict and "enable_split" not in ss_cfg_dict:
                    ss_cfg_dict["enable_split"] = bool(ss_cfg_dict.get("enable_split_storage"))
        except Exception:
            ss_cfg_dict = {}

        ss_config = ScriptSizeConfig.from_dict(ss_cfg_dict) if ss_cfg_dict else ScriptSizeConfig()

        # Storage backend selection: prefer explicit script_size.storage_backend, then env defaults
        opt_backend = None
        try:
            opt_backend = (self.config.provider_config.get("script_size", {}) or {}).get(
                "storage_backend"
            )
        except Exception:
            opt_backend = None

        storage_cfg = StorageConfig.from_env()
        if opt_backend:
            if not storage_cfg:
                storage_cfg = StorageConfig()
            storage_cfg.backend_type = opt_backend

        # Try to use cloud storage if configured
        if storage_cfg and storage_cfg.backend_type and storage_cfg.backend_type != "local":
            try:
                backend = create_storage_backend(storage_cfg)
                logger.info(f"Using {storage_cfg.backend_type} storage backend for large scripts.")
                return ScriptSizeHandler(storage_backend=backend, config=ss_config)
            except Exception as e:
                logger.warning(f"Failed to init {storage_cfg.backend_type} storage: {e}")

        # Default to inline transfer
        logger.info("Using inline script transfer (no external storage).")
        # When no storage backend is available, disable split to avoid noisy warnings
        # from the ScriptSizeHandler about missing storage for split strategy.
        try:
            if getattr(ss_config, "enable_split", False):
                ss_config.enable_split = False
        except Exception:
            pass
        return ScriptSizeHandler(storage_backend=None, config=ss_config)
