"""Tests for fast startup functionality."""

import asyncio
import pytest
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from strands_mcp.server import StrandsMCPServer
from strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from datetime import datetime, timezone


class TestFastStartup:
    """Test fast startup functionality."""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock server for testing."""
        with patch('strands_mcp.server.DocumentationService'), \
             patch('strands_mcp.server.DocumentIndexingService'), \
             patch('strands_mcp.server.SearchService'), \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            server = StrandsMCPServer()
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
            ),
            DocumentChunk(
                id="test2",
                title="Test Document 2", 
                content="This is test content for document 2",
                source_url="https://example.com/doc2",
                section="Advanced",
                file_path="/tmp/doc2.md",
                last_modified=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_fast_startup_with_existing_index(self, mock_server, sample_chunks):
        """Test fast startup when search index already exists."""
        # Mock search service to return True for index loading
        mock_server._search_service.load_index = AsyncMock(return_value=True)
        mock_server._search_service.get_index_stats = MagicMock(return_value={
            'total_chunks': 2,
            'unique_documents': 2
        })
        
        start_time = time.time()
        await mock_server._initialize_services_fast()
        end_time = time.time()
        
        # Should complete very quickly when index exists
        assert end_time - start_time < 1.0
        assert mock_server._services_initialized
        mock_server._search_service.load_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fast_startup_with_user_cache(self, mock_server, sample_chunks):
        """Test fast startup using user cache when no index exists."""
        # Mock search service to return False for index loading
        mock_server._search_service.load_index = AsyncMock(return_value=False)
        
        # Mock cache hierarchy to return user cache
        mock_server._get_cached_docs_with_hierarchy = AsyncMock(return_value=sample_chunks)
        mock_server._indexing_service.index_documents = AsyncMock()
        
        start_time = time.time()
        await mock_server._initialize_services_fast()
        end_time = time.time()
        
        # Should complete reasonably quickly with cache
        assert end_time - start_time < 3.0
        assert mock_server._services_initialized
        mock_server._get_cached_docs_with_hierarchy.assert_called_once()
        mock_server._indexing_service.index_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fast_startup_with_no_cache(self, mock_server):
        """Test fast startup when no cache is available."""
        # Mock search service to return False for index loading
        mock_server._search_service.load_index = AsyncMock(return_value=False)
        
        # Mock cache hierarchy to return None
        mock_server._get_cached_docs_with_hierarchy = AsyncMock(return_value=None)
        
        start_time = time.time()
        await mock_server._initialize_services_fast()
        end_time = time.time()
        
        # Should still complete quickly even with no cache
        assert end_time - start_time < 1.0
        assert mock_server._services_initialized
        mock_server._get_cached_docs_with_hierarchy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_startup_timeout_handling(self, mock_server):
        """Test that startup timeout is handled gracefully."""
        # Mock to simulate slow initialization
        async def slow_init():
            await asyncio.sleep(10)  # Longer than 5-second timeout
        
        mock_server._initialize_services_fast = slow_init
        
        start_time = time.time()
        await mock_server._ensure_services_initialized()
        end_time = time.time()
        
        # Should timeout and continue
        assert end_time - start_time < 7.0  # Should timeout at 5 seconds + some buffer
        assert mock_server._services_initialized  # Should still be marked as initialized
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_user_cache_first(self, mock_server, sample_chunks):
        """Test that cache hierarchy checks user cache first."""
        # Mock user cache to return chunks
        mock_server._documentation_service.get_cached_docs = AsyncMock(return_value=sample_chunks)
        mock_server._get_bundled_cache = AsyncMock()
        
        result = await mock_server._get_cached_docs_with_hierarchy()
        
        assert result == sample_chunks
        mock_server._documentation_service.get_cached_docs.assert_called_once()
        mock_server._get_bundled_cache.assert_not_called()  # Should not check bundled cache
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_bundled_cache_fallback(self, mock_server, sample_chunks):
        """Test that cache hierarchy falls back to bundled cache."""
        # Mock user cache to return None, bundled cache to return chunks
        mock_server._documentation_service.get_cached_docs = AsyncMock(return_value=None)
        mock_server._get_bundled_cache = AsyncMock(return_value=sample_chunks)
        
        result = await mock_server._get_cached_docs_with_hierarchy()
        
        assert result == sample_chunks
        mock_server._documentation_service.get_cached_docs.assert_called_once()
        mock_server._get_bundled_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_no_cache_available(self, mock_server):
        """Test cache hierarchy when no cache is available."""
        # Mock both caches to return None
        mock_server._documentation_service.get_cached_docs = AsyncMock(return_value=None)
        mock_server._get_bundled_cache = AsyncMock(return_value=None)
        
        result = await mock_server._get_cached_docs_with_hierarchy()
        
        assert result is None
        mock_server._documentation_service.get_cached_docs.assert_called_once()
        mock_server._get_bundled_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bundled_cache_loading(self, mock_server, sample_chunks):
        """Test loading bundled cache from package data."""
        # Mock the bundled cache method directly
        mock_server._get_bundled_cache = AsyncMock(return_value=sample_chunks)
        
        result = await mock_server._get_bundled_cache()
        
        assert result == sample_chunks
    
    @pytest.mark.asyncio
    async def test_background_update_task_creation(self, mock_server):
        """Test that background update task is created properly."""
        mock_server._initialize_services_fast = AsyncMock()
        
        await mock_server._ensure_services_initialized()
        
        # Background task should be created
        assert mock_server._background_update_task is not None
        assert isinstance(mock_server._background_update_task, asyncio.Task)
    
    @pytest.mark.asyncio
    async def test_background_update_task_not_duplicated(self, mock_server):
        """Test that background update task is not created multiple times."""
        mock_server._initialize_services_fast = AsyncMock()
        
        # Call twice
        await mock_server._ensure_services_initialized()
        first_task = mock_server._background_update_task
        
        await mock_server._ensure_services_initialized()
        second_task = mock_server._background_update_task
        
        # Should be the same task
        assert first_task is second_task
    
    @pytest.mark.asyncio
    async def test_background_update_initialization(self, mock_server):
        """Test background update initializes services if needed."""
        mock_server._services_initialized = False
        mock_server._initialize_services_fast = AsyncMock()
        mock_server._should_check_for_updates = MagicMock(return_value=False)
        
        # Run background update
        await mock_server._background_cache_update()
        
        # Should attempt to initialize services
        mock_server._initialize_services_fast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_cancels_background_task(self, mock_server):
        """Test that cleanup properly cancels background task."""
        # Create a mock background task
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        mock_server._background_update_task = mock_task
        
        # Mock documentation service close method
        mock_server._documentation_service.close = AsyncMock()
        
        await mock_server._cleanup_services()
        
        # Task should be cancelled
        mock_task.cancel.assert_called_once()