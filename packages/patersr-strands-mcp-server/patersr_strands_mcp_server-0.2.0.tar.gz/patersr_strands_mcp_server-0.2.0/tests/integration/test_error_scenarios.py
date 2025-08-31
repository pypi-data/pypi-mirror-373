"""Integration tests for error handling scenarios."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.strands_mcp.server import StrandsMCPServer
from src.strands_mcp.services.documentation_service import DocumentationService
from src.strands_mcp.services.search_service import SearchService
from src.strands_mcp.utils.errors import NetworkError, SearchError, ServiceUnavailableError


class TestNetworkErrorScenarios:
    """Test network-related error scenarios."""
    
    @pytest.mark.asyncio
    async def test_github_api_timeout(self):
        """Test handling of GitHub API timeout."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Mock timeout error
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            
            doc_service = DocumentationService()
            
            with pytest.raises(NetworkError) as exc_info:
                await doc_service._fetch_github_contents()
            
            assert "GitHub API request failed" in str(exc_info.value)
            assert exc_info.value.error_code == "NETWORK_ERROR"
    
    @pytest.mark.asyncio
    async def test_github_api_rate_limit(self):
        """Test handling of GitHub API rate limiting."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Mock rate limit response
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limit exceeded",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.get.return_value = mock_response
            
            doc_service = DocumentationService()
            
            with pytest.raises(NetworkError) as exc_info:
                await doc_service._fetch_github_contents()
            
            assert exc_info.value.details.get("status_code") == 403
    
    @pytest.mark.asyncio
    async def test_network_connection_failure(self):
        """Test handling of network connection failure."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Mock connection error
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            
            doc_service = DocumentationService()
            
            with pytest.raises(NetworkError) as exc_info:
                await doc_service._fetch_github_contents()
            
            assert "GitHub API request failed" in str(exc_info.value)


class TestSearchErrorScenarios:
    """Test search-related error scenarios."""
    
    @pytest.mark.asyncio
    async def test_search_without_index(self):
        """Test search operation without loaded index."""
        search_service = SearchService()
        
        # Ensure no index is loaded
        search_service._document_index = None
        search_service._faiss_index = None
        
        from src.strands_mcp.models.documentation import SearchQuery
        query = SearchQuery(query="test", limit=5)
        
        with pytest.raises(SearchError) as exc_info:
            await search_service.semantic_search(query)
        
        assert exc_info.value.error_code == "SEARCH_ERROR"
        assert exc_info.value.details["index_status"] == "not_loaded"
    
    @pytest.mark.asyncio
    async def test_search_with_invalid_query(self):
        """Test search with invalid query parameters."""
        from src.strands_mcp.tools.documentation import SearchDocumentationTool
        from src.strands_mcp.utils.errors import ValidationError as CustomValidationError
        
        mock_search_service = MagicMock()
        tool = SearchDocumentationTool(mock_search_service)
        
        # Test with empty query
        with pytest.raises(CustomValidationError) as exc_info:
            await tool.execute({"query": "", "limit": 10})
        
        assert exc_info.value.error_code == "VALIDATION_ERROR"
    
    @pytest.mark.asyncio
    async def test_search_service_failure(self):
        """Test search service internal failure."""
        from src.strands_mcp.tools.documentation import SearchDocumentationTool
        
        mock_search_service = MagicMock()
        mock_search_service.semantic_search = AsyncMock(side_effect=Exception("Internal error"))
        
        tool = SearchDocumentationTool(mock_search_service)
        
        with pytest.raises(Exception):  # Should be wrapped in appropriate error
            await tool.execute({"query": "test", "limit": 10})


class TestServerErrorScenarios:
    """Test server-level error scenarios."""
    
    @pytest.mark.asyncio
    async def test_server_initialization_with_service_failures(self):
        """Test server initialization when services fail."""
        with patch('src.strands_mcp.server.DocumentationService') as mock_doc_service_class, \
             patch('src.strands_mcp.server.SearchService') as mock_search_service_class, \
             patch('src.strands_mcp.server.DocumentIndexingService') as mock_indexing_service_class:
            
            # Mock service initialization failures
            mock_doc_service = MagicMock()
            mock_doc_service.get_cache_info = AsyncMock(side_effect=Exception("Cache error"))
            mock_doc_service_class.return_value = mock_doc_service
            
            mock_search_service = MagicMock()
            mock_search_service.load_index = AsyncMock(return_value=False)
            mock_search_service_class.return_value = mock_search_service
            
            mock_indexing_service = MagicMock()
            mock_indexing_service_class.return_value = mock_indexing_service
            
            # Server should still initialize despite service failures
            server = StrandsMCPServer()
            
            # Services should be marked as initialized (graceful degradation)
            await server._ensure_services_initialized()
            assert server._services_initialized is True
    
    @pytest.mark.asyncio
    async def test_server_health_check_with_failures(self):
        """Test server health check when components fail."""
        with patch('src.strands_mcp.server.DocumentationService') as mock_doc_service_class:
            mock_doc_service = MagicMock()
            mock_doc_service.get_cache_info = AsyncMock(side_effect=Exception("Service error"))
            mock_doc_service_class.return_value = mock_doc_service
            
            server = StrandsMCPServer()
            
            # Health check should handle component failures gracefully
            health_result = await server._health_checker.check_documentation_service()
            
            assert health_result.status == "unhealthy"
            assert "health check failed" in health_result.message.lower()
    
    @pytest.mark.asyncio
    async def test_background_update_error_handling(self):
        """Test background update error handling."""
        with patch('src.strands_mcp.server.DocumentationService') as mock_doc_service_class:
            mock_doc_service = MagicMock()
            mock_doc_service.check_for_updates = AsyncMock(side_effect=Exception("Update error"))
            mock_doc_service_class.return_value = mock_doc_service
            
            server = StrandsMCPServer()
            server._services_initialized = True
            
            # Background update should handle errors gracefully
            await server._background_cache_update()
            
            # Server should still be running despite update failure
            assert server._running is False  # Not started in test, but no crash


class TestRecoveryScenarios:
    """Test error recovery scenarios."""
    
    @pytest.mark.asyncio
    async def test_service_recovery_after_failure(self):
        """Test service recovery after temporary failure."""
        call_count = 0
        
        async def mock_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Temporary failure")
            return {"success": True}
        
        from src.strands_mcp.utils.error_handler import retry_with_backoff
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def test_function():
            return await mock_operation()
        
        result = await test_function()
        assert result == {"success": True}
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after failures."""
        from src.strands_mcp.utils.error_handler import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)
        call_count = 0
        
        @breaker
        async def test_function(should_fail=True):
            nonlocal call_count
            call_count += 1
            if should_fail:
                raise Exception("Test failure")
            return "success"
        
        # Trigger failures to open circuit
        with pytest.raises(Exception):
            await test_function()
        with pytest.raises(Exception):
            await test_function()
        
        assert breaker.state == "OPEN"
        
        # Wait for recovery timeout
        await asyncio.sleep(0.02)
        
        # Should recover on successful call
        result = await test_function(should_fail=False)
        assert result == "success"
        assert breaker.state == "CLOSED"


class TestErrorPropagation:
    """Test error propagation through the system."""
    
    @pytest.mark.asyncio
    async def test_mcp_tool_error_propagation(self):
        """Test error propagation from services to MCP tools."""
        from src.strands_mcp.tools.documentation import SearchDocumentationTool
        from src.strands_mcp.utils.errors import SearchError
        
        mock_search_service = MagicMock()
        mock_search_service.semantic_search = AsyncMock(
            side_effect=SearchError("Search failed", query="test")
        )
        
        tool = SearchDocumentationTool(mock_search_service)
        
        with pytest.raises(SearchError) as exc_info:
            await tool.execute({"query": "test", "limit": 10})
        
        assert exc_info.value.error_code == "SEARCH_ERROR"
        assert exc_info.value.details["query"] == "test"
    
    @pytest.mark.asyncio
    async def test_server_error_handling_in_tools(self):
        """Test server-level error handling for tool execution."""
        with patch('src.strands_mcp.server.DocumentationService'), \
             patch('src.strands_mcp.server.SearchService') as mock_search_service_class, \
             patch('src.strands_mcp.server.DocumentIndexingService'):
            
            mock_search_service = MagicMock()
            mock_search_service.semantic_search = AsyncMock(side_effect=Exception("Service error"))
            mock_search_service_class.return_value = mock_search_service
            
            server = StrandsMCPServer()
            server._services_initialized = True
            
            # Tool execution should handle service errors gracefully
            with pytest.raises(Exception):  # Should be wrapped in StrandsMCPError
                await server.search_documentation("test query")
            
            # Error should be recorded
            assert server._error_count > 0
            assert server._last_error is not None


@pytest.mark.asyncio
async def test_comprehensive_error_logging():
    """Test that errors are logged with proper structure."""
    from src.strands_mcp.utils.error_handler import ErrorHandler
    from src.strands_mcp.utils.errors import NetworkError
    
    with patch('src.strands_mcp.utils.error_handler.logger') as mock_logger:
        error = NetworkError(
            message="Connection failed",
            url="https://api.github.com/test",
            status_code=500
        )
        
        ErrorHandler.log_error(
            error=error,
            operation="test_operation",
            component="test_component",
            extra_context={"request_id": "123"}
        )
        
        # Verify structured logging
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        # Check extra fields contain error details
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["operation"] == "test_operation"
        assert extra_fields["component"] == "test_component"
        assert extra_fields["error_code"] == "NETWORK_ERROR"
        assert extra_fields["request_id"] == "123"