"""
Tests for the enhanced error handling functionality in SlugKit SDK.

This test suite covers the new error types, error context, recovery suggestions,
and error categorization features.
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
    SlugKitValidationError,
    SlugKitTimeoutError,
    SlugKitQuotaError,
    SlugKitConfigurationError,
    ErrorContext,
    ErrorSeverity,
    get_error_recovery_suggestions,
    categorize_error,
    should_retry_error,
)


class TestEnhancedErrorTypes:
    """Test the new specific error types."""

    def test_validation_error_with_pattern(self):
        """Test SlugKitValidationError with pattern information."""
        error = SlugKitValidationError("Invalid syntax", pattern="{invalid-{pattern}")

        assert "Validation error: Invalid syntax" in str(error)
        assert error.pattern == "{invalid-{pattern}"
        assert error.context is None

    def test_timeout_error_with_duration(self):
        """Test SlugKitTimeoutError with timeout information."""
        error = SlugKitTimeoutError("Operation timed out", timeout_seconds=30.0)

        assert "Timeout error: Operation timed out" in str(error)
        assert error.timeout_seconds == 30.0

    def test_quota_error_with_details(self):
        """Test SlugKitQuotaError with quota information."""
        error = SlugKitQuotaError("Daily limit exceeded", quota_type="daily", limit=1000)

        assert "Quota error: Daily limit exceeded" in str(error)
        assert error.quota_type == "daily"
        assert error.limit == 1000

    def test_configuration_error_with_key(self):
        """Test SlugKitConfigurationError with configuration key."""
        error = SlugKitConfigurationError("Missing required setting", config_key="API_KEY")

        assert "Configuration error: Missing required setting" in str(error)
        assert error.config_key == "API_KEY"


class TestErrorContext:
    """Test the ErrorContext class."""

    def test_error_context_creation(self):
        """Test creating error context with various parameters."""
        context = ErrorContext(
            operation="mint_slugs", endpoint="/api/v1/mint", request_id="req-123", user_id="user-456"
        )

        assert context.operation == "mint_slugs"
        assert context.endpoint == "/api/v1/mint"
        assert context.request_id == "req-123"
        assert context.user_id == "user-456"
        assert context.timestamp > 0

    def test_error_context_to_dict(self):
        """Test converting error context to dictionary."""
        context = ErrorContext(operation="validate_pattern", endpoint="/api/v1/validate", request_id="req-789")

        context_dict = context.to_dict()
        assert context_dict["operation"] == "validate_pattern"
        assert context_dict["endpoint"] == "/api/v1/validate"
        assert context_dict["request_id"] == "req-789"
        assert "timestamp" in context_dict

    def test_error_context_string_representation(self):
        """Test string representation of error context."""
        context = ErrorContext("test_operation", "/test/endpoint", "req-123")

        context_str = str(context)
        assert "Operation: test_operation" in context_str
        assert "Endpoint: /test/endpoint" in context_str
        assert "Request ID: req-123" in context_str

    def test_error_context_without_optional_fields(self):
        """Test error context with minimal parameters."""
        context = ErrorContext("simple_operation")

        assert context.operation == "simple_operation"
        assert context.endpoint is None
        assert context.request_id is None
        assert context.timestamp > 0


class TestEnhancedBaseError:
    """Test the enhanced base SlugKitError class."""

    def test_error_with_context(self):
        """Test error with error context."""
        context = ErrorContext("test_operation", "/test/endpoint")
        error = SlugKitError("Test error message", context=context)

        assert error.context == context
        assert error.timestamp > 0
        assert "test_operation" in str(error)

    def test_error_with_cause(self):
        """Test error with cause exception."""
        original_error = ValueError("Original error")
        error = SlugKitError("Test error", cause=original_error)

        assert error.cause == original_error
        assert "Caused by: ValueError: Original error" in str(error)

    def test_error_add_context(self):
        """Test adding context to an existing error."""
        error = SlugKitError("Test error")
        context = ErrorContext("added_operation")

        error.add_context(context)
        assert error.context == context

    def test_error_get_context_info(self):
        """Test getting context information as dictionary."""
        context = ErrorContext("test_operation", "/test/endpoint", "req-123")
        error = SlugKitError("Test error", context=context)

        context_info = error.get_context_info()
        assert context_info["operation"] == "test_operation"
        assert context_info["endpoint"] == "/test/endpoint"
        assert context_info["request_id"] == "req-123"


class TestErrorRecoverySuggestions:
    """Test the error recovery suggestions functionality."""

    def test_connection_error_suggestions(self):
        """Test recovery suggestions for connection errors."""
        error = SlugKitConnectionError("Network timeout")
        suggestions = get_error_recovery_suggestions(error)

        assert "Check your internet connection" in suggestions
        assert "Verify the server URL is correct and accessible" in suggestions
        assert "Try again in a few moments (network issues are often temporary)" in suggestions
        assert "Check if there are any firewall or proxy restrictions" in suggestions

    def test_authentication_error_suggestions(self):
        """Test recovery suggestions for authentication errors."""
        error = SlugKitAuthenticationError("Invalid API key")
        suggestions = get_error_recovery_suggestions(error)

        assert "Verify your API key is correct" in suggestions
        assert "Check if your API key has expired" in suggestions
        assert "Ensure your API key has the required permissions" in suggestions

    def test_validation_error_suggestions(self):
        """Test recovery suggestions for validation errors."""
        error = SlugKitValidationError("Invalid pattern syntax")
        suggestions = get_error_recovery_suggestions(error)

        assert "Review the pattern syntax in the SlugKit documentation" in suggestions
        assert "Check for balanced braces and valid placeholder names" in suggestions
        assert "Use validate_pattern() to test your pattern before use" in suggestions

    def test_timeout_error_suggestions(self):
        """Test recovery suggestions for timeout errors."""
        error = SlugKitTimeoutError("Operation timed out")
        suggestions = get_error_recovery_suggestions(error)

        assert "The operation may complete if you wait longer" in suggestions
        assert "Consider reducing the batch size for large operations" in suggestions
        assert "Check your network latency to the server" in suggestions

    def test_rate_limit_error_suggestions(self):
        """Test recovery suggestions for rate limit errors."""
        error = SlugKitRateLimitError("Too many requests")
        suggestions = get_error_recovery_suggestions(error)

        assert "Wait before making additional requests" in suggestions
        assert "Implement exponential backoff in your application" in suggestions
        assert "Consider upgrading your plan for higher rate limits" in suggestions

    def test_quota_error_suggestions(self):
        """Test recovery suggestions for quota errors."""
        error = SlugKitQuotaError("Daily limit exceeded")
        suggestions = get_error_recovery_suggestions(error)

        assert "Check your current usage against your plan limits" in suggestions
        assert "Consider upgrading your plan for higher quotas" in suggestions
        assert "Review and optimize your slug generation patterns" in suggestions

    def test_configuration_error_suggestions(self):
        """Test recovery suggestions for configuration errors."""
        error = SlugKitConfigurationError("Missing API key")
        suggestions = get_error_recovery_suggestions(error)

        assert "Verify your configuration settings" in suggestions
        assert "Check environment variables are set correctly" in suggestions
        assert "Review the configuration documentation" in suggestions

    def test_generic_error_suggestions(self):
        """Test that generic suggestions are always included."""
        error = SlugKitError("Unknown error")
        suggestions = get_error_recovery_suggestions(error)

        assert "Check the SlugKit documentation for troubleshooting" in suggestions
        assert "Review the error context for additional details" in suggestions
        assert "Enable debug logging for more information" in suggestions


class TestErrorCategorization:
    """Test the error categorization functionality."""

    def test_connection_error_categorization(self):
        """Test categorization of connection errors."""
        error = SlugKitConnectionError("Network timeout")
        category = categorize_error(error)

        assert category["type"] == "connectivity"
        assert category["severity"] == ErrorSeverity.MEDIUM
        assert category["retryable"] is True
        assert category["user_actionable"] is True

    def test_authentication_error_categorization(self):
        """Test categorization of authentication errors."""
        error = SlugKitAuthenticationError("Invalid API key")
        category = categorize_error(error)

        assert category["type"] == "authentication"
        assert category["severity"] == ErrorSeverity.HIGH
        assert category["retryable"] is False
        assert category["user_actionable"] is True

    def test_validation_error_categorization(self):
        """Test categorization of validation errors."""
        error = SlugKitValidationError("Invalid pattern")
        category = categorize_error(error)

        assert category["type"] == "validation"
        assert category["severity"] == ErrorSeverity.LOW
        assert category["retryable"] is False
        assert category["user_actionable"] is True

    def test_timeout_error_categorization(self):
        """Test categorization of timeout errors."""
        error = SlugKitTimeoutError("Operation timed out")
        category = categorize_error(error)

        assert category["type"] == "performance"
        assert category["severity"] == ErrorSeverity.MEDIUM
        assert category["retryable"] is True
        assert category["user_actionable"] is True

    def test_rate_limit_error_categorization(self):
        """Test categorization of rate limit errors."""
        error = SlugKitRateLimitError("Too many requests")
        category = categorize_error(error)

        assert category["type"] == "rate_limiting"
        assert category["severity"] == ErrorSeverity.MEDIUM
        assert category["retryable"] is True
        assert category["user_actionable"] is True

    def test_quota_error_categorization(self):
        """Test categorization of quota errors."""
        error = SlugKitQuotaError("Daily limit exceeded")
        category = categorize_error(error)

        assert category["type"] == "quota"
        assert category["severity"] == ErrorSeverity.HIGH
        assert category["retryable"] is False
        assert category["user_actionable"] is True

    def test_configuration_error_categorization(self):
        """Test categorization of configuration errors."""
        error = SlugKitConfigurationError("Missing setting")
        category = categorize_error(error)

        assert category["type"] == "configuration"
        assert category["severity"] == ErrorSeverity.HIGH
        assert category["retryable"] is False
        assert category["user_actionable"] is True

    def test_server_error_categorization(self):
        """Test categorization of server errors."""
        error = SlugKitServerError("Internal server error")
        category = categorize_error(error)

        assert category["type"] == "server"
        assert category["severity"] == ErrorSeverity.HIGH
        assert category["retryable"] is True
        assert category["user_actionable"] is False

    def test_unknown_error_categorization(self):
        """Test categorization of unknown errors."""
        error = Exception("Unknown error")
        category = categorize_error(error)

        assert category["type"] == "unknown"
        assert category["severity"] == ErrorSeverity.MEDIUM
        assert category["retryable"] is False
        assert category["user_actionable"] is False


class TestErrorSeverity:
    """Test the error severity constants."""

    def test_error_severity_constants(self):
        """Test that error severity constants are defined correctly."""
        assert ErrorSeverity.LOW == "low"
        assert ErrorSeverity.MEDIUM == "medium"
        assert ErrorSeverity.HIGH == "high"
        assert ErrorSeverity.CRITICAL == "critical"


class TestIntegrationWithRetryLogic:
    """Test integration between error handling and retry logic."""

    def test_retryable_errors_are_categorized_correctly(self):
        """Test that retryable errors are properly categorized."""
        # Test connection error (retryable)
        connect_error = SlugKitConnectionError("Network timeout")
        assert should_retry_error(connect_error) is True

        category = categorize_error(connect_error)
        assert category["retryable"] is True

        # Test authentication error (not retryable)
        auth_error = SlugKitAuthenticationError("Invalid API key")
        assert should_retry_error(auth_error) is False

        category = categorize_error(auth_error)
        assert category["retryable"] is False

    def test_error_context_in_retry_scenarios(self):
        """Test that error context is preserved during retry scenarios."""
        context = ErrorContext("test_operation", "/test/endpoint")
        error = SlugKitConnectionError("Network timeout", context=context)

        # Error should be retryable
        assert should_retry_error(error) is True

        # Context should be preserved
        assert error.context == context
        assert error.get_context_info()["operation"] == "test_operation"


if __name__ == "__main__":
    pytest.main([__file__])
