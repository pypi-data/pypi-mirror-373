import logging
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from ._config import TORA_API_KEY, TORA_BASE_URL
from ._exceptions import (
    HTTPStatusError,
    ToraAPIError,
    ToraAuthenticationError,
    ToraConfigurationError,
    ToraExperimentError,
    ToraMetricError,
    ToraNetworkError,
    ToraValidationError,
)
from ._http import HttpClient
from ._types import HPValue, MetricMetadata
from ._validation import (
    validate_experiment_name,
    validate_hyperparams,
    validate_metric_name,
    validate_metric_value,
    validate_step,
    validate_tags,
    validate_workspace_id,
)

__all__ = ["Tora", "create_workspace"]

logger = logging.getLogger("tora")


def _to_tora_hp(hp: Mapping[str, HPValue]) -> list[dict[str, HPValue]]:
    """Convert hyperparameters dict to Tora API format."""
    return [{"key": k, "value": v} for k, v in hp.items()]


def _from_tora_hp(tora_hp: list[dict[str, Any]]) -> dict[str, HPValue]:
    """Convert Tora API hyperparameters format to dict."""
    return {item["key"]: item["value"] for item in tora_hp}


def create_workspace(
    name: str,
    description: str | None = None,
    api_key: str | None = None,
    server_url: str | None = None,
) -> dict[str, Any]:
    """Create a new Tora workspace.

    Args:
        name: The name for the new workspace
        description: An optional description for the workspace
        api_key: API key for authentication. If not provided, uses TORA_API_KEY
            environment variable
        server_url: The base URL of the Tora server. If not provided, uses TORA_BASE_URL

    Returns:
        The workspace data from the API response

    Raises:
        ToraAuthenticationError: If no API key is provided
        ToraValidationError: If the workspace name is invalid
        ToraAPIError: If the API request fails
        ToraNetworkError: If there's a network error
    """
    if not name or not isinstance(name, str):
        raise ToraValidationError("Workspace name must be a non-empty string")

    name = name.strip()
    if len(name) > 255:
        raise ToraValidationError("Workspace name cannot exceed 255 characters")

    if description is not None and len(description) > 1000:
        raise ToraValidationError("Workspace description cannot exceed 1000 characters")

    server_url = server_url or TORA_BASE_URL
    resolved_api_key = Tora._get_api_key(api_key)

    if not resolved_api_key:
        raise ToraAuthenticationError("API key is required to create a workspace")

    headers = {
        "x-api-key": resolved_api_key,
        "Content-Type": "application/json",
    }

    try:
        with HttpClient(base_url=server_url, headers=headers) as client:
            response = client.post("/workspaces", json={"name": name, "description": description})
            response.raise_for_status()

            json_data = response.json()
            if not isinstance(json_data, dict) or "data" not in json_data:
                raise ToraAPIError("Invalid response format from workspace creation API")

            return json_data["data"]

    except HTTPStatusError as e:
        if e.status_code == 401:
            raise ToraAuthenticationError("Invalid API key") from e
        if e.status_code == 400:
            raise ToraValidationError("Invalid workspace data") from e
        raise ToraAPIError(f"API error: {e}") from e
    except ToraNetworkError:
        raise
    except Exception as e:
        logger.exception("Unexpected error creating workspace")
        raise ToraAPIError(f"Unexpected error creating workspace: {e}") from e


class Tora:
    """Main client for interacting with Tora experiment tracking.

    This class provides methods for logging metrics, managing experiments,
    and interacting with the Tora API. It supports both buffered and immediate
    metric logging for optimal performance.

    Example:
        >>> tora = Tora.create_experiment("my-experiment", workspace_id="workspace-123")
        >>> tora.log("accuracy", 0.95, step=100)
        >>> tora.shutdown()
    """

    def __init__(
        self,
        experiment_id: str,
        url: str,
        description: str | None = None,
        hyperparams: Mapping[str, HPValue] | None = None,
        tags: list[str] | None = None,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ) -> None:
        """Initialize a Tora client for an existing experiment.

        Args:
            experiment_id: The ID of the experiment
            url: link to the experiment
            description: Optional description of the experiment
            hyperparams: Optional hyperparameters for the experiment
            tags: Optional list of tags for the experiment
            max_buffer_len: Maximum number of metrics to buffer before sending
                (default: 25)
            api_key: API key for authentication. Uses TORA_API_KEY env var if not
                provided
            server_url: Base URL for the Tora API. Uses TORA_BASE_URL env var if not
                provided

        Raises:
            ToraValidationError: If experiment_id is invalid
            ToraConfigurationError: If server configuration is invalid

        """
        if not experiment_id or not isinstance(experiment_id, str):
            raise ToraValidationError("Experiment ID must be a non-empty string")

        self._experiment_id = experiment_id.strip()
        self._url = url
        self._description = description
        self._hyperparams = hyperparams
        self._tags = tags
        self._max_buffer_len = max(1, int(max_buffer_len))
        self._buffer: list[dict[str, Any]] = []
        self._api_key = api_key or TORA_API_KEY
        self._closed = False

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        if server_url is None:
            server_url = TORA_BASE_URL

        if not server_url:
            raise ToraConfigurationError(
                "Server URL must be provided via parameter or TORA_BASE_URL environment variable",
            )

        try:
            self._http_client = HttpClient(base_url=server_url, headers=headers)
        except Exception as e:
            raise ToraConfigurationError(f"Failed to initialize HTTP client: {e}") from e

    @staticmethod
    def _get_api_key(api_key: str | None) -> str | None:
        """Resolve API key from parameter or environment variable.

        Args:
            api_key: API key parameter

        Returns:
            Resolved API key or None

        """
        key = api_key or TORA_API_KEY
        if key is None:
            logger.warning("Tora API key not provided. Operating in anonymous mode.")
        return key

    @classmethod
    def create_experiment(
        cls,
        name: str,
        workspace_id: str | None = None,
        description: str | None = None,
        hyperparams: Mapping[str, HPValue] | None = None,
        tags: list[str] | None = None,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ) -> "Tora":
        """Create a new experiment and return a Tora client instance.

        Args:
            name: Name of the experiment
            workspace_id: ID of the workspace to create the experiment in
            description: Optional description of the experiment
            hyperparams: Optional hyperparameters for the experiment
            tags: Optional list of tags for the experiment
            max_buffer_len: Maximum number of metrics to buffer before sending
                (default: 25)
            api_key: API key for authentication. Uses TORA_API_KEY env var if not
                provided
            server_url: Base URL for the Tora API. Uses TORA_BASE_URL env var if not
                provided

        Returns:
            A Tora client instance for the created experiment

        Raises:
            ToraValidationError: If input validation fails
            ToraAuthenticationError: If authentication fails
            ToraAPIError: If the API request fails
            ToraNetworkError: If there's a network error

        """
        name = validate_experiment_name(name)
        workspace_id = validate_workspace_id(workspace_id)
        hyperparams = validate_hyperparams(hyperparams)
        tags = validate_tags(tags)

        resolved_api_key = cls._get_api_key(api_key)
        if server_url is None:
            server_url = TORA_BASE_URL

        if not server_url:
            raise ToraConfigurationError("Server URL must be provided")

        data = cls._create_payload(name, workspace_id, description, hyperparams, tags)
        headers = {"Content-Type": "application/json"}
        if resolved_api_key:
            headers["x-api-key"] = resolved_api_key

        try:
            with HttpClient(base_url=server_url, headers=headers) as client:
                logger.debug(f"Creating experiment with data: {data}")
                response = client.post("/experiments", json=data)
                response.raise_for_status()

                json_data = response.json()
                if not isinstance(json_data, dict) or "data" not in json_data:
                    raise ToraAPIError("Invalid response format from experiment creation API")

                experiment_data = json_data["data"]
                experiment_id = experiment_data["id"]
                experiment_url = experiment_data["url"]

                if not experiment_id:
                    raise ToraAPIError("No experiment ID in response")

        except HTTPStatusError as e:
            if e.status_code == 401:
                raise ToraAuthenticationError("Invalid API key") from e
            if e.status_code == 400:
                raise ToraValidationError("Invalid experiment data") from e
            if e.status_code == 404:
                raise ToraValidationError("Workspace not found") from e
            raise ToraAPIError(f"API error: {e}") from e
        except ToraNetworkError:
            raise
        except Exception as e:
            logger.exception("Unexpected error creating experiment")
            raise ToraAPIError(f"Unexpected error creating experiment: {e}") from e

        return cls(
            experiment_id=experiment_id,
            url=experiment_url,
            description=description,
            hyperparams=hyperparams,
            tags=tags,
            server_url=server_url,
            max_buffer_len=max_buffer_len,
            api_key=resolved_api_key,
        )

    @classmethod
    def _create_payload(
        cls,
        name: str,
        workspace_id: str | None,
        description: str | None,
        hyperparams: Mapping[str, HPValue] | None,
        tags: list[str] | None,
    ) -> dict[str, Any]:
        """Create the payload for experiment creation API.

        Args:
            name: Experiment name
            workspace_id: Optional workspace ID
            description: Optional description
            hyperparams: Optional hyperparameters
            tags: Optional tags

        Returns:
            Dictionary payload for the API request

        """
        data: dict[str, Any] = {"name": name}

        if workspace_id:
            data["workspaceId"] = workspace_id
        if description:
            data["description"] = description
        if hyperparams:
            data["hyperparams"] = _to_tora_hp(hyperparams)
        if tags:
            data["tags"] = tags

        return data

    @classmethod
    def load_experiment(
        cls,
        experiment_id: str,
        max_buffer_len: int = 25,
        api_key: str | None = None,
        server_url: str | None = None,
    ) -> "Tora":
        """Load an existing experiment and return a Tora client instance.

        Args:
            experiment_id: ID of the experiment to load
            max_buffer_len: Maximum number of metrics to buffer before sending
                (default: 25)
            api_key: API key for authentication. Uses TORA_API_KEY env var if not
                provided
            server_url: Base URL for the Tora API. Uses TORA_BASE_URL env var if not
                provided

        Returns:
            A Tora client instance for the loaded experiment

        Raises:
            ToraValidationError: If experiment_id is invalid
            ToraExperimentError: If experiment is not found
            ToraAPIError: If the API request fails
            ToraNetworkError: If there's a network error

        """
        if not experiment_id or not isinstance(experiment_id, str):
            raise ToraValidationError("Experiment ID must be a non-empty string")

        experiment_id = experiment_id.strip()
        if server_url is None:
            server_url = TORA_BASE_URL

        if not server_url:
            raise ToraConfigurationError("Server URL must be provided")

        resolved_api_key = cls._get_api_key(api_key)
        headers = {}
        if resolved_api_key:
            headers["x-api-key"] = resolved_api_key

        try:
            with HttpClient(base_url=server_url, headers=headers) as client:
                response = client.get(f"/experiments/{experiment_id}")
                response.raise_for_status()

                json_data = response.json()
                if not isinstance(json_data, dict) or "data" not in json_data:
                    raise ToraAPIError("Invalid response format from experiment API")

                data = json_data["data"]

        except HTTPStatusError as e:
            if e.status_code == 404:
                raise ToraExperimentError(f"Experiment {experiment_id} not found") from e
            if e.status_code == 401:
                raise ToraAuthenticationError("Invalid API key") from e
            raise ToraAPIError(f"API error loading experiment: {e}") from e
        except ToraNetworkError:
            raise
        except Exception as e:
            logger.exception("Unexpected error loading experiment")
            raise ToraAPIError(f"Unexpected error loading experiment: {e}") from e

        hyperparams = None
        if data.get("hyperparams"):
            try:
                hyperparams = _from_tora_hp(data["hyperparams"])
            except Exception as e:
                logger.warning(f"Failed to parse hyperparameters: {e}")

        return cls(
            experiment_id=data["id"],
            url=data["url"],
            description=data.get("description"),
            hyperparams=hyperparams,
            tags=data.get("tags"),
            max_buffer_len=max_buffer_len,
            api_key=resolved_api_key,
            server_url=server_url,
        )

    def _log(
        self,
        name: str,
        value: int | float,
        step: int | None = None,
        metadata: MetricMetadata | None = None,
    ) -> None:
        """Log a value.

        Logs are buffered and sent in batches when the buffer reaches max_buffer_len.
        Call flush() or shutdown() to send remaining buffered metrics immediately.

        Args:
            name: Name of the log
            value: Numeric value of the log
            step: Optional step number for the log
            metadata: Optional metadata dictionary for the log

        Raises:
            ToraValidationError: If input validation fails
            ToraMetricError: If the client is closed
        """
        if self._closed:
            raise ToraMetricError("Cannot log metrics on a closed Tora client")

        name = validate_metric_name(name)
        value = validate_metric_value(value)
        step = validate_step(step)

        if metadata is not None:
            try:
                import json

                metadata_str = json.dumps(metadata)
                if len(metadata_str) > 10000:
                    raise ToraValidationError("Metadata too large (max 10KB)")
            except (TypeError, ValueError) as e:
                raise ToraValidationError(f"Metadata must be JSON serializable: {e}") from e

        log_entry = {
            "name": name,
            "msg_id": str(uuid4()),
            "value": value,
            "step": step,
            "metadata": metadata,
        }

        self._buffer.append(log_entry)
        logger.debug(f"Logged metric: {name}={value} (step={step})")

        if len(self._buffer) >= self._max_buffer_len:
            self._write_logs()

    def metric(
        self,
        name: str,
        value: int | float,
        step_or_epoch: int,
    ) -> None:
        """Log a metric value.

        Metrics are buffered and sent in batches when the buffer reaches max_buffer_len.
        Call flush() or shutdown() to send remaining buffered metrics immediately.

        Args:
            name: Name of the metric
            value: Numeric value of the metric
            step_or_epoch: Step number or epoch of the metric
            metadata: Additional metadata for the metric

        Raises:
            ToraValidationError: If input validation fails
            ToraMetricError: If the client is closed
        """
        if step_or_epoch is None:
            raise ToraValidationError("step_or_epoch cannot be None")

        self._log(name=name, value=value, step=step_or_epoch, metadata={"type": "metric"})

    def result(self, name: str, value: int | float):
        """Log a experiment result.

        Results are buffered and sent in batches when the buffer reaches max_buffer_len.
        Call flush() or shutdown() to send remaining buffered metrics immediately.

        Args:
            name: Name of the result
            value: Numeric value of the result

        Raises:
            ToraValidationError: If input validation fails
            ToraMetricError: If the client is closed
        """
        self._log(name=name, value=value, step=None, metadata={"type": "result"})

    def _write_logs(self) -> None:
        """Write buffered metrics to the API.

        This method is called automatically when the buffer is full or during
        shutdown.
        It handles errors gracefully and logs them without raising exceptions.
        """
        if not self._buffer or self._closed:
            return

        logs = self._buffer.copy()

        try:
            logger.debug(f"Sending {len(logs)} metrics for experiment {self._experiment_id}")
            response = self._http_client.post(
                f"/experiments/{self._experiment_id}/logs/batch",
                json={"logs": logs},
                timeout=120,
            )
            response.raise_for_status()
            self._buffer = []
            logger.debug(f"Successfully sent {len(logs)} metrics")

        except HTTPStatusError as e:
            error_msg = f"Failed to write metrics (HTTP {e.status_code})"
            if hasattr(e, "response") and hasattr(e.response, "text"):
                error_msg += f": {e.response.text[:200]}"
            logger.error(error_msg)

        except ToraNetworkError as e:
            logger.error(f"Network error writing metrics: {e}")

        except Exception as e:
            logger.error(f"Unexpected error writing metrics: {e}")

    def flush(self) -> None:
        """Immediately send all buffered metrics to the API.

        This method forces sending of buffered metrics without waiting for
        the buffer to fill up. Useful for ensuring metrics are sent at
        specific points in your code.

        Raises:
            ToraMetricError: If the client is closed

        """
        if self._closed:
            raise ToraMetricError("Cannot flush metrics on a closed Tora client")

        if self._buffer:
            logger.debug(f"Flushing {len(self._buffer)} buffered metrics")
            self._write_logs()

    def shutdown(self) -> None:
        """Flush all buffered metrics and close the client.

        This method should be called when you're done with the Tora client
        to ensure all metrics are sent and resources are cleaned up.
        After calling shutdown(), the client cannot be used for logging.
        """
        if self._closed:
            return

        if self._buffer:
            logger.info(f"Tora shutting down. Sending {len(self._buffer)} remaining metrics...")
            self._write_logs()

        self._http_client.close()
        self._closed = True
        logger.debug("Tora client shut down")

    @property
    def max_buffer_len(self) -> int:
        """Get the maximum buffer length."""
        return self._max_buffer_len

    @max_buffer_len.setter
    def max_buffer_len(self, value: int) -> None:
        """Set the maximum buffer length.

        Args:
            value: New maximum buffer length (minimum 1)

        """
        if not isinstance(value, int) or value < 1:
            raise ToraValidationError("max_buffer_len must be a positive integer")
        self._max_buffer_len = value

    @property
    def experiment_id(self) -> str:
        """Get the experiment ID."""
        return self._experiment_id

    @property
    def url(self) -> str:
        """Returns the experiment url"""
        return self._url

    @property
    def buffer_size(self) -> int:
        """Get the current number of buffered metrics."""
        return len(self._buffer)

    @property
    def is_closed(self) -> bool:
        """Check if the client is closed."""
        return self._closed

    def __enter__(self) -> "Tora":
        """Enter context manager."""
        return self

    def __exit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit context manager, ensuring logs are flushed."""
        self.shutdown()

    def log_metrics(self, metrics: dict[str, int | float], step: int | None = None) -> None:
        """Log multiple metrics at once.

        Args:
            metrics: Dictionary of metric names to values
            step: Optional step number for all metrics

        Raises:
            ToraValidationError: If input validation fails
            ToraMetricError: If the client is closed

        """
        for name, value in metrics.items():
            self._log(name, value, step=step)

    def __repr__(self) -> str:
        """Return string representation of the Tora client."""
        status = "closed" if self.is_closed else "open"
        return f"Tora(experiment_id='{self.experiment_id}', status='{status}', buffer_size={self.buffer_size})"
