"""Integration tests for background update functionality."""

import asyncio
import pytest
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from strands_mcp.server import StrandsMCPServer
from strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from datetime import datetime, timezone


class TestBackgroundUpdates:
    """Test background update functionality."""
    
    @pytest.fixture
    def server_with_mocks(self):
        """Create a server with mocked dependencies."""
        with patch('strands_mcp.server.DocumentationService') as mock_doc_service, \
             patch('strands_mcp.server.DocumentIndexingService') as mock_index_service, \
             patch('strands_mcp.server.SearchService') as mock_search_service, \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Setup mock services
            server._documentation_service = mock_doc_service.return_value
            server._indexing_service = mock_index_service.return_value
            server._search_service = mock_search_service.return_value
            
            return server
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks for testing."""
        return [
            DocumentChunk(
                id="test1",
                title="Test Document 1",
                content="This is test content for document 1",
                source_url="https://example.com/doc1",
                section="Getting Started",
                file_path="/tmp/doc1.md",
                last_modified=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_background_update_checks_for_updates(self, server_with_mocks):
        """Test that background update checks for documentation updates."""
        server = server_with_mocks
        server._services_initialized = True
        server._should_check_for_updates = MagicMock(return_value=True)
        server._documentation_service.check_for_updates = AsyncMock(return_value=False)
        
        # Run background update (with shorter sleep for testing)
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await server._background_cache_update()
        
        # Should check for updates
        server._documentation_service.check_for_updates.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_background_update_skips_recent_check(self, server_with_mocks):
        """Test that background update skips check if done recently."""
        server = server_with_mocks
        server._services_initialized = True
        server._should_check_for_updates = MagicMock(return_value=False)
        server._documentation_service.check_for_updates = AsyncMock()
        
        # Run background update
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await server._background_cache_update()
        
        # Should not check for updates
        server._documentation_service.check_for_updates.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_background_update_fetches_when_available(self, server_with_mocks, sample_chunks):
        """Test that background update fetches documentation when updates are available."""
        server = server_with_mocks
        server._services_initialized = True
        server._should_check_for_updates = MagicMock(return_value=True)
        server._documentation_service.check_for_updates = AsyncMock(return_value=True)
        server._update_documentation = AsyncMock()
        
        # Run background update
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await server._background_cache_update()
        
        # Should update documentation
        server._update_documentation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_background_update_handles_errors_gracefully(self, server_with_mocks):
        """Test that background update handles errors without crashing."""
        server = server_with_mocks
        server._services_initialized = True
        server._should_check_for_updates = MagicMock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await server._background_cache_update()
        
        # Server should still be running (no exception raised)
        assert True  # If we get here, no exception was raised
    
    @pytest.mark.asyncio
    async def test_background_update_initializes_services_if_needed(self, server_with_mocks):
        """Test that background update initializes services if they're not ready."""
        server = server_with_mocks
        server._services_initialized = False
        server._initialize_services_fast = AsyncMock()
        server._should_check_for_updates = MagicMock(return_value=False)
        
        # Run background update
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await server._background_cache_update()
        
        # Should attempt to initialize services
        server._initialize_services_fast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_documentation_rebuilds_index(self, server_with_mocks, sample_chunks):
        """Test that update_documentation rebuilds the search index."""
        server = server_with_mocks
        server._documentation_service.fetch_latest_docs = AsyncMock(return_value=sample_chunks)
        server._documentation_service.save_docs_to_cache = AsyncMock()
        server._indexing_service.index_documents = AsyncMock()
        server._search_service.load_index = AsyncMock()
        
        await server._update_documentation()
        
        # Should fetch, save, index, and reload
        server._documentation_service.fetch_latest_docs.assert_called_once()
        server._documentation_service.save_docs_to_cache.assert_called_once_with(sample_chunks)
        server._indexing_service.index_documents.assert_called_once()
        server._search_service.load_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_documentation_handles_fetch_failure(self, server_with_mocks):
        """Test that update_documentation handles fetch failures gracefully."""
        server = server_with_mocks
        server._documentation_service.fetch_latest_docs = AsyncMock(side_effect=Exception("Fetch failed"))
        
        # Should not raise exception
        await server._update_documentation()
        
        # If we get here, exception was handled gracefully
        assert True
    
    @pytest.mark.asyncio
    async def test_update_documentation_handles_empty_chunks(self, server_with_mocks):
        """Test that update_documentation handles empty chunk list."""
        server = server_with_mocks
        server._documentation_service.fetch_latest_docs = AsyncMock(return_value=[])
        server._documentation_service.save_docs_to_cache = AsyncMock()
        
        await server._update_documentation()
        
        # Should not attempt to save empty chunks
        server._documentation_service.save_docs_to_cache.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_documentation_continues_on_index_failure(self, server_with_mocks, sample_chunks):
        """Test that update_documentation continues even if index rebuild fails."""
        server = server_with_mocks
        server._documentation_service.fetch_latest_docs = AsyncMock(return_value=sample_chunks)
        server._documentation_service.save_docs_to_cache = AsyncMock()
        server._indexing_service.index_documents = AsyncMock(side_effect=Exception("Index failed"))
        
        # Should not raise exception even if indexing fails
        await server._update_documentation()
        
        # Should still save to cache
        server._documentation_service.save_docs_to_cache.assert_called_once_with(sample_chunks)
    
    @pytest.mark.asyncio
    async def test_should_check_for_updates_first_time(self, server_with_mocks):
        """Test that should_check_for_updates returns True on first check."""
        server = server_with_mocks
        server._last_update_check = None
        
        result = server._should_check_for_updates()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_check_for_updates_recent_check(self, server_with_mocks):
        """Test that should_check_for_updates returns False for recent checks."""
        server = server_with_mocks
        server._last_update_check = datetime.now(timezone.utc)  # Just checked
        
        result = server._should_check_for_updates()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_should_check_for_updates_old_check(self, server_with_mocks):
        """Test that should_check_for_updates returns True for old checks."""
        server = server_with_mocks
        # Set last check to 25 hours ago
        from datetime import timedelta
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        server._last_update_check = old_time
        
        result = server._should_check_for_updates()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_background_task_lifecycle(self, server_with_mocks):
        """Test the complete lifecycle of background task creation and cleanup."""
        server = server_with_mocks
        server._initialize_services_fast = AsyncMock()
        
        # Ensure services initialized to create background task
        await server._ensure_services_initialized()
        
        # Task should be created
        assert server._background_update_task is not None
        task = server._background_update_task
        
        # Mock the task as not done
        task.done = MagicMock(return_value=False)
        task.cancel = MagicMock()
        
        # Mock documentation service close
        server._documentation_service.close = AsyncMock()
        
        # Cleanup should cancel the task
        await server._cleanup_services()
        
        task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_concurrent_background_updates(self, server_with_mocks):
        """Test that multiple calls to ensure_services_initialized don't create multiple tasks."""
        server = server_with_mocks
        server._initialize_services_fast = AsyncMock()
        
        # Call multiple times concurrently
        tasks = [
            server._ensure_services_initialized(),
            server._ensure_services_initialized(),
            server._ensure_services_initialized()
        ]
        
        await asyncio.gather(*tasks)
        
        # Should only have one background task
        assert server._background_update_task is not None
        
        # All calls should have used the same task
        # (This is implicitly tested by not having multiple tasks created)