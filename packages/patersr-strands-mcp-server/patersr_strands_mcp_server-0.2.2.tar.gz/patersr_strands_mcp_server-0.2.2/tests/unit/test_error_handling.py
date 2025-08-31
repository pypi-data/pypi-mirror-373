"""Tests for error handling utilities."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from pydantic import ValidationError

from src.strands_mcp.utils.errors import (
    StrandsMCPError,
    NetworkError,
    SearchError,
    IndexingError,
    CacheError,
    ValidationError as CustomValidationError,
    ServiceUnavailableError,
    ConfigurationError
)
from src.strands_mcp.utils.error_handler import (
    ErrorHandler,
    handle_errors,
    handle_sync_errors,
    CircuitBreaker,
    retry_with_backoff
)


class TestCustomErrors:
    """Test custom error classes."""
    
    def test_strands_mcp_error_basic(self):
        """Test basic StrandsMCPError functionality."""
        error = StrandsMCPError(
            message="Test error",
            error_code="TEST_ERROR",
            user_message="User friendly message"
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.user_message == "User friendly message"
        assert error.details == {}
        
        error_dict = error.to_dict()
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["user_message"] == "User friendly message"
    
    def test_network_error(self):
        """Test NetworkError with specific details."""
        error = NetworkError(
            message="Connection failed",
            url="https://api.github.com/test",
            status_code=500,
            retry_count=3
        )
        
        assert error.error_code == "NETWORK_ERROR"
        assert error.details["url"] == "https://api.github.com/test"
        assert error.details["status_code"] == 500
        assert error.details["retry_count"] == 3
        assert "server returned error 500" in error.user_message.lower()
    
    def test_network_error_no_status_code(self):
        """Test NetworkError without status code."""
        error = NetworkError(
            message="Connection failed",
            url="https://api.github.com/test"
        )
        
        assert error.error_code == "NETWORK_ERROR"
        assert "network connection failed" in error.user_message.lower()
    
    def test_search_error(self):
        """Test SearchError with query context."""
        error = SearchError(
            message="Search failed",
            query="test query",
            index_status="not_loaded"
        )
        
        assert error.error_code == "SEARCH_ERROR"
        assert error.details["query"] == "test query"
        assert error.details["index_status"] == "not_loaded"
        assert "search index is not available" in error.user_message.lower()
    
    def test_validation_error(self):
        """Test ValidationError with field context."""
        error = CustomValidationError(
            message="Invalid value",
            field="query",
            value="",
        )
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details["field"] == "query"
        assert error.details["value"] == ""
        assert "invalid value for query" in error.user_message.lower()


class TestErrorHandler:
    """Test ErrorHandler utility functions."""
    
    def test_create_user_friendly_error_custom(self):
        """Test user-friendly error creation for custom errors."""
        error = SearchError(
            message="Search failed",
            query="test",
            index_status="not_loaded"
        )
        
        result = ErrorHandler.create_user_friendly_error(error)
        
        assert result["error"] == "SEARCH_ERROR"
        assert "search index is not available" in result["message"].lower()
        assert result["details"]["query"] == "test"
    
    def test_create_user_friendly_error_httpx(self):
        """Test user-friendly error creation for httpx errors."""
        # Mock httpx.HTTPStatusError
        mock_request = MagicMock()
        mock_request.url = "https://api.github.com/test"
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        error = httpx.HTTPStatusError(
            message="Not found",
            request=mock_request,
            response=mock_response
        )
        
        result = ErrorHandler.create_user_friendly_error(error)
        
        assert result["error"] == "NETWORK_ERROR"
        assert "404" in result["message"]
        assert result["details"]["status_code"] == 404
    
    def test_create_user_friendly_error_timeout(self):
        """Test user-friendly error creation for timeout errors."""
        error = asyncio.TimeoutError()
        
        result = ErrorHandler.create_user_friendly_error(error)
        
        assert result["error"] == "TIMEOUT_ERROR"
        assert "timed out" in result["message"].lower()
    
    def test_classify_error_validation(self):
        """Test error classification for validation errors."""
        # Mock pydantic ValidationError
        mock_validation_error = MagicMock(spec=ValidationError)
        mock_validation_error.errors.return_value = [{"field": "query", "message": "required"}]
        
        result = ErrorHandler.classify_error(mock_validation_error)
        
        assert isinstance(result, CustomValidationError)
        assert result.error_code == "VALIDATION_ERROR"
    
    def test_classify_error_httpx(self):
        """Test error classification for httpx errors."""
        mock_request = MagicMock()
        mock_request.url = "https://api.github.com/test"
        
        error = httpx.RequestError(message="Connection failed", request=mock_request)
        
        result = ErrorHandler.classify_error(error)
        
        assert isinstance(result, NetworkError)
        assert result.error_code == "NETWORK_ERROR"
    
    def test_classify_error_generic(self):
        """Test error classification for generic errors."""
        error = ValueError("Invalid value")
        
        result = ErrorHandler.classify_error(error)
        
        assert isinstance(result, StrandsMCPError)
        assert result.error_code == "INTERNAL_ERROR"


class TestErrorDecorators:
    """Test error handling decorators."""
    
    @pytest.mark.asyncio
    async def test_handle_errors_success(self):
        """Test handle_errors decorator with successful operation."""
        
        @handle_errors("test_operation", "test_component")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_handle_errors_with_exception(self):
        """Test handle_errors decorator with exception."""
        
        @handle_errors("test_operation", "test_component")
        async def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(StrandsMCPError) as exc_info:
            await test_function()
        
        assert exc_info.value.error_code == "INTERNAL_ERROR"
    
    @pytest.mark.asyncio
    async def test_handle_errors_no_reraise(self):
        """Test handle_errors decorator without reraising."""
        
        @handle_errors("test_operation", "test_component", reraise=False, default_return="default")
        async def test_function():
            raise ValueError("Test error")
        
        result = await test_function()
        assert result == "default"
    
    def test_handle_sync_errors(self):
        """Test handle_sync_errors decorator."""
        
        @handle_sync_errors("test_operation", "test_component", reraise=False, default_return="default")
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result == "default"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self):
        """Test retry decorator with successful operation."""
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_eventual_success(self):
        """Test retry decorator with eventual success."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_all_failures(self):
        """Test retry decorator with all attempts failing."""
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def test_function():
            raise ValueError("Persistent error")
        
        with pytest.raises(ValueError, match="Persistent error"):
            await test_function()


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        @breaker
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert breaker.state == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        @breaker
        async def test_function():
            raise ValueError("Test error")
        
        # First failure
        with pytest.raises(ValueError):
            await test_function()
        assert breaker.state == "CLOSED"
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            await test_function()
        assert breaker.state == "OPEN"
        
        # Third call should raise ServiceUnavailableError
        with pytest.raises(ServiceUnavailableError):
            await test_function()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        
        @breaker
        async def test_function(should_fail=True):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # Trigger failure to open circuit
        with pytest.raises(ValueError):
            await test_function()
        assert breaker.state == "OPEN"
        
        # Wait for recovery timeout
        await asyncio.sleep(0.02)
        
        # Should transition to HALF_OPEN and succeed
        result = await test_function(should_fail=False)
        assert result == "success"
        assert breaker.state == "CLOSED"


@pytest.mark.asyncio
async def test_error_logging_with_context():
    """Test error logging with structured context."""
    with patch('src.strands_mcp.utils.error_handler.logger') as mock_logger:
        error = ValueError("Test error")
        
        ErrorHandler.log_error(
            error=error,
            operation="test_operation",
            component="test_component",
            extra_context={"key": "value"}
        )
        
        # Verify logger.error was called with correct parameters
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        # Check the error message
        assert "test_component.test_operation" in call_args[0][0]
        
        # Check extra fields
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["operation"] == "test_operation"
        assert extra_fields["component"] == "test_component"
        assert extra_fields["error_type"] == "ValueError"
        assert extra_fields["key"] == "value"