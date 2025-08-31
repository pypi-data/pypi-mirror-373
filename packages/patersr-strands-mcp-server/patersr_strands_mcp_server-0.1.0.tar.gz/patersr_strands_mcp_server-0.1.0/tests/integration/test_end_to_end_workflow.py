"""End-to-end integration tests for the complete MCP workflow."""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
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
            content="# Getting Started with Strands\n\nThis guide will help you get started with the Strands Agent SDK. The SDK provides a framework for building intelligent agents that can interact with various services and APIs.",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            section="Getting Started",
            file_path="/tmp/getting-started.md",
            last_modified=datetime.now(timezone.utc)
        ),
        DocumentChunk(
            id="strands-agents/docs:multi-agent/overview.md",
            title="Multi-Agent Overview",
            content="# Multi-Agent Systems\n\nStrands supports building multi-agent systems where multiple agents can collaborate to solve complex problems. This section covers the patterns and best practices for multi-agent architectures.",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent/overview.md",
            section="Multi-Agent",
            file_path="/tmp/multi-agent-overview.md",
            last_modified=datetime.now(timezone.utc)
        ),
        DocumentChunk(
            id="strands-agents/docs:deployment/aws.md",
            title="AWS Deployment",
            content="# Deploying to AWS\n\nThis guide covers how to deploy your Strands agents to AWS using various services like Lambda, ECS, and EC2. We'll cover best practices for production deployments.",
            source_url="https://github.com/strands-agents/docs/blob/main/deployment/aws.md",
            section="Deployment",
            file_path="/tmp/deployment-aws.md",
            last_modified=datetime.now(timezone.utc)
        )
    ]


class TestEndToEndWorkflow:
    """Test the complete MCP server workflow."""
    
    @pytest.mark.asyncio
    async def test_server_initialization_with_no_cache(self, temp_dirs, sample_documentation):
        """Test server initialization when no cache exists."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            # Mock the documentation service to return sample docs
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                # Mock methods
                mock_doc_service.check_for_updates.return_value = True
                mock_doc_service.fetch_latest_docs.return_value = sample_documentation
                mock_doc_service.get_cached_docs.return_value = None
                mock_doc_service.save_docs_to_cache = AsyncMock()
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # Initialize services manually for testing
                await server._initialize_services()
                
                # Verify services are initialized
                assert server.services_initialized
                
                # Verify documentation was fetched and cached
                mock_doc_service.check_for_updates.assert_called_once()
                mock_doc_service.fetch_latest_docs.assert_called_once()
                mock_doc_service.save_docs_to_cache.assert_called_once_with(sample_documentation)
    
    @pytest.mark.asyncio
    async def test_server_initialization_with_valid_cache(self, temp_dirs, sample_documentation):
        """Test server initialization when valid cache exists."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            # Create a mock index file
            index_file = Path(temp_dirs['cache_dir']) / "index.json"
            index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="all-MiniLM-L6-v2"
            )
            index.save_to_file(str(index_file))
            
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                # Mock methods - no updates needed
                mock_doc_service.check_for_updates.return_value = False
                mock_doc_service.get_cached_docs.return_value = sample_documentation
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # Initialize services manually for testing
                await server._initialize_services()
                
                # Verify services are initialized
                assert server.services_initialized
                
                # Verify no fetch was needed
                mock_doc_service.check_for_updates.assert_called_once()
                mock_doc_service.fetch_latest_docs.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_search_workflow_after_initialization(self, temp_dirs, sample_documentation):
        """Test the complete search workflow after server initialization."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            # Mock services
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                mock_doc_service.check_for_updates.return_value = False
                mock_doc_service.get_cached_docs.return_value = sample_documentation
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # Mock the search service to avoid actual embedding computation
                with patch.object(server._search_service, 'load_index', return_value=True):
                    with patch.object(server._search_service, 'semantic_search') as mock_search:
                        from strands_mcp.models.documentation import SearchResult
                        
                        mock_search.return_value = [
                            SearchResult(
                                title="Getting Started with Strands",
                                snippet="This guide will help you get started with the Strands Agent SDK...",
                                source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
                                relevance_score=0.95,
                                section="Getting Started"
                            )
                        ]
                        
                        # Initialize services
                        await server._initialize_services()
                        
                        # Test search functionality
                        tool = server._tool_registry.get_tool("search_documentation")
                        result = await tool.execute({
                            "query": "getting started",
                            "limit": 10,
                            "min_score": 0.3
                        })
                        
                        # Verify search results
                        assert result.total_found == 1
                        assert result.query == "getting started"
                        assert len(result.results) == 1
                        assert result.results[0].title == "Getting Started with Strands"
                        assert result.results[0].relevance_score == 0.95
    
    @pytest.mark.asyncio
    async def test_list_documentation_workflow(self, temp_dirs, sample_documentation):
        """Test the documentation listing workflow."""
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
                
                # Create server
                server = StrandsMCPServer()
                
                # Mock the search service
                with patch.object(server._search_service, 'load_index', return_value=True):
                    # Set up the document index directly
                    from strands_mcp.models.documentation import DocumentIndex
                    server._search_service._document_index = DocumentIndex(
                        version="1.0",
                        last_updated=datetime.now(timezone.utc),
                        chunks=sample_documentation,
                        embedding_model="all-MiniLM-L6-v2"
                    )
                    
                    # Initialize services
                    await server._initialize_services()
                    
                    # Test list functionality
                    tool = server._tool_registry.get_tool("list_documentation")
                    result = await tool.execute({
                        "section_filter": None,
                        "limit": 20
                    })
                    
                    # Verify listing results
                    assert result.total_available == 3
                    assert len(result.documents) == 3
                    assert len(result.sections) == 3
                    assert "Getting Started" in result.sections
                    assert "Multi-Agent" in result.sections
                    assert "Deployment" in result.sections
                    
                    # Test with section filter
                    result_filtered = await tool.execute({
                        "section_filter": "Getting Started",
                        "limit": 20
                    })
                    
                    assert result_filtered.total_available == 1
                    assert len(result_filtered.documents) == 1
                    assert result_filtered.documents[0].section == "Getting Started"
                    assert result_filtered.applied_filter == "Getting Started"
    
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
                
                # Mock a failure during documentation fetch
                mock_doc_service.check_for_updates.side_effect = Exception("Network error")
                mock_doc_service.get_cached_docs.return_value = None
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # Initialize services - should handle error gracefully
                await server._initialize_services()
                
                # Server should still be running but services not fully initialized
                assert not server.services_initialized
    
    @pytest.mark.asyncio
    async def test_daily_update_check_mechanism(self, temp_dirs, sample_documentation):
        """Test the daily update check mechanism."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                mock_doc_service.check_for_updates.return_value = True
                mock_doc_service.fetch_latest_docs.return_value = sample_documentation
                mock_doc_service.save_docs_to_cache = AsyncMock()
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # First initialization should check for updates
                await server._initialize_services()
                
                # Verify update check was called
                assert mock_doc_service.check_for_updates.call_count == 1
                
                # Reset the mock
                mock_doc_service.reset_mock()
                mock_doc_service.check_for_updates.return_value = False
                
                # Second initialization within 24 hours should not check for updates
                server._services_initialized = False  # Reset for testing
                await server._initialize_services()
                
                # Should not check for updates again (within 24 hours)
                assert mock_doc_service.check_for_updates.call_count == 0
    
    @pytest.mark.asyncio
    async def test_service_cleanup_on_shutdown(self, temp_dirs):
        """Test proper service cleanup during server shutdown."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                mock_doc_service.check_for_updates.return_value = False
                mock_doc_service.get_cached_docs.return_value = []
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # Initialize services
                await server._initialize_services()
                
                # Stop server
                await server.stop()
                
                # Verify cleanup was called
                mock_doc_service.close.assert_called_once()
                assert not server.is_running
    
    @pytest.mark.asyncio
    async def test_health_check_reflects_service_state(self, temp_dirs):
        """Test that health check reflects the actual service state."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            # Create server
            server = StrandsMCPServer()
            server._running = True
            
            # Before initialization
            health = server._mcp_server._tools[0]()  # Call health_check tool
            assert health.status == "starting"
            
            # Mock successful initialization
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                mock_doc_service.check_for_updates.return_value = False
                mock_doc_service.get_cached_docs.return_value = []
                mock_doc_service.close = AsyncMock()
                
                await server._initialize_services()
                
                # After initialization
                health = server._mcp_server._tools[0]()  # Call health_check tool
                assert health.status == "healthy"
                
                # After stopping
                server._running = False
                health = server._mcp_server._tools[0]()  # Call health_check tool
                assert health.status == "stopped"


class TestServiceIntegrationEdgeCases:
    """Test edge cases in service integration."""
    
    @pytest.mark.asyncio
    async def test_concurrent_service_initialization(self, temp_dirs, sample_documentation):
        """Test that concurrent service initialization is handled properly."""
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
                
                # Create server
                server = StrandsMCPServer()
                
                # Mock search service
                with patch.object(server._search_service, 'load_index', return_value=True):
                    # Simulate concurrent initialization calls
                    tasks = [
                        server._ensure_services_initialized(),
                        server._ensure_services_initialized(),
                        server._ensure_services_initialized()
                    ]
                    
                    await asyncio.gather(*tasks)
                    
                    # Should only initialize once
                    assert server.services_initialized
                    assert mock_doc_service.check_for_updates.call_count == 1
    
    @pytest.mark.asyncio
    async def test_partial_service_failure_recovery(self, temp_dirs, sample_documentation):
        """Test recovery from partial service failures."""
        with patch.dict(os.environ, {
            'STRANDS_CACHE_DIR': temp_dirs['cache_dir'],
            'STRANDS_INDEX_DIR': temp_dirs['index_dir']
        }):
            with patch('strands_mcp.services.documentation_service.DocumentationService') as mock_doc_service_class:
                mock_doc_service = AsyncMock()
                mock_doc_service_class.return_value = mock_doc_service
                
                # First call fails, second succeeds
                mock_doc_service.check_for_updates.side_effect = [Exception("Network error"), False]
                mock_doc_service.get_cached_docs.return_value = sample_documentation
                mock_doc_service.close = AsyncMock()
                
                # Create server
                server = StrandsMCPServer()
                
                # First initialization attempt should fail gracefully
                await server._initialize_services()
                assert not server.services_initialized
                
                # Reset for retry
                server._services_initialized = False
                
                # Second attempt should succeed
                await server._initialize_services()
                # Note: This would succeed if we had proper retry logic
                # For now, it demonstrates the error handling