"""Integration tests for server functionality."""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from strands_mcp.server import StrandsMCPServer
from strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from datetime import datetime, timezone


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        cache_dir = temp_path / "cache"
        index_dir = temp_path / "indexes"
        
        cache_dir.mkdir()
        index_dir.mkdir()
        
        yield {
            "cache_dir": str(cache_dir),
            "index_dir": str(index_dir)
        }


@pytest.fixture
def sample_documentation():
    """Sample documentation chunks for testing."""
    return [
        DocumentChunk(
            id="strands-agents/docs:getting-started.md",
            title="Getting Started with Strands",
            content="# Getting Started with Strands\n\nThis guide will help you get started with the Strands Agent SDK.",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            section="Getting Started",
            file_path="/tmp/getting-started.md",
            last_modified=datetime.now(timezone.utc)
        )
    ]


class TestServerIntegration:
    """Test server integration functionality."""
    
    def test_server_creation(self):
        """Test that server can be created successfully."""
        server = StrandsMCPServer()
        
        assert server is not None
        assert not server.is_running
        assert not server.services_initialized
        assert server._mcp_server is not None
        assert server._documentation_service is not None
        assert server._search_service is not None
        assert server._indexing_service is not None
    
    def test_server_info(self):
        """Test server info is properly configured."""
        server = StrandsMCPServer()
        
        server_info = server._mcp_server.server_info
        assert server_info["name"] == "strands-mcp-server"
        assert server_info["version"] == "0.1.0"
        assert "documentation search" in server_info["description"]
    
    @pytest.mark.asyncio
    async def test_service_initialization_with_mocked_services(self, temp_dirs, sample_documentation):
        """Test service initialization with mocked external dependencies."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            # Mock all external dependencies
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                with patch.object(StrandsMCPServer, '_indexing_service') as mock_indexing_service:
                    with patch.object(StrandsMCPServer, '_search_service') as mock_search_service:
                        
                        # Setup mocks
                        mock_doc_service = AsyncMock()
                        mock_doc_service_class.return_value = mock_doc_service
                        mock_doc_service.check_for_updates.return_value = False
                        mock_doc_service.get_cached_docs.return_value = sample_documentation
                        mock_doc_service.close = AsyncMock()
                        
                        mock_indexing_service.index_documents = AsyncMock()
                        mock_search_service.load_index = AsyncMock(return_value=True)
                        
                        # Create server
                        server = StrandsMCPServer()
                        server._indexing_service = mock_indexing_service
                        server._search_service = mock_search_service
                        
                        # Initialize services
                        await server._initialize_services()
                        
                        # Verify initialization
                        assert server.services_initialized
                        mock_search_service.load_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_check_mechanism(self, temp_dirs, sample_documentation):
        """Test the update check mechanism."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                # First call should check for updates
                mock_doc_service.check_for_updates.return_value = True
                mock_doc_service.fetch_latest_docs.return_value = sample_documentation
                mock_doc_service.save_docs_to_cache = AsyncMock()
                mock_doc_service.close = AsyncMock()
                
                server = StrandsMCPServer()
                
                # Mock other services
                with patch.object(server, '_indexing_service') as mock_indexing_service:
                    with patch.object(server, '_search_service') as mock_search_service:
                        mock_indexing_service.index_documents = AsyncMock()
                        mock_search_service.load_index = AsyncMock(return_value=True)
                        
                        # First initialization should check for updates
                        await server._initialize_services()
                        
                        # Verify update check was called
                        mock_doc_service.check_for_updates.assert_called_once()
                        mock_doc_service.fetch_latest_docs.assert_called_once()
                        mock_doc_service.save_docs_to_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_during_initialization(self, temp_dirs):
        """Test error handling during service initialization."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                # Mock a failure during documentation check
                mock_doc_service.check_for_updates.side_effect = Exception("Network error")
                mock_doc_service.close = AsyncMock()
                
                server = StrandsMCPServer()
                
                # Initialize services - should handle error gracefully
                await server._initialize_services()
                
                # Server should still be created but services not fully initialized
                assert not server.services_initialized
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, temp_dirs):
        """Test service cleanup functionality."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                mock_doc_service.close = AsyncMock()
                
                server = StrandsMCPServer()
                
                # Test cleanup
                await server.stop()
                
                # Verify cleanup was attempted
                assert not server.is_running
    
    @pytest.mark.asyncio
    async def test_ensure_services_initialized_idempotent(self, temp_dirs, sample_documentation):
        """Test that ensure_services_initialized is idempotent."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                mock_doc_service.check_for_updates.return_value = False
                mock_doc_service.get_cached_docs.return_value = sample_documentation
                mock_doc_service.close = AsyncMock()
                
                server = StrandsMCPServer()
                
                # Mock other services
                with patch.object(server, '_indexing_service') as mock_indexing_service:
                    with patch.object(server, '_search_service') as mock_search_service:
                        mock_indexing_service.index_documents = AsyncMock()
                        mock_search_service.load_index = AsyncMock(return_value=True)
                        
                        # Call multiple times
                        await server._ensure_services_initialized()
                        await server._ensure_services_initialized()
                        await server._ensure_services_initialized()
                        
                        # Should only initialize once
                        assert server.services_initialized
                        assert mock_doc_service.check_for_updates.call_count == 1
    
    def test_daily_update_check_logic(self):
        """Test the daily update check logic."""
        server = StrandsMCPServer()
        
        # First check should return True
        assert server._should_check_for_updates() is True
        
        # Set last check time to now
        server._last_update_check = datetime.now(timezone.utc)
        
        # Should not check again immediately
        assert server._should_check_for_updates() is False
        
        # Simulate 25 hours later
        from datetime import timedelta
        server._last_update_check = datetime.now(timezone.utc) - timedelta(hours=25)
        
        # Should check again
        assert server._should_check_for_updates() is True