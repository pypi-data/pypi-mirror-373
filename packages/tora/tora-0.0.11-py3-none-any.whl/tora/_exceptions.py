from typing import Any


class ToraError(Exception):
    """Base exception class for all Tora SDK errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ToraConfigurationError(ToraError):
    """Raised when there's a configuration issue."""


class ToraAuthenticationError(ToraError):
    """Raised when authentication fails."""


class ToraValidationError(ToraError):
    """Raised when input validation fails."""


class ToraNetworkError(ToraError):
    """Raised when network operations fail."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.response_text:
            parts.append(f"Response: {self.response_text}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class ToraAPIError(ToraNetworkError):
    """Raised when the Tora API returns an error response."""


class ToraTimeoutError(ToraNetworkError):
    """Raised when a network operation times out."""


class ToraExperimentError(ToraError):
    """Raised when experiment operations fail."""


class ToraMetricError(ToraError):
    """Raised when metric operations fail."""


class ToraWorkspaceError(ToraError):
    """Raised when workspace operations fail."""


class HTTPStatusError(ToraNetworkError):
    """Legacy exception for HTTP errors. Use ToraNetworkError instead."""

    def __init__(self, message: str, response: Any) -> None:
        status_code = getattr(response, "status_code", None)
        response_text = getattr(response, "text", None)

        super().__init__(
            message=message,
            status_code=status_code,
            response_text=response_text,
        )
        self.response = response
