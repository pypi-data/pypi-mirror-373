"""Run service - orchestrates task execution.

This service implements the use case for running tasks through providers.
It follows the thin vertical pattern: CLI → Application → Port → Adapter.
"""

from dataclasses import dataclass

from flow.domain.ir.spec import TaskSpec
from flow.protocols.provider import Plan, Provider, TaskHandle


@dataclass(frozen=True, slots=True)
class RunRequest:
    """Request to run a task."""

    spec: TaskSpec
    trace: bool = False
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class RunResponse:
    """Response from running a task."""

    handle: TaskHandle
    plan: Plan | None = None
    correlation_id: str | None = None


class RunService:
    """Service for running tasks through providers."""

    def __init__(self, provider: Provider):
        """Initialize with a provider implementation.

        Args:
            provider: Provider implementation to use for task execution
        """
        self._provider = provider

    def run(self, request: RunRequest) -> RunResponse:
        """Execute a task through the provider.

        Args:
            request: Run request containing task specification

        Returns:
            Response containing task handle and optional trace info
        """
        # Generate plan from IR
        plan = self._provider.plan(request.spec)

        # Submit task through provider
        handle = self._provider.submit(plan)

        # Return response with trace info if requested
        if request.trace:
            return RunResponse(handle=handle, plan=plan, correlation_id=request.correlation_id)

        return RunResponse(handle=handle, correlation_id=request.correlation_id)
