"""Custom error classes for the Strands MCP server."""

from typing import Any, Dict, Optional


class StrandsMCPError(Exception):
    """Base exception class for Strands MCP server errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """Initialize the error.
        
        Args:
            message: Technical error message for logging
            error_code: Unique error code for categorization
            details: Additional error details for debugging
            user_message: User-friendly error message for MCP responses
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "details": self.details
        }


class NetworkError(StrandsMCPError):
    """Error related to network operations."""
    
    def __init__(
        self, 
        message: str, 
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        retry_count: int = 0,
        **kwargs
    ):
        details = {
            "url": url,
            "status_code": status_code,
            "retry_count": retry_count
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Network connection failed. Please check your internet connection and try again."
        if status_code:
            user_message = f"Server returned error {status_code}. Please try again later."
        
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            details=details,
            user_message=user_message
        )


class SearchError(StrandsMCPError):
    """Error related to search operations."""
    
    def __init__(
        self, 
        message: str, 
        query: Optional[str] = None,
        index_status: Optional[str] = None,
        **kwargs
    ):
        details = {
            "query": query,
            "index_status": index_status
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Search operation failed. Please try a different query or try again later."
        if index_status == "not_loaded":
            user_message = "Search index is not available. Please wait for the system to initialize."
        
        super().__init__(
            message=message,
            error_code="SEARCH_ERROR",
            details=details,
            user_message=user_message
        )


class IndexingError(StrandsMCPError):
    """Error related to document indexing operations."""
    
    def __init__(
        self, 
        message: str, 
        document_count: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "document_count": document_count,
            "operation": operation
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Document indexing failed. The system will continue with existing data."
        
        super().__init__(
            message=message,
            error_code="INDEXING_ERROR",
            details=details,
            user_message=user_message
        )


class CacheError(StrandsMCPError):
    """Error related to cache operations."""
    
    def __init__(
        self, 
        message: str, 
        cache_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "cache_type": cache_type,
            "operation": operation
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Cache operation failed. The system will attempt to fetch fresh data."
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details,
            user_message=user_message
        )


class ValidationError(StrandsMCPError):
    """Error related to input validation."""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = {
            "field": field,
            "value": str(value) if value is not None else None
        }
        details.update(kwargs.get("details", {}))
        
        user_message = f"Invalid input: {message}"
        if field:
            user_message = f"Invalid value for {field}: {message}"
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            user_message=user_message
        )


class ServiceUnavailableError(StrandsMCPError):
    """Error when a service is temporarily unavailable."""
    
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = {
            "service": service,
            "retry_after_seconds": retry_after
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Service is temporarily unavailable. Please try again in a few moments."
        if retry_after:
            user_message = f"Service is temporarily unavailable. Please try again in {retry_after} seconds."
        
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
            user_message=user_message
        )


class ConfigurationError(StrandsMCPError):
    """Error related to configuration issues."""
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = {
            "config_key": config_key
        }
        details.update(kwargs.get("details", {}))
        
        user_message = "Configuration error. Please check your setup and try again."
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            user_message=user_message
        )