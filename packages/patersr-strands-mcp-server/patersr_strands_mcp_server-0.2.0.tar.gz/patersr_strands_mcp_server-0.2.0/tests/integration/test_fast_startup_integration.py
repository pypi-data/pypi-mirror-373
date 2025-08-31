"""Integration test for fast startup functionality."""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from strands_mcp.server import StrandsMCPServer


class TestFastStartupIntegration:
    """Integration tests for fast startup functionality."""
    
    @pytest.mark.asyncio
    async def test_server_initialization_performance(self):
        """Test that server initialization meets performance requirements."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Mock fast index loading
            server._search_service.load_index = AsyncMock(return_value=True)
            server._search_service.get_index_stats = MagicMock(return_value={
                'total_chunks': 50,
                'unique_documents': 25
            })
            
            start_time = time.time()
            await server._ensure_services_initialized()
            end_time = time.time()
            
            initialization_time = end_time - start_time
            
            # Should meet the 5-second requirement
            assert initialization_time < 5.0, f"Initialization took {initialization_time:.2f}s, should be under 5s"
            assert server._services_initialized
            assert server._background_update_task is not None
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_fallback_behavior(self):
        """Test that cache hierarchy works correctly."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Mock no existing index
            server._search_service.load_index = AsyncMock(return_value=False)
            
            # Mock user cache not available
            server._documentation_service.get_cached_docs = AsyncMock(return_value=None)
            
            # Mock bundled cache available
            server._get_bundled_cache = AsyncMock(return_value=[])
            
            # Mock indexing
            server._indexing_service.index_documents = AsyncMock()
            
            await server._ensure_services_initialized()
            
            # Should have checked user cache first, then bundled cache
            server._documentation_service.get_cached_docs.assert_called_once()
            server._get_bundled_cache.assert_called_once()
            assert server._services_initialized
    
    @pytest.mark.asyncio
    async def test_background_update_task_lifecycle(self):
        """Test the complete lifecycle of background update task."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Mock fast initialization
            server._initialize_services_fast = AsyncMock()
            
            # Initialize services
            await server._ensure_services_initialized()
            
            # Background task should be created
            assert server._background_update_task is not None
            background_task = server._background_update_task
            
            # Mock cleanup
            server._documentation_service.close = AsyncMock()
            
            # Cleanup should handle the background task
            await server._cleanup_services()
            
            # Task should be cancelled (if it was still running)
            # Note: In real scenarios, the task might complete before cleanup
    
    @pytest.mark.asyncio
    async def test_error_handling_during_startup(self):
        """Test that startup errors are handled gracefully."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Mock initialization failure
            server._initialize_services_fast = AsyncMock(side_effect=Exception("Test error"))
            
            # Should not raise exception
            await server._ensure_services_initialized()
            
            # Should still be marked as initialized (graceful degradation)
            assert server._services_initialized
            
            # Background task should still be created
            assert server._background_update_task is not None
    
    @pytest.mark.asyncio
    async def test_timeout_handling_during_startup(self):
        """Test that startup timeout is handled correctly."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Mock slow initialization (longer than 5-second timeout)
            async def slow_init():
                await asyncio.sleep(10)
            
            server._initialize_services_fast = slow_init
            
            start_time = time.time()
            await server._ensure_services_initialized()
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Should timeout and continue
            assert total_time < 7.0, f"Startup took {total_time:.2f}s, should timeout at 5s"
            assert server._services_initialized
            assert server._background_update_task is not None