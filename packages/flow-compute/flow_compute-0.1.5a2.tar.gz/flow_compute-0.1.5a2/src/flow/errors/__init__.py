"""Flow SDK exception hierarchy.

Comprehensive error handling with actionable recovery guidance. All Flow
exceptions inherit from FlowError and provide structured error information
including suggestions and error codes for programmatic handling.

Exception Hierarchy:
    FlowError (base)
    ├── AuthenticationError - API key and auth issues
    ├── ResourceNotFoundError - Missing resources
    │   └── TaskNotFoundError - Missing tasks
    ├── ValidationError - Configuration/parameter errors
    ├── APIError - API communication failures
    │   └── ValidationAPIError - 422 validation errors
    ├── NetworkError - Connection issues
    ├── ProviderError - Provider-specific failures
    └── (others...)

Usage Guidelines:
    - Always include suggestions for user recovery
    - Preserve original error context with cause
    - Use specific subclasses over generic FlowError
    - Include error codes for common failures
"""


class FlowError(Exception):
    """Base exception for all Flow SDK errors.

    Provides structured error information with consistent formatting,
    actionable recovery suggestions, and machine-readable error codes.
    All Flow exceptions should inherit from this base class.

    Args:
        message: Primary error description. Should be clear and specific
            about what went wrong. Avoid technical jargon where possible.
        suggestions: Optional list of actionable steps to resolve the error.
            Each suggestion should be a complete sentence starting with a verb.
        error_code: Optional machine-readable code for programmatic handling.
            Format: CATEGORY_NUMBER (e.g., AUTH_001, NETWORK_003).

    Attributes:
        message: The error message.
        suggestions: List of recovery suggestions.
        error_code: Unique error identifier.

    Error Code Categories:
        - AUTH_*: Authentication and authorization
        - RESOURCE_*: Resource not found or unavailable
        - VALIDATION_*: Input validation failures
        - NETWORK_*: Network and connectivity issues
        - PROVIDER_*: Provider-specific errors
        - TASK_*: Task execution failures

    Example:
        >>> raise FlowError(
        ...     "Failed to connect to GPU cluster",
        ...     suggestions=[
        ...         "Check your internet connection",
        ...         "Verify the API endpoint is correct",
        ...         "Ensure your API key has not expired",
        ...         f"Check {self._get_status_url()} for outages" if self._get_status_url() else "Check the provider status page for outages"
        ...     ],
        ...     error_code="NETWORK_001"
        ... )
    """

    def __init__(self, message: str, suggestions: list = None, error_code: str = None):
        self.message = message
        self.suggestions = suggestions or []
        self.error_code = error_code
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error with suggestions."""
        msg = self.message

        if self.suggestions:
            msg += "\n\nSuggestions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                msg += f"\n  {i}. {suggestion}"

        if self.error_code:
            msg += f"\n\nError code: {self.error_code}"

        return msg


class AuthenticationError(FlowError):
    """Authentication or authorization failure.

    Raised when API authentication fails or user lacks required permissions.
    This is typically the first error users encounter when setting up Flow.

    Common Causes:
        - Missing API key configuration
        - Invalid or expired API key
        - Insufficient permissions for requested operation
        - Wrong API endpoint for key type
        - Rate limit exceeded

    Error Codes:
        - AUTH_001: No API key provided
        - AUTH_002: Invalid API key format
        - AUTH_003: API key expired or revoked
        - AUTH_004: Insufficient permissions
        - AUTH_005: Rate limit exceeded

    Examples:
        >>> # Missing API key
        >>> raise AuthenticationError(
        ...     "No API key configured",
        ...     suggestions=[
        ...         "Run 'flow init' to configure your API key interactively",
        ...         "Set MITHRIL_API_KEY environment variable",
        ...         "Create ~/.flow/config.yaml with your API key",
        ...         "Pass api_key to Flow(config=Config(api_key='...'))"
        ...     ],
        ...     error_code="AUTH_001"
        ... )

        >>> # Permission denied
        >>> raise AuthenticationError(
        ...     "API key lacks permission to create instances in project 'prod'",
        ...     suggestions=[
        ...         "Request access to the 'prod' project from your admin",
        ...         "Use a different project with 'flow init --project'",
        ...         "Check your permissions in the provider dashboard"
        ...     ],
        ...     error_code="AUTH_004"
        ... )
    """

    pass


class ResourceNotFoundError(FlowError):
    """Raised when a requested resource cannot be found.

    This is the base class for all resource-not-found errors. Specific
    subclasses provide more context for different resource types.

    Common causes:
    - Resource ID is incorrect
    - Resource has been deleted
    - User lacks permission to access the resource
    - Resource exists in a different project or region

    Example:
        >>> raise ResourceNotFoundError(
        ...     "Project 'my-project' not found",
        ...     suggestions=[
        ...         "Check the project name for typos",
        ...         "Ensure you have access to this project",
        ...         "List available projects with 'flow list projects'"
        ...     ]
        ... )
    """

    pass


class TaskNotFoundError(ResourceNotFoundError):
    """Raised when a task cannot be found.

    This typically occurs when:
    - Task ID is incorrect or malformed
    - Task has already completed and been cleaned up
    - Task exists in a different project
    - User lacks permission to view the task

    Example:
        >>> from flow.errors.messages import TASK_NOT_FOUND
        >>> raise TaskNotFoundError(
        ...     TASK_NOT_FOUND.format(task_id='task-abc123'),
        ...     suggestions=[
        ...         "Verify the task ID is correct",
        ...         "Check if the task has already completed",
        ...         "Use 'flow list' to see active tasks",
        ...         "Ensure you're using the correct project"
        ...     ]
        ... )
    """

    pass


class ValidationError(FlowError, ValueError):
    """Raised when configuration or parameters are invalid.

    Inherits from both FlowError and ValueError for compatibility with
    standard Python error handling patterns.

    Common validation errors:
    - Invalid resource specifications (CPU, memory, GPU)
    - Malformed configuration files
    - Type mismatches
    - Out-of-range values
    - Missing required fields

    Args:
        message: Description of what validation failed.
        suggestions: Optional list of how to fix the validation error.
        error_code: Optional error code for specific validation failures.

    Example:
        >>> raise ValidationError(
        ...     "Invalid memory specification: '10GB'",
        ...     suggestions=[
        ...         "Memory must be specified as an integer (in MB)",
        ...         "Example: memory=10240 for 10GB",
        ...         "Valid range: 512-524288 (512MB to 512GB)"
        ...     ]
        ... )
    """

    def __init__(self, message: str, suggestions: list = None, error_code: str = None):
        # Call FlowError's __init__ to handle formatting
        FlowError.__init__(self, message, suggestions, error_code)
        # Also initialize ValueError for compatibility
        ValueError.__init__(self, self._format_message())


class APIError(FlowError):
    """Raised when an API request fails.

    Base class for all API-related errors. Provides access to the HTTP
    status code and response body for debugging.

    Args:
        message: Human-readable error description.
        status_code: HTTP status code from the failed request.
        response_body: Raw response body for debugging.
        request_id: Provider request ID/correlation ID for support/debugging.

    Attributes:
        status_code: The HTTP status code (e.g., 400, 500).
        response_body: The raw response body text.
        request_id: Request correlation identifier when available.

    Example:
        >>> raise APIError(
        ...     "Server error while creating task",
        ...     status_code=500,
        ...     response_body='{"error": "Internal server error"}',
        ...     request_id="req_abc123"
        ... )
    """

    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_body: str = None,
        request_id: str = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id


class RateLimitError(APIError):
    """Rate limit exceeded error (HTTP 429).

    Raised when API request rate limit is exceeded.
    Includes retry_after information when available.
    """

    def __init__(self, message: str, retry_after=None, request_id: str | None = None, **kwargs):
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional error details
        """
        super().__init__(message, request_id=request_id, **kwargs)
        self.retry_after = retry_after


class ValidationAPIError(APIError):
    """API request validation failure (HTTP 422).

    Specialized error for handling FastAPI/Pydantic validation responses.
    Parses structured validation errors and provides field-specific guidance
    for common configuration mistakes.

    Response Format Expected:
        {
            "detail": [
                {
                    "loc": ["body", "instance_type"],
                    "msg": "Invalid instance type",
                    "type": "value_error"
                }
            ]
        }

    Common Field Errors:
        - instance_type: Unknown GPU type or format
        - region: Invalid or unavailable region
        - max_price_per_hour: Price below minimum bid
        - volumes: Invalid mount paths or size
        - ssh_keys: Unknown key IDs
    """

    def __init__(self, response):
        import json

        self.validation_errors = []
        self.response = response

        try:
            error_data = response.json()
            if "detail" in error_data and isinstance(error_data["detail"], list):
                self.validation_errors = error_data["detail"]
        except (json.JSONDecodeError, KeyError):
            # Fallback to raw response if parsing fails
            pass

        message = self._format_message()
        # Capture request/correlation ID when available
        request_id = None
        try:
            request_id = response.headers.get("x-request-id") or response.headers.get(
                "x-correlation-id"
            )
        except Exception:
            request_id = None

        super().__init__(
            message, status_code=422, response_body=response.text, request_id=request_id
        )

    def _format_message(self) -> str:
        """Format validation errors into a readable message."""
        if not self.validation_errors:
            return "Validation failed. The request contained invalid data."

        field_errors = {}
        for error in self.validation_errors:
            field_path = error.get("loc", [])
            field = field_path[-1] if field_path else "unknown"

            if len(field_path) > 1 and field_path[0] == "body":
                field = ".".join(str(part) for part in field_path[1:])

            error_type = error.get("type", "validation_error")
            error_msg = error.get("msg", "Invalid value")

            if field not in field_errors:
                field_errors[field] = []

            if error_type == "missing":
                field_errors[field].append("Field is required")
            elif error_type == "value_error":
                field_errors[field].append(error_msg)
            else:
                field_errors[field].append(f"{error_msg}")

        lines = ["Validation failed:"]
        for field, errors in field_errors.items():
            for error in errors:
                lines.append(f"  - {field}: {error}")

        # Best-effort provider-specific help (guarded import)
        try:
            from flow.adapters.providers.builtin.mithril.core.constants import (
                format_validation_help,  # type: ignore
            )

            for field in ["region", "disk_interface", "instance_type"]:
                if field in field_errors:
                    help_lines = format_validation_help(field)
                    if help_lines:
                        lines.append("")
                        lines.extend(help_lines)
        except Exception:
            pass

        return "\n".join(lines)


class InsufficientBidPriceError(ValidationAPIError):
    """Raised when a bid fails due to price being below minimum.

    This specialized validation error provides current market pricing
    information to help users set an appropriate bid price.

    Attributes:
        current_price: Current spot price for the instance type
        min_bid_price: Minimum acceptable bid price
        recommended_price: Suggested bid price (usually current + margin)
        instance_type: The instance type being bid on
        region: The region where the bid was placed
    """

    def __init__(
        self,
        message: str,
        current_price: float = None,
        min_bid_price: float = None,
        recommended_price: float = None,
        instance_type: str = None,
        region: str = None,
        response=None,
        **kwargs,
    ):
        # Store pricing attributes first
        self.current_price = current_price
        self.min_bid_price = min_bid_price
        self.recommended_price = recommended_price
        self.instance_type = instance_type
        self.region = region

        # Initialize validation_errors before calling any parent init
        self.validation_errors = []

        # If we have a response, initialize from it
        if response:
            super().__init__(response)
            # Override the formatted message with our custom one
            self.message = message
        else:
            # Initialize as APIError without going through ValidationAPIError
            self.message = message
            self.suggestions = []
            self.error_code = None
            self.status_code = 422
            self.response_body = None
            # Call Exception init directly to avoid format_message issues
            Exception.__init__(self, message)

        # Ensure we have suggestions list
        if not hasattr(self, "suggestions") or self.suggestions is None:
            self.suggestions = []

        # Add pricing suggestions if available
        if current_price and recommended_price:
            self.suggestions.extend(
                [
                    f"Current spot price: ${current_price:.2f}/hour",
                    f"Recommended bid: ${recommended_price:.2f}/hour (50% above current)",
                    f"Update your config: max_price_per_hour={recommended_price:.2f}",
                    f"Or use 'flow run --max-price {recommended_price:.2f} ...'",
                ]
            )


class NetworkError(FlowError):
    """Raised when network communication fails.

    This error indicates problems with network connectivity, DNS resolution,
    or connection establishment. It's distinct from API errors which occur
    after a connection is established.

    Common causes:
    - No internet connection
    - DNS resolution failure
    - Firewall blocking connections
    - Proxy configuration issues
    - SSL/TLS certificate problems

    Example:
        >>> raise NetworkError(
        ...     "Failed to connect to Mithril API",
        ...     suggestions=[
        ...         "Check your internet connection",
        ...         "Verify firewall settings allow HTTPS traffic",
        ...         "Check proxy configuration if behind a corporate firewall",
        ...         "Try again in a few moments"
        ...     ]
        ... )
    """

    pass


class InvalidResponseError(FlowError):
    """Raised when API returns an invalid or unexpected response.

    This error occurs when:
    - Response is not valid JSON when JSON is expected
    - Response structure doesn't match expected schema
    - Required fields are missing from response
    - Response contains invalid data types

    Example:
        >>> raise InvalidResponseError(
        ...     "Expected JSON response but received HTML",
        ...     suggestions=[
        ...         "This might indicate a temporary API issue",
        ...         "Check the Mithril status page for ongoing incidents",
        ...         "Contact support if the problem persists"
        ...     ]
        ... )
    """

    pass


class TimeoutError(FlowError):
    """Raised when a request exceeds the timeout limit.

    Timeouts can occur at different stages:
    - Connection timeout: Failed to establish connection
    - Read timeout: Connected but no response received
    - Task timeout: Task execution exceeded time limit

    Example:
        >>> raise TimeoutError(
        ...     "Request timed out after 30 seconds",
        ...     suggestions=[
        ...         "Check if the service is experiencing high load",
        ...         "Increase timeout with timeout parameter",
        ...         "Retry the operation",
        ...         "Break large operations into smaller chunks"
        ...     ]
        ... )
    """

    pass


class ProviderError(FlowError):
    """Raised when provider configuration or initialization fails.

    This error indicates problems with:
    - Provider configuration validation
    - Provider initialization
    - Provider-specific requirements not met
    - Incompatible provider versions

    Example:
        >>> raise ProviderError(
        ...     "Mithril provider requires 'project' to be configured",
        ...     suggestions=[
        ...         "Set project in flow.yaml configuration",
        ...         "Pass project parameter to Flow constructor",
        ...         "Set MITHRIL_PROJECT environment variable"
        ...     ]
        ... )
    """

    pass


class ConfigParserError(FlowError):
    """Raised when configuration file parsing fails.

    This error occurs when:
    - YAML/JSON syntax is invalid
    - Configuration schema validation fails
    - Circular references in configuration
    - Unsupported configuration version

    Example:
        >>> raise ConfigParserError(
        ...     "Invalid YAML in flow.yaml at line 15",
        ...     suggestions=[
        ...         "Check YAML indentation (use spaces, not tabs)",
        ...         "Validate YAML syntax at yamllint.com",
        ...         "Ensure all strings with special characters are quoted",
        ...         "Remove any duplicate keys"
        ...     ]
        ... )
    """

    pass


class ResourceNotAvailableError(FlowError):
    """Requested resource is temporarily unavailable.

    Distinct from ResourceNotFoundError - the resource type exists
    but no capacity is currently available.

    Common Scenarios:
        - No GPU instances available in region
        - Spot instance capacity exhausted
        - Volume attachment limit reached
        - Quota exceeded

    Example:
        >>> raise ResourceNotAvailableError(
        ...     "No H100 instances available in us-east-1",
        ...     suggestions=[
        ...         "Try a different region with 'flow run --region us-west-2'",
        ...         "Use a different GPU type like A100",
        ...         "Enable cross-region search with '--any-region'",
        ...         "Check availability in the provider capacity dashboard"
        ...     ],
        ...     error_code="RESOURCE_002"
        ... )
    """

    pass


class ResourceLimitError(FlowError):
    """Resource limit exceeded error.

    Raised when requested resources exceed available limits
    (e.g., GPU count, memory, storage).
    """

    def __init__(self, message: str, resource_type=None, requested=None, available=None, **kwargs):
        """Initialize resource limit error.

        Args:
            message: Error message
            resource_type: Type of resource (e.g., 'gpu', 'memory', 'storage')
            requested: Amount requested
            available: Amount available
            **kwargs: Additional error details
        """
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.requested = requested
        self.available = available


class QuotaExceededError(FlowError):
    """Resource quota limit exceeded.

    Raised when user hits project or account-level resource limits.

    Quota Types:
        - GPU hours per month
        - Concurrent instances
        - Storage volume count/size
        - API request rate

    Example:
        >>> raise QuotaExceededError(
        ...     "GPU quota exceeded: 1000/1000 hours used this month",
        ...     suggestions=[
        ...         "Request quota increase from your provider",
        ...         "Terminate idle instances with 'flow list --running | flow cancel'",
        ...         "Upgrade to a higher tier plan",
        ...         "Wait until next billing cycle (7 days remaining)"
        ...     ],
        ...     error_code="QUOTA_001"
        ... )
    """

    pass


class VolumeError(FlowError):
    """Storage volume operation failed.

    Base class for volume-related errors including creation,
    attachment, and data transfer failures.

    Example:
        >>> raise VolumeError(
        ...     "Cannot attach volume 'vol-123' - already in use",
        ...     suggestions=[
        ...         "Detach volume from current instance first",
        ...         "Create a new volume with 'flow volume create'",
        ...         "Use read-only mount for shared access"
        ...     ],
        ...     error_code="VOLUME_003"
        ... )
    """

    pass


class TaskExecutionError(FlowError):
    """Task failed during execution.

    Raised when a task fails after successful submission.
    Includes exit code and last log lines for debugging.

    Attributes:
        exit_code: Process exit code if available
        last_logs: Final log output lines

    Example:
        >>> raise TaskExecutionError(
        ...     "Task failed with exit code 137 (Out of Memory)",
        ...     suggestions=[
        ...         "Increase instance memory with --instance-type",
        ...         "Reduce batch size or model size",
        ...         "Enable gradient checkpointing",
        ...         "Check logs with 'flow logs task-123'"
        ...     ],
        ...     error_code="TASK_002"
        ... )
    """

    def __init__(self, message: str, exit_code: int = None, last_logs: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.exit_code = exit_code
        self.last_logs = last_logs


# Standard Python exceptions used by Flow:
# - ValueError: Invalid parameter values
# - TypeError: Wrong parameter types
# - KeyError: Missing configuration keys
# - FileNotFoundError: Missing files
# - PermissionError: Insufficient file permissions
# - TimeoutError: Operation timeouts (built-in)
# - ConnectionError: Network issues (built-in)


class FlowOperationError(FlowError):
    """Structured error for failed operations with full context.

    Wraps operation failures with additional context about what was
    being attempted, which resource was involved, and the underlying
    cause. Useful for debugging complex multi-step operations.

    Args:
        operation: Description of attempted operation (e.g., "volume attachment")
        resource_id: Identifier of resource being operated on
        cause: Original exception that caused the failure
        suggestions: Optional recovery suggestions

    Attributes:
        operation: The failed operation name
        resource_id: The resource identifier
        cause: Original exception

    Example:
        >>> try:
        ...     attach_volume(vol_id, instance_id)
        ... except VolumeInUseError as e:
        ...     raise FlowOperationError(
        ...         operation="volume attachment",
        ...         resource_id=vol_id,
        ...         cause=e,
        ...         suggestions=[
        ...             "Check if volume is already attached",
        ...             "Ensure volume and instance are in same region"
        ...         ]
        ...     ) from e
    """

    def __init__(
        self,
        operation: str,
        resource_id: str,
        cause: Exception,
        suggestions: list = None,
        error_code: str = None,
    ):
        self.operation = operation
        self.resource_id = resource_id
        self.cause = cause

        message = f"{operation} failed for {resource_id}"
        if cause:
            message += f": {cause!s}"

        # Inherit suggestions from cause if not provided
        if suggestions is None and hasattr(cause, "suggestions"):
            suggestions = cause.suggestions

        super().__init__(message, suggestions=suggestions, error_code=error_code)


class DevVMNotFoundError(FlowError):
    """Raised when no development VM is running.

    This error indicates that a dev VM operation was attempted
    but no active dev VM could be found. Start a VM with
    flow.dev.start() or flow.dev.ensure_started().
    """

    def __init__(self, message: str = None, **kwargs):
        if message is None:
            message = "No development VM is currently running"

        suggestions = kwargs.pop(
            "suggestions",
            [
                "Start a new dev VM with flow.dev.start()",
                "Use flow.dev.ensure_started() to start or reuse existing VM",
                "Check VM status with flow.dev.status()",
                "List all running tasks with flow list_tasks()",
            ],
        )

        super().__init__(message, suggestions=suggestions, error_code="DEV_001", **kwargs)


class DevVMStartupError(FlowError):
    """Raised when development VM fails to start.

    This error indicates the dev VM could not be provisioned
    or reach a running state. Check instance availability,
    quotas, and credentials.
    """

    def __init__(self, message: str = None, instance_type: str = None, **kwargs):
        if message is None:
            message = "Failed to start development VM"
            if instance_type:
                message += f" with instance type '{instance_type}'"

        suggestions = kwargs.pop(
            "suggestions",
            [
                "Check if the instance type is available in your region",
                "Verify you have sufficient quota for the requested resources",
                "Try a different instance type (e.g., 'a100' instead of 'h100')",
                "Check the task logs for more details",
                "Ensure your API credentials are valid",
            ],
        )

        super().__init__(message, suggestions=suggestions, error_code="DEV_002", **kwargs)


class DevContainerError(FlowError):
    """Raised when container operations fail on dev VM.

    This error indicates Docker container execution failed.
    Common causes include missing images, Docker daemon issues,
    or command failures.
    """

    def __init__(self, message: str = None, command: str = None, image: str = None, **kwargs):
        if message is None:
            message = "Container operation failed on dev VM"
            if command:
                message += f" while executing '{command}'"

        suggestions = kwargs.pop("suggestions", [])

        # Add context-specific suggestions
        if image and "not found" in str(kwargs.get("cause", "")):
            suggestions.append(f"Verify Docker image '{image}' exists or is accessible")
            suggestions.append("The image will be pulled automatically if available")

        if "docker: command not found" in str(kwargs.get("cause", "")):
            suggestions.append("Docker may not be installed on the dev VM")
            suggestions.append("SSH into the VM with flow.dev.connect() and install Docker")

        # Default suggestions if none were added
        if not suggestions:
            suggestions = [
                "Check if Docker is running on the dev VM",
                "Verify the Docker image name is correct",
                "Use flow.dev.connect() to debug directly on the VM",
                "Reset containers with flow.dev.reset()",
                "Check available disk space on the dev VM",
            ]

        super().__init__(message, suggestions=suggestions, error_code="DEV_003", **kwargs)


class RemoteExecutionError(FlowError):
    """Error executing remote command on instance.

    Raised when SSH-based remote command execution fails. This covers
    both connection issues and command execution failures.
    """

    def __init__(self, message: str, exit_code: int = None):
        """Initialize remote execution error.

        Args:
            message: Error description
            exit_code: Command exit code if available
        """
        suggestions = [
            "Verify the instance is running and accessible",
            "Check that SSH keys are properly configured",
            "Ensure the command exists on the remote system",
            "Try connecting with 'flow ssh' to debug",
        ]

        if exit_code is not None:
            message = f"{message} (exit code: {exit_code})"

        super().__init__(message, suggestions=suggestions, error_code="REMOTE_001")


class NameConflictError(FlowError):
    """Raised when a resource name is already in use."""

    def __init__(self, name: str, resource_type: str = "resource"):
        """Initialize name conflict error.

        Args:
            name: The conflicting name
            resource_type: Type of resource (e.g., "task", "volume", "dev VM")
        """
        super().__init__(
            f"{resource_type.capitalize()} name '{name}' is already in use",
            suggestions=[
                f"Choose a different name for your {resource_type}",
                "Use --force-new to create with a unique suffix",
                f"Check existing {resource_type}s with 'flow list'",
            ],
            error_code="RESOURCE_002",
        )


class DependencyNotFoundError(FlowError):
    """Raised when a required system dependency is missing."""

    def __init__(self, dependency: str, install_commands: dict = None):
        """Initialize dependency not found error.

        Args:
            dependency: Name of missing dependency
            install_commands: Dict of platform -> install command
        """
        suggestions = [f"Install {dependency} on your system"]

        if install_commands:
            for platform, cmd in install_commands.items():
                suggestions.append(f"{platform}: {cmd}")

        super().__init__(
            f"Required dependency '{dependency}' not found",
            suggestions=suggestions,
            error_code="DEPENDENCY_001",
        )


class InstanceNotReadyError(FlowError):
    """Raised when instance is still provisioning or not ready."""

    def __init__(self, task_id: str, reason: str = "provisioning"):
        """Initialize instance not ready error.

        Args:
            task_id: Task ID that's not ready
            reason: Specific reason (provisioning, starting, etc.)
        """
        super().__init__(
            f"Instance {task_id} is not ready: {reason}",
            suggestions=[
                "Wait a few more minutes for provisioning to complete",
                f"Check instance status with 'flow status {task_id}'",
                "Some operations may take 5-10 minutes on first start",
            ],
            error_code="INSTANCE_001",
        )
