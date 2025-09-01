from typing import Any, Protocol

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

HPValue = str | float | int
MetricMetadata = dict[str, Any]


class ExperimentResponse(TypedDict, total=False):
    """Type definition for experiment API response."""

    id: str
    name: str
    description: str | None
    hyperparams: list[dict[str, Any]]
    tags: list[str]
    created_at: str
    updated_at: str
    available_metrics: list[str]
    workspace_id: str | None


class MetricResponse(TypedDict):
    """Type definition for metric API response."""

    id: int
    experiment_id: str
    name: str
    value: float
    step: int | None
    metadata: dict[str, Any] | None
    created_at: str


class WorkspaceResponse(TypedDict, total=False):
    """Type definition for workspace API response."""

    id: str
    name: str
    description: str | None
    created_at: str
    updated_at: str


class APIResponse(TypedDict):
    """Generic API response wrapper."""

    status: int
    data: Any


class ToraConfig(TypedDict, total=False):
    """Configuration options for Tora client."""

    api_key: str | None
    base_url: str | None
    timeout: int | None
    max_retries: int | None
    retry_delay: float | None
    debug: bool | None


class HTTPClient(Protocol):
    """Protocol for HTTP client implementations."""

    def get(self, path: str, headers: dict[str, str] | None = None) -> Any:
        """Send GET request."""
        ...

    def post(
        self,
        path: str,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> Any:
        """Send POST request."""
        ...

    def close(self) -> None:
        """Close the client."""
        ...


class MetricCallback(Protocol):
    """Protocol for metric logging callbacks."""

    def __call__(
        self,
        name: str,
        value: int | float,
        step: int | None = None,
        metadata: MetricMetadata | None = None,
    ) -> None:
        """Log a metric."""
        ...
