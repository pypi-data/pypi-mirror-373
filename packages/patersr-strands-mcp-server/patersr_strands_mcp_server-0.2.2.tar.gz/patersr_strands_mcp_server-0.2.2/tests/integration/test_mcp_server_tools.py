"""Integration tests for MCP server tool integration."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.strands_mcp.server import StrandsMCPServer
from src.strands_mcp.models.documentation import (
    DocumentChunk,
    DocumentIndex,
    SearchResult
)


@pytest.fixture
def sample_document_index():
    """Create a sample document index for testing."""
    chunks = [
        DocumentChunk(
            id="chunk1",
            title="Getting Started with Strands",
            content="This guide will help you get started with the Strands Agent SDK. The SDK provides a comprehensive framework for building AI agents.",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            section="Getting Started",
            file_path="docs/getting-started.md",
            last_modified=datetime.now(),
            embedding=[0.1, 0.2, 0.3]
        ),
        DocumentChunk(
            id="chunk2",
            title="Multi-Agent Patterns",
            content="Learn about different multi-agent patterns available in Strands. These patterns help you build complex agent interactions.",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent.md",
            section="Multi-Agent",
            file_path="docs/multi-agent.md",
            last_modified=datetime.now(),
            embedding=[0.4, 0.5, 0.6]
        )
    ]
    
    return DocumentIndex(
        version="test-v1.0",
        last_updated=datetime.now(),
        chunks=chunks,
        embedding_model="all-MiniLM-L6-v2"
    )


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    return [
        SearchResult(
            title="Getting Started with Strands",
            snippet="This guide will help you get started with the Strands Agent SDK...",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            relevance_score=0.95,
            section="Getting Started"
        )
    ]


class TestMCPServerToolIntegration:
    """Test MCP server tool integration."""
    
    def test_server_initialization_with_tools(self):
        """Test that server initializes with documentation tools."""
        server = StrandsMCPServer()
        
        # Verify server components
        assert server._search_service is not None
        assert server._tool_registry is not None
        assert server._mcp_server is not None
        
        # Verify tools are registered
        tools = server._tool_registry.get_all_tools()
        assert "search_documentation" in tools
        assert "list_documentation" in tools
        
        # Verify tool schemas
        schemas = server._tool_registry.get_tool_schemas()
        assert len(schemas) == 2
        
        schema_names = [schema["name"] for schema in schemas]
        assert "search_documentation" in schema_names
        assert "list_documentation" in schema_names
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.semantic_search')
    def test_search_tool_mcp_integration(self, mock_semantic_search, mock_load_index, sample_search_results):
        """Test search tool integration with MCP server."""
        # Setup mocks
        mock_load_index.return_value = True
        mock_semantic_search.return_value = sample_search_results
        
        server = StrandsMCPServer()
        
        # Get the search tool
        search_tool = server._tool_registry.get_tool("search_documentation")
        assert search_tool is not None
        
        # Verify tool schema
        schema = search_tool.get_schema()
        assert schema["name"] == "search_documentation"
        assert "inputSchema" in schema
        
        # Verify input schema has required fields
        input_schema = schema["inputSchema"]
        properties = input_schema["properties"]
        assert "query" in properties
        assert "limit" in properties
        assert "min_score" in properties
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    def test_list_tool_mcp_integration(self, mock_load_index, sample_document_index):
        """Test list tool integration with MCP server."""
        # Setup mocks
        mock_load_index.return_value = True
        
        server = StrandsMCPServer()
        server._search_service._document_index = sample_document_index
        
        # Get the list tool
        list_tool = server._tool_registry.get_tool("list_documentation")
        assert list_tool is not None
        
        # Verify tool schema
        schema = list_tool.get_schema()
        assert schema["name"] == "list_documentation"
        assert "inputSchema" in schema
        
        # Verify input schema has required fields
        input_schema = schema["inputSchema"]
        properties = input_schema["properties"]
        assert "section_filter" in properties
        assert "limit" in properties
    
    def test_server_health_check(self):
        """Test server health check functionality."""
        server = StrandsMCPServer()
        
        # Server should not be running initially
        assert not server.is_running
        assert server.uptime == 0.0
        
        # Test health check tool exists
        # Note: We can't easily test the actual FastMCP tool registration
        # without starting the server, but we can verify the method exists
        assert hasattr(server, '_register_health_check')
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.get_index_stats')
    def test_server_service_initialization(self, mock_get_stats, mock_load_index):
        """Test server service initialization."""
        # Setup mocks
        mock_load_index.return_value = True
        mock_get_stats.return_value = {
            'status': 'loaded',
            'total_chunks': 10,
            'unique_documents': 5
        }
        
        server = StrandsMCPServer()
        
        # Verify services are initialized
        assert server._search_service is not None
        assert server._tool_registry is not None
        
        # Verify search service has the expected interface
        assert hasattr(server._search_service, 'load_index')
        assert hasattr(server._search_service, 'semantic_search')
        assert hasattr(server._search_service, 'get_index_stats')
    
    def test_tool_registry_completeness(self):
        """Test that tool registry has all expected tools."""
        server = StrandsMCPServer()
        registry = server._tool_registry
        
        # Verify all expected tools are present
        expected_tools = ["search_documentation", "list_documentation"]
        actual_tools = list(registry.get_all_tools().keys())
        
        for tool_name in expected_tools:
            assert tool_name in actual_tools, f"Missing tool: {tool_name}"
        
        # Verify tool schemas are valid
        schemas = registry.get_tool_schemas()
        assert len(schemas) == len(expected_tools)
        
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "inputSchema" in schema
            assert schema["name"] in expected_tools
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    def test_server_graceful_degradation(self, mock_load_index):
        """Test server handles missing index gracefully."""
        # Setup mock to simulate no index available
        mock_load_index.return_value = False
        
        server = StrandsMCPServer()
        
        # Server should still initialize successfully
        assert server._search_service is not None
        assert server._tool_registry is not None
        
        # Tools should still be available even if index is not loaded
        tools = server._tool_registry.get_all_tools()
        assert len(tools) == 2
        
        # Tools should handle missing index appropriately
        # (This is tested in the individual tool tests)


@pytest.mark.asyncio
async def test_tool_execution_workflow():
    """Test the complete tool execution workflow."""
    with patch('src.strands_mcp.services.search_service.SearchService.load_index') as mock_load_index, \
         patch('src.strands_mcp.services.search_service.SearchService.semantic_search') as mock_search:
        
        # Setup mocks
        mock_load_index.return_value = True
        mock_search.return_value = [
            SearchResult(
                title="Test Document",
                snippet="Test content snippet",
                source_url="https://example.com/test.md",
                relevance_score=0.9,
                section="Test Section"
            )
        ]
        
        server = StrandsMCPServer()
        
        # Get search tool and execute
        search_tool = server._tool_registry.get_tool("search_documentation")
        
        result = await search_tool.execute({
            "query": "test query",
            "limit": 5,
            "min_score": 0.5
        })
        
        # Verify result structure
        assert result.query == "test query"
        assert result.total_found == 1
        assert len(result.results) == 1
        assert result.search_time_ms > 0
        
        # Verify search service was called
        mock_search.assert_called_once()


def test_server_info_configuration():
    """Test server info is properly configured."""
    server = StrandsMCPServer()
    
    # Verify server info is set
    server_info = server._mcp_server.server_info
    assert server_info["name"] == "strands-mcp-server"
    assert server_info["version"] == "0.1.0"
    assert "description" in server_info
    assert "Strands Agent SDK" in server_info["description"]