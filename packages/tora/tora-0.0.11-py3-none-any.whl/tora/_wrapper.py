import atexit
import logging

from ._client import Tora
from ._exceptions import ToraError
from ._types import HPValue

__all__ = [
    "flush",
    "get_experiment_id",
    "get_experiment_url",
    "is_initialized",
    "setup",
    "shutdown",
    "tmetric",
    "tresult",
]

logger = logging.getLogger("tora")
_INSTANCE: Tora | None = None


def _get_client() -> Tora:
    """Get the global client instance."""
    if _INSTANCE is None:
        raise ToraError("Tora client not initialized. Call tora.setup() first.")
    return _INSTANCE


def setup(
    name: str,
    workspace_id: str | None = None,
    description: str | None = None,
    hyperparams: dict[str, HPValue] | None = None,
    tags: list[str] | None = None,
    api_key: str | None = None,
    server_url: str | None = None,
    max_buffer_len: int = 1,
) -> str:
    """Set up the global Tora client with a new experiment.

    This creates a new experiment and initializes the global client.
    After calling this function, you can use tmetric() to log metrics.

    Args:
        name: Name of the experiment
        workspace_id: ID of the workspace to create the experiment in
        description: Optional description of the experiment
        hyperparams: Optional hyperparameters for the experiment
        tags: Optional list of tags for the experiment
        api_key: API key for authentication. Uses TORA_API_KEY env var if not
            provided
        server_url: Base URL for the Tora API. Uses TORA_BASE_URL env var if not
            provided
        max_buffer_len: Maximum number of metrics to buffer before sending
            (default: 1 for immediate sending)

    Returns:
        The experiment ID of the created experiment

    Raises:
        ToraError: If setup fails or client is already initialized
        ToraValidationError: If input validation fails
        ToraAuthenticationError: If authentication fails
        ToraAPIError: If the API request fails
        ToraNetworkError: If there's a network error

    """
    global _INSTANCE
    if _INSTANCE is not None:
        raise ToraError("Tora client already initialized. Call shutdown() first to reinitialize.")

    try:
        _INSTANCE = Tora.create_experiment(
            name=name,
            workspace_id=workspace_id,
            description=description,
            hyperparams=hyperparams,
            tags=tags,
            api_key=api_key,
            server_url=server_url,
            max_buffer_len=max_buffer_len,
        )
        atexit.register(shutdown)
        logger.info(f"Tora experiment created: {_INSTANCE.url}")
        print(f"Tora experiment: {_INSTANCE.url}")
        return _INSTANCE.experiment_id

    except Exception:
        _INSTANCE = None
        raise


def tmetric(name: str, value: int | float, step: int | None = None) -> None:
    """Log a training metric using the global Tora client.

    Args:
        name: Name of the metric
        value: Numeric value of the metric
        step: Optional step number for the metric

    Raises:
        ToraError: If the global client is not initialized
        ToraValidationError: If input validation fails
        ToraMetricError: If logging fails

    """
    client = _get_client()
    client.metric(name, value, step)


def tresult(name: str, value: int | float) -> None:
    """Log a result using the global Tora client.

    Args:
        name: Name of the result
        value: Numeric value of the result

    Raises:
        ToraError: If the global client is not initialized
        ToraValidationError: If input validation fails
        ToraMetricError: If logging fails

    """
    client = _get_client()
    client.result(name, value)


def flush() -> None:
    """Flush all buffered metrics using the global client.

    Raises:
        ToraError: If the global client is not initialized

    """
    if _INSTANCE is not None:
        _INSTANCE.flush()


def shutdown() -> None:
    """Shutdown the global Tora client and flush all metrics.

    After calling this function, you need to call setup() again
    to reinitialize the client.
    """
    global _INSTANCE
    if _INSTANCE is not None:
        try:
            _INSTANCE.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            _INSTANCE = None


def is_initialized() -> bool:
    """Check if the global Tora client is initialized.

    Returns:
        True if the client is initialized, False otherwise

    """
    return _INSTANCE is not None and not _INSTANCE.is_closed


def get_experiment_id() -> str | None:
    """Get the experiment ID of the global client.

    Returns:
        The experiment ID if initialized, None otherwise

    """
    if _INSTANCE is not None and not _INSTANCE.is_closed:
        return _INSTANCE.experiment_id
    return None


def get_experiment_url() -> str | None:
    """Get the web URL for the current experiment.

    Returns:
        The experiment URL if initialized, None otherwise

    """
    if _INSTANCE is not None and not _INSTANCE.is_closed:
        return _INSTANCE.url
    return None
