"""Error handling utilities for the Strands MCP server."""

import asyncio
import functools
import logging
import time
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar, Union

import httpx
from pydantic import ValidationError

from .errors import (
    CacheError,
    ConfigurationError,
    IndexingError,
    NetworkError,
    SearchError,
    ServiceUnavailableError,
    StrandsMCPError,
    ValidationError as CustomValidationError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorHandler:
    """Centralized error handling for the MCP server."""
    
    @staticmethod
    def log_error(
        error: Exception,
        operation: str,
        component: str,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an error with structured context.
        
        Args:
            error: The exception that occurred
            operation: The operation being performed when the error occurred
            component: The component where the error occurred
            extra_context: Additional context for debugging
        """
        context = {
            "operation": operation,
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if extra_context:
            context.update(extra_context)
        
        # Add structured error details if it's a custom error
        if isinstance(error, StrandsMCPError):
            context.update(error.to_dict())
        
        logger.error(
            f"Error in {component}.{operation}: {error}",
            extra={"extra_fields": context},
            exc_info=True
        )
    
    @staticmethod
    def create_user_friendly_error(error: Exception) -> Dict[str, Any]:
        """Create a user-friendly error response for MCP clients.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Dictionary with user-friendly error information
        """
        if isinstance(error, StrandsMCPError):
            return {
                "error": error.error_code,
                "message": error.user_message,
                "details": error.details
            }
        elif isinstance(error, ValidationError):
            return {
                "error": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "details": {"validation_errors": error.errors()}
            }
        elif isinstance(error, httpx.RequestError):
            return {
                "error": "NETWORK_ERROR",
                "message": "Network connection failed. Please check your internet connection and try again.",
                "details": {"url": str(getattr(error, 'request', {}).get('url', 'unknown'))}
            }
        elif isinstance(error, httpx.HTTPStatusError):
            return {
                "error": "NETWORK_ERROR",
                "message": f"Server returned error {error.response.status_code}. Please try again later.",
                "details": {"status_code": error.response.status_code, "url": str(error.request.url)}
            }
        elif isinstance(error, asyncio.TimeoutError):
            return {
                "error": "TIMEOUT_ERROR",
                "message": "Operation timed out. Please try again.",
                "details": {}
            }
        else:
            return {
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {"error_type": type(error).__name__}
            }
    
    @staticmethod
    def classify_error(error: Exception) -> StrandsMCPError:
        """Classify a generic exception into a specific error type.
        
        Args:
            error: The exception to classify
            
        Returns:
            Classified StrandsMCPError
        """
        if isinstance(error, StrandsMCPError):
            return error
        elif isinstance(error, ValidationError):
            return CustomValidationError(
                message=f"Validation failed: {error}",
                details={"validation_errors": error.errors()}
            )
        elif isinstance(error, (httpx.RequestError, httpx.HTTPStatusError)):
            status_code = getattr(error, 'response', {}).get('status_code')
            url = str(getattr(error, 'request', {}).get('url', 'unknown'))
            return NetworkError(
                message=f"Network error: {error}",
                url=url,
                status_code=status_code
            )
        elif isinstance(error, asyncio.TimeoutError):
            return ServiceUnavailableError(
                message="Operation timed out",
                retry_after=30
            )
        elif isinstance(error, FileNotFoundError):
            return CacheError(
                message=f"File not found: {error}",
                operation="file_access"
            )
        elif isinstance(error, PermissionError):
            return ConfigurationError(
                message=f"Permission denied: {error}"
            )
        else:
            return StrandsMCPError(
                message=f"Unexpected error: {error}",
                error_code="INTERNAL_ERROR"
            )


def handle_errors(
    operation: str,
    component: str,
    reraise: bool = True,
    default_return: Any = None
):
    """Decorator for handling errors in async functions.
    
    Args:
        operation: Name of the operation being performed
        component: Name of the component where the operation occurs
        reraise: Whether to reraise the exception after logging
        default_return: Default value to return if error occurs and reraise=False
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log successful operations for monitoring
                logger.info(
                    f"Completed {component}.{operation}",
                    extra={
                        "extra_fields": {
                            "operation": operation,
                            "component": component,
                            "duration_ms": duration_ms,
                            "success": True
                        }
                    }
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log the error with context
                ErrorHandler.log_error(
                    error=e,
                    operation=operation,
                    component=component,
                    extra_context={
                        "duration_ms": duration_ms,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                )
                
                if reraise:
                    # Classify and reraise as appropriate error type
                    classified_error = ErrorHandler.classify_error(e)
                    raise classified_error
                else:
                    return default_return
        
        return wrapper
    return decorator


def handle_sync_errors(
    operation: str,
    component: str,
    reraise: bool = True,
    default_return: Any = None
):
    """Decorator for handling errors in synchronous functions.
    
    Args:
        operation: Name of the operation being performed
        component: Name of the component where the operation occurs
        reraise: Whether to reraise the exception after logging
        default_return: Default value to return if error occurs and reraise=False
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log successful operations for monitoring
                logger.info(
                    f"Completed {component}.{operation}",
                    extra={
                        "extra_fields": {
                            "operation": operation,
                            "component": component,
                            "duration_ms": duration_ms,
                            "success": True
                        }
                    }
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log the error with context
                ErrorHandler.log_error(
                    error=e,
                    operation=operation,
                    component=component,
                    extra_context={
                        "duration_ms": duration_ms,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                )
                
                if reraise:
                    # Classify and reraise as appropriate error type
                    classified_error = ErrorHandler.classify_error(e)
                    raise classified_error
                else:
                    return default_return
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for handling repeated failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that triggers the circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time < self.recovery_timeout:
                    raise ServiceUnavailableError(
                        message="Service circuit breaker is open",
                        service=func.__name__,
                        retry_after=self.recovery_timeout
                    )
                else:
                    self.state = "HALF_OPEN"
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures",
                extra={
                    "extra_fields": {
                        "component": "circuit_breaker",
                        "failure_count": self.failure_count,
                        "state": self.state
                    }
                }
            )


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}",
                            extra={
                                "extra_fields": {
                                    "operation": func.__name__,
                                    "attempt": attempt + 1,
                                    "max_retries": max_retries,
                                    "error": str(e)
                                }
                            }
                        )
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.1f}s",
                        extra={
                            "extra_fields": {
                                "operation": func.__name__,
                                "attempt": attempt + 1,
                                "delay_seconds": delay,
                                "error": str(e)
                            }
                        }
                    )
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator