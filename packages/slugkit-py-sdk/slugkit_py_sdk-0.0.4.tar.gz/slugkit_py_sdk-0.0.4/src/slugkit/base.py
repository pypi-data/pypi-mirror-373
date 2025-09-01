import httpx
import logging
from enum import Enum
from typing import Any, Callable, Self
from pydantic import BaseModel
from .errors import (
    SlugKitError,
    SlugKitConnectionError,
    SlugKitAuthenticationError,
    SlugKitClientError,
    SlugKitServerError,
    SlugKitValidationError,
    SlugKitTimeoutError,
    SlugKitQuotaError,
    SlugKitConfigurationError,
    SlugKitRateLimitError,
    ErrorContext,
    ErrorSeverity,
    get_error_recovery_suggestions,
    categorize_error,
    handle_http_error,
    retry_with_backoff,
)


class Endpoints(str, Enum):
    """API endpoint constants organized in an enum to prevent namespace pollution."""

    PING = "/ping"
    KEY_INFO = "/key-info"
    MINT = "/gen/mint"
    SLICE = "/gen/slice"
    FORGE = "/gen/forge"
    RESET = "/gen/reset"
    STATS = "/gen/stats/latest"
    SERIES_LIST = "/gen/available-series"
    SERIES_INFO = "/gen/series-info"
    PATTERN_INFO = "/gen/pattern-info"
    DICTIONARY_INFO = "/gen/dictionary-info"
    DICTIONARY_TAGS = "/gen/dictionary-tags"


DEFAULT_BATCH_SIZE = 100000


def get_error_recovery_suggestions(error: Exception) -> list[str]:
    """
    Get recovery suggestions for different types of errors.

    Args:
        error: The exception that occurred

    Returns:
        List of human-readable recovery suggestions
    """
    suggestions = []

    if isinstance(error, SlugKitConnectionError):
        suggestions.extend(
            [
                "Check your internet connection",
                "Verify the server URL is correct and accessible",
                "Try again in a few moments (network issues are often temporary)",
                "Check if there are any firewall or proxy restrictions",
            ]
        )

    elif isinstance(error, SlugKitAuthenticationError):
        suggestions.extend(
            [
                "Verify your API key is correct",
                "Check if your API key has expired",
                "Ensure your API key has the required permissions",
                "Contact support if the issue persists",
            ]
        )

    elif isinstance(error, SlugKitValidationError):
        suggestions.extend(
            [
                "Review the pattern syntax in the SlugKit documentation",
                "Check for balanced braces and valid placeholder names",
                "Verify number generator syntax (e.g., {number:3d})",
                "Use validate_pattern() to test your pattern before use",
            ]
        )

    elif isinstance(error, SlugKitTimeoutError):
        suggestions.extend(
            [
                "The operation may complete if you wait longer",
                "Consider reducing the batch size for large operations",
                "Check your network latency to the server",
                "Try again during off-peak hours",
            ]
        )

    elif isinstance(error, SlugKitRateLimitError):
        suggestions.extend(
            [
                "Wait before making additional requests",
                "Implement exponential backoff in your application",
                "Consider upgrading your plan for higher rate limits",
                "Batch multiple operations together when possible",
            ]
        )

    elif isinstance(error, SlugKitQuotaError):
        suggestions.extend(
            [
                "Check your current usage against your plan limits",
                "Consider upgrading your plan for higher quotas",
                "Review and optimize your slug generation patterns",
                "Contact support to discuss quota increases",
            ]
        )

    elif isinstance(error, SlugKitConfigurationError):
        suggestions.extend(
            [
                "Verify your configuration settings",
                "Check environment variables are set correctly",
                "Review the configuration documentation",
                "Ensure all required fields are provided",
            ]
        )

    # Generic suggestions for any error
    suggestions.extend(
        [
            "Check the SlugKit documentation for troubleshooting",
            "Review the error context for additional details",
            "Enable debug logging for more information",
            "Contact support with the full error details if the issue persists",
        ]
    )

    return suggestions


class ErrorSeverity:
    """Error severity levels for categorization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def categorize_error(error: Exception) -> dict:
    """
    Categorize an error with severity and type information.

    Args:
        error: The exception that occurred

    Returns:
        Dictionary with error categorization
    """
    if isinstance(error, SlugKitConnectionError):
        return {"type": "connectivity", "severity": ErrorSeverity.MEDIUM, "retryable": True, "user_actionable": True}

    elif isinstance(error, SlugKitAuthenticationError):
        return {"type": "authentication", "severity": ErrorSeverity.HIGH, "retryable": False, "user_actionable": True}

    elif isinstance(error, SlugKitValidationError):
        return {"type": "validation", "severity": ErrorSeverity.LOW, "retryable": False, "user_actionable": True}

    elif isinstance(error, SlugKitTimeoutError):
        return {"type": "performance", "severity": ErrorSeverity.MEDIUM, "retryable": True, "user_actionable": True}

    elif isinstance(error, SlugKitRateLimitError):
        return {"type": "rate_limiting", "severity": ErrorSeverity.MEDIUM, "retryable": True, "user_actionable": True}

    elif isinstance(error, SlugKitQuotaError):
        return {"type": "quota", "severity": ErrorSeverity.HIGH, "retryable": False, "user_actionable": True}

    elif isinstance(error, SlugKitConfigurationError):
        return {"type": "configuration", "severity": ErrorSeverity.HIGH, "retryable": False, "user_actionable": True}

    elif isinstance(error, SlugKitServerError):
        return {"type": "server", "severity": ErrorSeverity.HIGH, "retryable": True, "user_actionable": False}

    else:
        return {"type": "unknown", "severity": ErrorSeverity.MEDIUM, "retryable": False, "user_actionable": False}


def should_retry_error(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry.

    Args:
        error: The exception that occurred

    Returns:
        True if the error is retryable, False otherwise
    """
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
    """
    Calculate exponential backoff delay with jitter.

    Args:
        attempt: Current attempt number (1-based)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)

    Returns:
        Delay in seconds before next retry
    """
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
    """
    Decorator that adds retry logic with exponential backoff to functions.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        retryable_errors: Custom tuple of retryable exception types
                         (default: uses should_retry_error function)

    Example:
        @retry_with_backoff(max_attempts=5, base_delay=2.0)
        def my_function():
            # This function will be retried up to 5 times
            pass
    """

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


class EventType(Enum):
    """Enum for event types in stats responses."""

    FORGE = "forge"
    MINT = "mint"
    SLICE = "slice"
    RESET = "reset"


class DatePart(Enum):
    """Enum for date parts in stats responses."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    TOTAL = "total"


class KeyScope(Enum):
    """Enum for key scopes in key information."""

    ORG = "org"
    SERIES = "series"


class KeyInfo(BaseModel):
    """Pydantic model representing a key information from the API response."""

    type: str
    """
    The type of key, api-key or sdk-config
    """
    key_scope: KeyScope
    """
    The scope of the key: org or series
    """
    slug: str
    """
    The slug of the key
    """
    org_slug: str
    """
    The slug of the org
    """
    series_slug: str | None = None
    """
    The slug of the series
    """
    scopes: list[str]
    """
    The scopes of the key: forge, mint, slice, reset, stats
    """
    enabled: bool
    """
    Whether the key is enabled
    """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KeyInfo":
        """Create a KeyInfo instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the KeyInfo to a dictionary (compat helper)."""
        return self.model_dump()


class StatsItem(BaseModel):
    """Pydantic model representing a single stats item from the API response."""

    event_type: str
    date_part: str
    total_count: int
    request_count: int
    total_duration_us: int
    avg_duration_us: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatsItem":
        """Create a StatsItem instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the StatsItem to a dictionary (compat helper)."""
        return self.model_dump()


class SeriesInfo(BaseModel):
    """Pydantic model representing series information from the API response."""

    slug: str
    org_slug: str
    name: str
    pattern: str
    max_pattern_length: int
    capacity: str
    generated_count: str
    mtime: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeriesInfo":
        """Create a SeriesInfo instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the SeriesInfo to a dictionary (compat helper)."""
        return self.model_dump()


class PatternInfo(BaseModel):
    """Pydantic model representing pattern information from the API response."""

    pattern: str
    capacity: str
    max_slug_length: int
    complexity: int
    components: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PatternInfo":
        """Create a PatternInfo instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the PatternInfo to a dictionary (compat helper)."""
        return self.model_dump()


class DictionaryInfo(BaseModel):
    """Pydantic model representing dictionary information from the API response."""

    kind: str
    count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DictionaryInfo":
        """Create a DictionaryInfo instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the DictionaryInfo to a dictionary (compat helper)."""
        return self.model_dump()


class DictionaryTag(BaseModel):
    """Pydantic model representing a dictionary tag from the API response."""

    kind: str
    tag: str
    description: str | None = None
    opt_in: bool | None = None
    word_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DictionaryTag":
        """Create a DictionaryTag instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the DictionaryTag to a dictionary (compat helper)."""
        return self.model_dump()


class GeneratorBase:
    def __init__(
        self,
        http_client: Callable[[], httpx.Client],
        *,
        series_slug: str | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        limit: int | None = None,
        dry_run: bool = False,
        sequence: int = 0,
    ):
        self._http_client = http_client
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        self._series_slug = series_slug
        self._batch_size = batch_size
        self._limit = limit
        self._dry_run = dry_run
        self._sequence = sequence

    def with_series(self, series_slug: str) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_batch_size(self, batch_size: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_limit(self, limit: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_dry_run(self) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=True,
            sequence=self._sequence,
        )

    def starting_from(self, sequence: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=sequence,
        )

    def _get_request(self, count: int, sequence: int | None = None) -> dict[str, Any]:
        req = {"count": count}
        if self._dry_run and sequence is not None:
            req["sequence"] = sequence
        if self._series_slug:
            req["series"] = self._series_slug
        return req

    def _get_path(self, stream: bool = False) -> str:
        path = Endpoints.MINT.value
        if self._dry_run:
            path = Endpoints.SLICE.value
        if stream:
            path = f"{path}/stream"
        return path
