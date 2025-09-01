import re
from collections.abc import Mapping
from typing import Any

from ._exceptions import ToraValidationError
from ._types import HPValue


def validate_experiment_name(name: str) -> str:
    """Validate experiment name.

    Args:
        name: The experiment name to validate

    Returns:
        The validated name

    Raises:
        ToraValidationError: If the name is invalid

    """
    if not isinstance(name, str):
        raise ToraValidationError("Experiment name must be a string")

    if not name or not name.strip():
        raise ToraValidationError("Experiment name cannot be empty")

    name = name.strip()
    if len(name) > 255:
        raise ToraValidationError("Experiment name cannot exceed 255 characters")

    if re.search(r'[<>:"/\\|?*\x00-\x1f]', name):
        raise ToraValidationError(
            'Experiment name contains invalid characters. Avoid: < > : " / \\ | ? * and control characters',
        )

    return name


def validate_workspace_id(workspace_id: str | None) -> str | None:
    """Validate workspace ID.

    Args:
        workspace_id: The workspace ID to validate

    Returns:
        The validated workspace ID

    Raises:
        ToraValidationError: If the workspace ID is invalid

    """
    if workspace_id is None:
        return None

    if not isinstance(workspace_id, str):
        raise ToraValidationError("Workspace ID must be a string")

    workspace_id = workspace_id.strip()
    if not workspace_id:
        raise ToraValidationError("Workspace ID cannot be empty")

    if not re.match(r"^[a-zA-Z0-9\-]+$", workspace_id):
        raise ToraValidationError("Workspace ID must contain only letters, numbers, and hyphens")

    return workspace_id


def validate_hyperparams(
    hyperparams: Mapping[str, HPValue] | None,
) -> dict[str, HPValue] | None:
    """Validate hyperparameters.

    Args:
        hyperparams: The hyperparameters to validate

    Returns:
        The validated hyperparameters as a dict

    Raises:
        ToraValidationError: If hyperparameters are invalid

    """
    if hyperparams is None:
        return None

    if not isinstance(hyperparams, Mapping):
        raise ToraValidationError("Hyperparameters must be a mapping (dict-like)")

    validated = {}

    for key, value in hyperparams.items():
        if not isinstance(key, str):
            raise ToraValidationError(f"Hyperparameter key must be string, got {type(key)}")

        if not key.strip():
            raise ToraValidationError("Hyperparameter key cannot be empty")

        key = key.strip()
        if len(key) > 100:
            raise ToraValidationError(f"Hyperparameter key '{key}' exceeds 100 characters")

        if not isinstance(value, str | int | float):
            raise ToraValidationError(
                f"Hyperparameter '{key}' has invalid type {type(value)}. Must be str, int, or float",
            )

        if isinstance(value, float):
            if value != value:
                raise ToraValidationError(f"Hyperparameter '{key}' cannot be NaN")

            if abs(value) == float("inf"):
                raise ToraValidationError(f"Hyperparameter '{key}' cannot be infinite")

            if not (-1e308 <= value <= 1e308):
                raise ToraValidationError(f"Hyperparameter '{key}' float value out of range")

        elif isinstance(value, int):
            if not (-(2**63) <= value <= 2**63 - 1):
                raise ToraValidationError(f"Hyperparameter '{key}' integer value out of range")

        elif isinstance(value, str):
            if len(value) > 1000:
                raise ToraValidationError(f"Hyperparameter '{key}' string value exceeds 1000 characters")

        validated[key] = value

    return validated


def validate_tags(tags: list[str] | None) -> list[str] | None:
    """Validate tags.

    Args:
        tags: The tags to validate

    Returns:
        The validated tags

    Raises:
        ToraValidationError: If tags are invalid

    """
    if tags is None:
        return None

    if not isinstance(tags, list):
        raise ToraValidationError("Tags must be a list")

    if len(tags) > 50:
        raise ToraValidationError("Cannot have more than 50 tags")

    validated: list[str] = []
    seen: set[str] = set()

    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            raise ToraValidationError(f"Tag at index {i} must be a string, got {type(tag)}")

        tag = tag.strip()
        if not tag:
            raise ToraValidationError(f"Tag at index {i} cannot be empty")

        if len(tag) > 50:
            raise ToraValidationError(f"Tag '{tag}' exceeds 50 characters")

        if re.search(r'[<>:"/\\|?*\x00-\x1f,;]', tag):
            raise ToraValidationError(
                f"Tag '{tag}' contains invalid characters. Avoid: < > : \" / \\ | ? * , ; and control characters",
            )

        tag_lower = tag.lower()
        if tag_lower in seen:
            continue

        seen.add(tag_lower)
        validated.append(tag)

    return validated


def validate_metric_name(name: str) -> str:
    """Validate metric name.

    Args:
        name: The metric name to validate

    Returns:
        The validated name

    Raises:
        ToraValidationError: If the name is invalid

    """
    if not isinstance(name, str):
        raise ToraValidationError("Metric name must be a string")

    if not name or not name.strip():
        raise ToraValidationError("Metric name cannot be empty")

    name = name.strip()
    if len(name) > 100:
        raise ToraValidationError("Metric name cannot exceed 100 characters")

    if not re.match(r"^[a-zA-Z0-9_\-./]+$", name):
        raise ToraValidationError(
            "Metric name can only contain letters, numbers, underscore, hyphen, dot, and slash",
        )

    return name


def validate_metric_value(value: Any) -> int | float:
    """Validate metric value.

    Args:
        value: The metric value to validate

    Returns:
        The validated value as int or float

    Raises:
        ToraValidationError: If the value is invalid

    """
    if isinstance(value, bool):
        return int(value)

    if not isinstance(value, int | float):
        try:
            value = float(value)
        except (ValueError, TypeError) as e:
            raise ToraValidationError(f"Metric value must be numeric, got {type(value)}") from e

    if isinstance(value, float):
        if value != value:
            raise ToraValidationError("Metric value cannot be NaN")

        if abs(value) == float("inf"):
            raise ToraValidationError("Metric value cannot be infinite")

        if not (-1e308 <= value <= 1e308):
            raise ToraValidationError("Metric value out of range")

    elif isinstance(value, int):
        if not (-(2**63) <= value <= 2**63 - 1):
            raise ToraValidationError("Metric value out of range")

    return value


def validate_step(step: int | None) -> int | None:
    """Validate step number.

    Args:
        step: The step number to validate

    Returns:
        The validated step number

    Raises:
        ToraValidationError: If the step is invalid

    """
    if step is None:
        return None

    if not isinstance(step, int):
        try:
            step = int(step)
        except (ValueError, TypeError) as e:
            raise ToraValidationError("Step must be an integer") from e

    if step < 0:
        raise ToraValidationError("Step must be non-negative")

    if step > 2**63 - 1:
        raise ToraValidationError("Step value too large")

    return step
