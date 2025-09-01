"""
Error handling utilities for SlugKit SDK.
"""

import time
from typing import Optional, Any
from enum import Enum
import httpx


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorContext:
    """Structured error context for better error reporting and debugging."""

    def __init__(
        self,
        operation: str,
        endpoint: Optional[str] = None,
        base_url: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        self.operation = operation
        self.endpoint = endpoint
        self.base_url = base_url
        self.user_id = user_id
        self.timestamp = time.time()
        self.additional_data = kwargs

        # Store all kwargs as attributes for easy access
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "operation": self.operation,
            "endpoint": self.endpoint,
            "base_url": self.base_url,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "additional_data": self.additional_data,
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [f"Operation: {self.operation}"]
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        if self.base_url:
            parts.append(f"Base URL: {self.base_url}")
        if self.user_id:
            parts.append(f"User ID: {self.user_id}")
        if self.additional_data:
            parts.append(f"Additional: {self.additional_data}")
        return " | ".join(parts)


class SlugKitError(Exception):
    """Base exception for all SlugKit errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        timestamp: Optional[float] = None,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext("unknown")
        self.cause = cause
        self.timestamp = timestamp or time.time()

    def add_context(self, **kwargs) -> "SlugKitError":
        """Add additional context information."""
        for key, value in kwargs.items():
            setattr(self.context, key, value)
        return self

    def get_context_info(self) -> str:
        """Get formatted context information."""
        return str(self.context)

    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [self.message]
        if self.context:
            parts.append(f"Context: {self.get_context_info()}")
        if self.cause:
            parts.append(f"Caused by: {str(self.cause)}")
        return " | ".join(parts)


class SlugKitConnectionError(SlugKitError):
    """Network connectivity or connection-related errors."""

    pass


class SlugKitAuthenticationError(SlugKitError):
    """Authentication and authorization errors."""

    pass


class SlugKitClientError(SlugKitError):
    """Client-side errors (bad requests, validation, etc.)."""

    pass


class SlugKitServerError(SlugKitError):
    """Server-side errors."""

    pass


class SlugKitRateLimitError(SlugKitError):
    """Rate limiting and throttling errors."""

    pass


class SlugKitValidationError(SlugKitError):
    """Data validation and format errors."""

    pass


class SlugKitTimeoutError(SlugKitError):
    """Request timeout errors."""

    pass


class SlugKitQuotaError(SlugKitError):
    """Quota and usage limit errors."""

    pass


class SlugKitConfigurationError(SlugKitError):
    """Configuration and setup errors."""

    pass


def get_error_recovery_suggestions(error: SlugKitError) -> list[str]:
    """Get actionable recovery suggestions for an error."""
    suggestions = []

    if isinstance(error, SlugKitConnectionError):
        suggestions.extend(
            [
                "Verify the server URL is correct and accessible",
                "Check your internet connection",
                "Try again in a few moments (network issues are often temporary)",
                "Verify firewall/proxy settings if applicable",
            ]
        )

    elif isinstance(error, SlugKitAuthenticationError):
        suggestions.extend(
            [
                "Verify your API key is correct and not expired",
                "Check that your API key has the required permissions",
                "Ensure the API key is properly formatted",
                "Contact support if the issue persists",
            ]
        )

    elif isinstance(error, SlugKitClientError):
        suggestions.extend(
            [
                "Review the request parameters and format",
                "Check the API documentation for correct usage",
                "Verify all required fields are provided",
                "Ensure data types match expected formats",
            ]
        )

    elif isinstance(error, SlugKitValidationError):
        suggestions.extend(
            [
                "Review the input data for format issues",
                "Check that all required fields are present",
                "Verify data types and constraints",
                "Use the validate_pattern tool to check pattern syntax",
            ]
        )

    elif isinstance(error, SlugKitRateLimitError):
        suggestions.extend(
            [
                "Wait before making additional requests",
                "Reduce request frequency",
                "Consider implementing exponential backoff",
                "Check your current usage limits",
            ]
        )

    elif isinstance(error, SlugKitServerError):
        suggestions.extend(
            [
                "Try again in a few moments",
                "Check the service status page",
                "Contact support if the issue persists",
                "Verify the request is not too complex",
            ]
        )

    elif isinstance(error, SlugKitTimeoutError):
        suggestions.extend(
            [
                "Check your network connection",
                "Try again with a longer timeout",
                "Reduce request complexity if possible",
                "Verify server responsiveness",
            ]
        )

    elif isinstance(error, SlugKitQuotaError):
        suggestions.extend(
            [
                "Check your current usage and limits",
                "Consider upgrading your plan if needed",
                "Review usage patterns and optimize",
                "Contact support for quota increases",
            ]
        )

    else:
        suggestions.extend(
            [
                "Review the error message for specific details",
                "Check the API documentation",
                "Try with simpler parameters first",
                "Contact support if the issue persists",
            ]
        )

    return suggestions


def categorize_error(error: SlugKitError) -> dict[str, Any]:
    """Categorize an error for better understanding and handling."""
    if isinstance(error, SlugKitConnectionError):
        severity = ErrorSeverity.HIGH
        category = "connectivity"
        retryable = True
    elif isinstance(error, SlugKitAuthenticationError):
        severity = ErrorSeverity.CRITICAL
        category = "authentication"
        retryable = False
    elif isinstance(error, SlugKitClientError):
        severity = ErrorSeverity.MEDIUM
        category = "client"
        retryable = False
    elif isinstance(error, SlugKitServerError):
        severity = ErrorSeverity.HIGH
        category = "server"
        retryable = True
    elif isinstance(error, SlugKitRateLimitError):
        severity = ErrorSeverity.MEDIUM
        category = "rate_limit"
        retryable = True
    elif isinstance(error, SlugKitValidationError):
        severity = ErrorSeverity.LOW
        category = "validation"
        retryable = False
    elif isinstance(error, SlugKitTimeoutError):
        severity = ErrorSeverity.MEDIUM
        category = "timeout"
        retryable = True
    elif isinstance(error, SlugKitQuotaError):
        severity = ErrorSeverity.HIGH
        category = "quota"
        retryable = False
    elif isinstance(error, SlugKitConfigurationError):
        severity = ErrorSeverity.CRITICAL
        category = "configuration"
        retryable = False
    else:
        severity = ErrorSeverity.MEDIUM
        category = "unknown"
        retryable = False

    return {
        "severity": severity.value,
        "category": category,
        "retryable": retryable,
        "suggestions": get_error_recovery_suggestions(error),
    }


def handle_http_error(
    error: "httpx.HTTPStatusError",
    operation: str,
    endpoint: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> Exception:
    """Convert HTTP errors to appropriate SlugKit exceptions with context.

    This is a free function that can be used by any class that needs error handling.

    Args:
        error: The httpx.HTTPStatusError that occurred
        operation: Description of the operation being performed
        endpoint: The API endpoint that was called
        base_url: The base URL of the API
        **kwargs: Additional context information

    Returns:
        An appropriate SlugKit exception with full context
    """
    context = ErrorContext(operation=operation, endpoint=endpoint, base_url=base_url, **kwargs)

    if error.response.status_code == 401:
        return SlugKitAuthenticationError("Invalid or expired API key", cause=error, context=context)
    elif error.response.status_code == 403:
        return SlugKitAuthenticationError("Insufficient permissions", cause=error, context=context)
    elif error.response.status_code == 404:
        return SlugKitClientError("Resource not found", cause=error, context=context)
    elif error.response.status_code == 422:
        return SlugKitValidationError("Invalid request data", cause=error, context=context)
    elif error.response.status_code == 429:
        return SlugKitRateLimitError("Rate limit exceeded", cause=error, context=context)
    elif error.response.status_code >= 500:
        return SlugKitServerError("Server error", cause=error, context=context)
    else:
        return SlugKitClientError(
            f"HTTP {error.response.status_code}: {error.response.text}", cause=error, context=context
        )


def should_retry_error(error: Exception) -> bool:
    """Determine if an error should trigger a retry."""
    # Retry on connection errors, timeouts, and 5xx server errors
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
        return True

    # Retry on SlugKit connection errors
    if isinstance(error, SlugKitConnectionError):
        return True

    # Retry on 5xx server errors (server issues)
    if isinstance(error, httpx.HTTPStatusError):
        return 500 <= error.response.status_code < 600

    # Retry on rate limit errors (temporary)
    if isinstance(error, SlugKitRateLimitError):
        return True

    return False


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay with jitter."""
    import random

    # Exponential backoff: base_delay * 2^(attempt-1)
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

    # Add jitter (±25% random variation)
    jitter = random.uniform(0.75, 1.25)
    delay = delay * jitter

    return delay


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_errors: tuple[type[Exception], ...] | None = None,
):
    """Decorator that adds retry logic with exponential backoff to functions."""

    def decorator(func):
        import functools
        import asyncio

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = should_retry_error(e)

                    if not should_retry or attempt == max_attempts:
                        break

                    # Calculate delay and wait
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay)
                    import time

                    time.sleep(delay)

            # Re-raise the last error
            raise last_error

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = should_retry_error(e)

                    if not should_retry or attempt == max_attempts:
                        break

                    # Calculate delay and wait
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay)
                    await asyncio.sleep(delay)

            # Re-raise the last error
            raise last_error

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
