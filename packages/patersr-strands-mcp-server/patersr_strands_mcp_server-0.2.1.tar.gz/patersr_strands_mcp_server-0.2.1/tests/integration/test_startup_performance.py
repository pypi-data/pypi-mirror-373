"""Performance tests for startup time requirements."""

import asyncio
import pytest
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from strands_mcp.server import StrandsMCPServer
from strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from datetime import datetime, timezone


class TestStartupPerformance:
    """Test startup performance requirements."""
    
    @pytest.fixture
    def server_with_realistic_mocks(self):
        """Create a server with realistic mock timings."""
        with patch('strands_mcp.server.DocumentationService') as mock_doc_service, \
             patch('strands_mcp.server.DocumentIndexingService') as mock_index_service, \
             patch('strands_mcp.server.SearchService') as mock_search_service, \
             patch('strands_mcp.server.DocumentationToolRegistry'), \
             patch('strands_mcp.server.FastMCP'):
            
            server = StrandsMCPServer()
            
            # Setup mock services with realistic timing
            server._documentation_service = mock_doc_service.return_value
            server._indexing_service = mock_index_service.return_value
            server._search_service = mock_search_service.return_value
            
            return server
    
    @pytest.fixture
    def large_chunk_set(self):
        """Create a large set of document chunks for performance testing."""
        chunks = []
        for i in range(100):  # Simulate 100 documents
            chunk = DocumentChunk(
                id=f"test{i}",
                title=f"Test Document {i}",
                content=f"This is test content for document {i}. " * 50,  # ~2KB per chunk
                source_url=f"https://example.com/doc{i}",
                section=f"Section {i % 10}",
                file_path=f"/tmp/doc{i}.md",
                last_modified=datetime.now(timezone.utc)
            )
            chunks.append(chunk)
        return chunks
    
    @pytest.mark.asyncio
    async def test_startup_with_existing_index_under_5_seconds(self, server_with_realistic_mocks):
        """Test that startup with existing index completes under 5 seconds."""
        server = server_with_realistic_mocks
        
        # Mock index loading to simulate realistic timing (should be very fast)
        async def mock_load_index():
            await asyncio.sleep(0.1)  # Simulate 100ms to load index
            return True
        
        server._search_service.load_index = mock_load_index
        server._search_service.get_index_stats = MagicMock(return_value={
            'total_chunks': 100,
            'unique_documents': 50
        })
        
        start_time = time.time()
        await server._initialize_services_fast()
        end_time = time.time()
        
        startup_time = end_time - start_time
        assert startup_time < 5.0, f"Startup took {startup_time:.2f}s, should be under 5s"
        assert startup_time < 1.0, f"With existing index, startup should be under 1s, took {startup_time:.2f}s"
        assert server._services_initialized
    
    @pytest.mark.asyncio
    async def test_startup_with_user_cache_under_5_seconds(self, server_with_realistic_mocks, large_chunk_set):
        """Test that startup with user cache completes under 5 seconds."""
        server = server_with_realistic_mocks
        
        # Mock no existing index
        server._search_service.load_index = AsyncMock(return_value=False)
        
        # Mock cache hierarchy to return user cache
        async def mock_get_cached_docs():
            await asyncio.sleep(0.2)  # Simulate 200ms to load cache
            return large_chunk_set
        
        server._get_cached_docs_with_hierarchy = mock_get_cached_docs
        
        # Mock indexing to simulate realistic timing
        async def mock_index_documents(documents):
            await asyncio.sleep(2.0)  # Simulate 2s to build index from 100 docs
        
        server._indexing_service.index_documents = mock_index_documents
        server._search_service.load_index = AsyncMock(return_value=True)
        
        start_time = time.time()
        await server._initialize_services_fast()
        end_time = time.time()
        
        startup_time = end_time - start_time
        assert startup_time < 5.0, f"Startup took {startup_time:.2f}s, should be under 5s"
        assert server._services_initialized
    
    @pytest.mark.asyncio
    async def test_startup_timeout_prevents_long_delays(self, server_with_realistic_mocks):
        """Test that startup timeout prevents long initialization delays."""
        server = server_with_realistic_mocks
        
        # Mock very slow initialization
        async def slow_init():
            await asyncio.sleep(10)  # 10 seconds - too slow
        
        server._initialize_services_fast = slow_init
        
        start_time = time.time()
        await server._ensure_services_initialized()
        end_time = time.time()
        
        startup_time = end_time - start_time
        # Should timeout at 5 seconds and continue
        assert startup_time < 7.0, f"Startup took {startup_time:.2f}s, should timeout at 5s"
        assert server._services_initialized  # Should still be marked as initialized
    
    @pytest.mark.asyncio
    async def test_startup_with_bundled_cache_under_5_seconds(self, server_with_realistic_mocks, large_chunk_set):
        """Test that startup with bundled cache completes under 5 seconds."""
        server = server_with_realistic_mocks
        
        # Mock no existing index or user cache
        server._search_service.load_index = AsyncMock(return_value=False)
        
        # Mock cache hierarchy to use bundled cache
        async def mock_get_cached_docs():
            await asyncio.sleep(0.3)  # Simulate 300ms to load bundled cache
            return large_chunk_set
        
        server._get_cached_docs_with_hierarchy = mock_get_cached_docs
        
        # Mock indexing with realistic timing
        async def mock_index_documents(documents):
            await asyncio.sleep(1.5)  # Simulate 1.5s to build index
        
        server._indexing_service.index_documents = mock_index_documents
        server._search_service.load_index = AsyncMock(return_value=True)
        
        start_time = time.time()
        await server._initialize_services_fast()
        end_time = time.time()
        
        startup_time = end_time - start_time
        assert startup_time < 5.0, f"Startup took {startup_time:.2f}s, should be under 5s"
        assert server._services_initialized
    
    @pytest.mark.asyncio
    async def test_startup_with_no_cache_is_fast(self, server_with_realistic_mocks):
        """Test that startup with no cache is still fast (just marks as initialized)."""
        server = server_with_realistic_mocks
        
        # Mock no existing index or cache
        server._search_service.load_index = AsyncMock(return_value=False)
        server._get_cached_docs_with_hierarchy = AsyncMock(return_value=None)
        
        start_time = time.time()
        await server._initialize_services_fast()
        end_time = time.time()
        
        startup_time = end_time - start_time
        assert startup_time < 1.0, f"Startup with no cache took {startup_time:.2f}s, should be under 1s"
        assert server._services_initialized
    
    @pytest.mark.asyncio
    async def test_background_task_creation_is_fast(self, server_with_realistic_mocks):
        """Test that background task creation doesn't slow down startup."""
        server = server_with_realistic_mocks
        server._initialize_services_fast = AsyncMock()
        
        start_time = time.time()
        await server._ensure_services_initialized()
        end_time = time.time()
        
        startup_time = end_time - start_time
        assert startup_time < 1.0, f"Service initialization took {startup_time:.2f}s, should be under 1s"
        assert server._background_update_task is not None
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_performance(self, server_with_realistic_mocks, large_chunk_set):
        """Test that cache hierarchy checking is performant."""
        server = server_with_realistic_mocks
        
        # Mock user cache check (fast)
        server._documentation_service.get_cached_docs = AsyncMock(return_value=None)
        
        # Mock bundled cache check (should also be fast)
        async def mock_get_bundled_cache():
            await asyncio.sleep(0.1)  # Should be very fast
            return large_chunk_set
        
        server._get_bundled_cache = mock_get_bundled_cache
        
        start_time = time.time()
        result = await server._get_cached_docs_with_hierarchy()
        end_time = time.time()
        
        hierarchy_time = end_time - start_time
        assert hierarchy_time < 0.5, f"Cache hierarchy check took {hierarchy_time:.2f}s, should be under 0.5s"
        assert result == large_chunk_set
    
    @pytest.mark.asyncio
    async def test_concurrent_initialization_performance(self, server_with_realistic_mocks):
        """Test that concurrent initialization calls don't cause performance issues."""
        server = server_with_realistic_mocks
        
        # Mock fast initialization
        server._initialize_services_fast = AsyncMock()
        
        # Call initialization multiple times concurrently
        start_time = time.time()
        tasks = [
            server._ensure_services_initialized(),
            server._ensure_services_initialized(),
            server._ensure_services_initialized(),
            server._ensure_services_initialized(),
            server._ensure_services_initialized()
        ]
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        assert total_time < 2.0, f"Concurrent initialization took {total_time:.2f}s, should be under 2s"
        
        # Should initialize multiple times but complete quickly
        # (The current implementation doesn't prevent concurrent calls, which is fine)
        assert server._initialize_services_fast.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_memory_efficient_startup(self, server_with_realistic_mocks, large_chunk_set):
        """Test that startup doesn't load unnecessary data into memory."""
        server = server_with_realistic_mocks
        
        # Mock index loading (should not load full chunks into memory)
        server._search_service.load_index = AsyncMock(return_value=True)
        server._search_service.get_index_stats = MagicMock(return_value={
            'total_chunks': len(large_chunk_set),
            'unique_documents': 50
        })
        
        # Should not call cache loading methods when index exists
        server._get_cached_docs_with_hierarchy = AsyncMock()
        
        await server._initialize_services_fast()
        
        # Should not have loaded cache when index was available
        server._get_cached_docs_with_hierarchy.assert_not_called()
        assert server._services_initialized