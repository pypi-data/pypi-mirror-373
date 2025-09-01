"""
Tests for the retry logic functionality in SlugKit SDK.

This test suite covers the retry decorator, backoff calculation,
and error classification for retryable vs non-retryable errors.
"""

import pytest
import time
from unittest.mock import Mock, patch
import httpx

from slugkit.base import (
    SlugKitError,
    SlugKitConnectionError,
    SlugKitAuthenticationError,
    SlugKitClientError,
    SlugKitServerError,
    SlugKitRateLimitError,
    should_retry_error,
    calculate_backoff_delay,
    retry_with_backoff,
)


class TestExceptionHierarchy:
    """Test the exception hierarchy and error classification."""

    def test_base_exception_inheritance(self):
        """Test that all exceptions inherit from SlugKitError."""
        assert issubclass(SlugKitConnectionError, SlugKitError)
        assert issubclass(SlugKitAuthenticationError, SlugKitError)
        assert issubclass(SlugKitClientError, SlugKitError)
        assert issubclass(SlugKitServerError, SlugKitError)
        assert issubclass(SlugKitRateLimitError, SlugKitError)

    def test_exception_message_formatting(self):
        """Test that exceptions format messages correctly."""
        error = SlugKitConnectionError("Network timeout")
        assert "Connection error: Network timeout" in str(error)
        assert error.message == "Connection error: Network timeout"

    def test_exception_with_cause(self):
        """Test that exceptions can capture the original cause."""
        original_error = httpx.ConnectError("Connection failed")
        error = SlugKitConnectionError("Network timeout", cause=original_error)
        assert error.cause == original_error


class TestRetryLogic:
    """Test the retry logic and error classification."""

    def test_should_retry_connection_errors(self):
        """Test that connection errors are retryable."""
        connect_error = httpx.ConnectError("Connection failed")
        timeout_error = httpx.TimeoutException("Request timeout")

        assert should_retry_error(connect_error) is True
        assert should_retry_error(timeout_error) is True

    def test_should_retry_server_errors(self):
        """Test that 5xx server errors are retryable."""
        # Mock HTTP error responses
        mock_500_response = Mock()
        mock_500_response.status_code = 500

        mock_599_response = Mock()
        mock_599_response.status_code = 599

        mock_400_response = Mock()
        mock_400_response.status_code = 400

        server_error_500 = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_500_response
        )
        server_error_599 = httpx.HTTPStatusError("599 Unknown", request=Mock(), response=mock_599_response)
        client_error_400 = httpx.HTTPStatusError("400 Bad Request", request=Mock(), response=mock_400_response)

        assert should_retry_error(server_error_500) is True
        assert should_retry_error(server_error_599) is True
        assert should_retry_error(client_error_400) is False

    def test_should_retry_rate_limit_errors(self):
        """Test that rate limit errors are retryable."""
        rate_limit_error = SlugKitRateLimitError("Too many requests")
        assert should_retry_error(rate_limit_error) is True

    def test_should_not_retry_client_errors(self):
        """Test that client errors are not retryable."""
        auth_error = SlugKitAuthenticationError("Invalid API key")
        client_error = SlugKitClientError("Invalid pattern syntax")

        assert should_retry_error(auth_error) is False
        assert should_retry_error(client_error) is False


class TestBackoffCalculation:
    """Test the exponential backoff delay calculation."""

    def test_backoff_exponential_growth(self):
        """Test that backoff delays grow exponentially."""
        delay1 = calculate_backoff_delay(1, base_delay=1.0)
        delay2 = calculate_backoff_delay(2, base_delay=1.0)
        delay3 = calculate_backoff_delay(3, base_delay=1.0)

        # Should be approximately: 1, 2, 4 seconds
        assert 0.5 <= delay1 <= 1.5  # With jitter
        assert 1.5 <= delay2 <= 2.5  # With jitter
        assert 3.0 <= delay3 <= 5.0  # With jitter

    def test_backoff_max_delay_respect(self):
        """Test that backoff respects maximum delay."""
        delay = calculate_backoff_delay(10, base_delay=1.0, max_delay=5.0)
        # With jitter (±25%), the delay can exceed max_delay by up to 25%
        assert delay <= 5.0 * 1.25

    def test_backoff_jitter_variation(self):
        """Test that jitter adds random variation."""
        delays = [calculate_backoff_delay(2, base_delay=1.0) for _ in range(10)]
        # Should have some variation due to jitter
        assert len(set(delays)) > 1


class TestRetryDecorator:
    """Test the retry decorator functionality."""

    def test_retry_decorator_success_on_first_try(self):
        """Test that successful calls don't retry."""
        call_count = 0

        @retry_with_backoff(max_attempts=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_decorator_retries_on_retryable_errors(self):
        """Test that retryable errors trigger retries."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return "success"

        result = failing_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_gives_up_on_non_retryable_errors(self):
        """Test that non-retryable errors don't trigger retries."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise SlugKitAuthenticationError("Invalid API key")

        with pytest.raises(SlugKitAuthenticationError):
            failing_function()

        assert call_count == 1  # Should not retry

    def test_retry_decorator_respects_max_attempts(self):
        """Test that decorator respects maximum attempts."""
        call_count = 0

        @retry_with_backoff(max_attempts=2, base_delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(httpx.ConnectError):
            always_failing_function()

        assert call_count == 2  # Should retry once, then give up

    @pytest.mark.asyncio
    async def test_retry_decorator_async_function(self):
        """Test that retry decorator works with async functions."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        async def async_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return "success"

        result = await async_failing_function()
        assert result == "success"
        assert call_count == 3


class TestRetryIntegration:
    """Test retry logic integration with actual client methods."""

    def test_sync_client_ping_retry(self):
        """Test that sync client ping method has retry logic."""
        from slugkit.sync_client import SyncClient

        # Check that the method has the retry decorator
        ping_method = SyncClient.ping
        assert hasattr(ping_method, "__wrapped__")  # Indicates decorator was applied

    def test_async_client_ping_retry(self):
        """Test that async client ping method has retry logic."""
        from slugkit.async_client import AsyncClient

        # Check that the method has the retry decorator
        ping_method = AsyncClient.ping
        assert hasattr(ping_method, "__wrapped__")  # Indicates decorator was applied


if __name__ == "__main__":
    pytest.main([__file__])
