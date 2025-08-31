"""Integration tests for MCP protocol tool communication."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from io import StringIO
import sys

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
            content="This comprehensive guide will help you get started with the Strands Agent SDK. The SDK provides a powerful framework for building intelligent AI agents that can interact with various services and APIs.",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            section="Getting Started",
            file_path="docs/getting-started.md",
            last_modified=datetime.now(),
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
        ),
        DocumentChunk(
            id="chunk2",
            title="Multi-Agent Patterns",
            content="Learn about different multi-agent patterns available in Strands. These patterns help you build complex agent interactions including hierarchical agents, peer-to-peer communication, and workflow orchestration.",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent.md",
            section="Multi-Agent",
            file_path="docs/multi-agent.md",
            last_modified=datetime.now(),
            embedding=[0.4, 0.5, 0.6, 0.7, 0.8]
        ),
        DocumentChunk(
            id="chunk3",
            title="Deployment Guide",
            content="Deploy your Strands agents to production environments. This guide covers AWS deployment options, containerization, monitoring, and best practices for scaling your agent applications.",
            source_url="https://github.com/strands-agents/docs/blob/main/deployment.md",
            section="Deploy",
            file_path="docs/deployment.md",
            last_modified=datetime.now(),
            embedding=[0.7, 0.8, 0.9, 0.1, 0.2]
        ),
        DocumentChunk(
            id="chunk4",
            title="Observability and Evaluation",
            content="Monitor and evaluate your Strands agents using built-in observability tools. Learn how to set up logging, metrics, tracing, and automated evaluation pipelines for your agent applications.",
            source_url="https://github.com/strands-agents/docs/blob/main/observability.md",
            section="Observability",
            file_path="docs/observability.md",
            last_modified=datetime.now(),
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6]
        )
    ]
    
    return DocumentIndex(
        version="test-v1.0",
        last_updated=datetime.now(),
        chunks=chunks,
        embedding_model="all-MiniLM-L6-v2"
    )


@pytest.fixture
def mock_search_results():
    """Create mock search results for testing."""
    return [
        SearchResult(
            title="Getting Started with Strands",
            snippet="This comprehensive guide will help you get started with the Strands Agent SDK. The SDK provides a powerful framework...",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            relevance_score=0.95,
            section="Getting Started"
        ),
        SearchResult(
            title="Multi-Agent Patterns",
            snippet="Learn about different multi-agent patterns available in Strands. These patterns help you build complex agent interactions...",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent.md",
            relevance_score=0.87,
            section="Multi-Agent"
        )
    ]


class TestMCPProtocolToolIntegration:
    """Test MCP protocol integration with documentation tools."""
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.semantic_search')
    def test_search_tool_mcp_schema_validation(self, mock_search, mock_load_index, mock_search_results):
        """Test that search tool MCP schema is valid and complete."""
        # Setup mocks
        mock_load_index.return_value = True
        mock_search.return_value = mock_search_results
        
        server = StrandsMCPServer()
        search_tool = server._tool_registry.get_tool("search_documentation")
        
        # Get tool schema
        schema = search_tool.get_schema()
        
        # Validate schema structure
        assert "name" in schema
        assert "description" in schema
        assert "inputSchema" in schema
        
        # Validate input schema details
        input_schema = schema["inputSchema"]
        assert input_schema["type"] == "object"
        assert "properties" in input_schema
        assert "required" in input_schema
        
        properties = input_schema["properties"]
        
        # Validate query field
        assert "query" in properties
        query_prop = properties["query"]
        assert query_prop["type"] == "string"
        assert "description" in query_prop
        assert query_prop["minLength"] == 1
        assert query_prop["maxLength"] == 1000
        
        # Validate limit field
        assert "limit" in properties
        limit_prop = properties["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 50
        assert limit_prop["default"] == 10
        
        # Validate min_score field
        assert "min_score" in properties
        score_prop = properties["min_score"]
        assert score_prop["type"] == "number"
        assert score_prop["minimum"] == 0.0
        assert score_prop["maximum"] == 1.0
        assert score_prop["default"] == 0.3
        
        # Validate required fields
        assert "query" in input_schema["required"]
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    def test_list_tool_mcp_schema_validation(self, mock_load_index, sample_document_index):
        """Test that list tool MCP schema is valid and complete."""
        # Setup mocks
        mock_load_index.return_value = True
        
        server = StrandsMCPServer()
        server._search_service._document_index = sample_document_index
        list_tool = server._tool_registry.get_tool("list_documentation")
        
        # Get tool schema
        schema = list_tool.get_schema()
        
        # Validate schema structure
        assert "name" in schema
        assert "description" in schema
        assert "inputSchema" in schema
        
        # Validate input schema details
        input_schema = schema["inputSchema"]
        assert input_schema["type"] == "object"
        assert "properties" in input_schema
        
        properties = input_schema["properties"]
        
        # Validate section_filter field
        assert "section_filter" in properties
        filter_prop = properties["section_filter"]
        # Pydantic generates anyOf for optional fields
        assert "anyOf" in filter_prop or "type" in filter_prop
        assert "description" in filter_prop
        if "anyOf" in filter_prop:
            # Check that it allows string and null
            types = [item.get("type") for item in filter_prop["anyOf"]]
            assert "string" in types
            assert "null" in types
        
        # Validate limit field
        assert "limit" in properties
        limit_prop = properties["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 100
        assert limit_prop["default"] == 20
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.semantic_search')
    @pytest.mark.asyncio
    async def test_search_tool_output_schema_compliance(self, mock_search, mock_load_index, mock_search_results):
        """Test that search tool output complies with expected schema."""
        # Setup mocks
        mock_load_index.return_value = True
        mock_search.return_value = mock_search_results
        
        server = StrandsMCPServer()
        search_tool = server._tool_registry.get_tool("search_documentation")
        
        # Execute search
        result = await search_tool.execute({
            "query": "getting started with agents",
            "limit": 5,
            "min_score": 0.5
        })
        
        # Validate output structure
        assert hasattr(result, 'results')
        assert hasattr(result, 'total_found')
        assert hasattr(result, 'query')
        assert hasattr(result, 'search_time_ms')
        
        # Validate output values
        assert isinstance(result.results, list)
        assert isinstance(result.total_found, int)
        assert isinstance(result.query, str)
        assert isinstance(result.search_time_ms, float)
        
        assert result.query == "getting started with agents"
        assert result.total_found == len(mock_search_results)
        assert result.search_time_ms > 0
        
        # Validate individual search results
        for search_result in result.results:
            assert hasattr(search_result, 'title')
            assert hasattr(search_result, 'snippet')
            assert hasattr(search_result, 'source_url')
            assert hasattr(search_result, 'relevance_score')
            assert hasattr(search_result, 'section')
            
            assert isinstance(search_result.title, str)
            assert isinstance(search_result.snippet, str)
            assert isinstance(search_result.source_url, str)
            assert isinstance(search_result.relevance_score, float)
            assert isinstance(search_result.section, str)
            
            assert len(search_result.title) > 0
            assert len(search_result.snippet) > 0
            assert search_result.source_url.startswith("https://")
            assert 0.0 <= search_result.relevance_score <= 1.0
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @pytest.mark.asyncio
    async def test_list_tool_output_schema_compliance(self, mock_load_index, sample_document_index):
        """Test that list tool output complies with expected schema."""
        # Setup mocks
        mock_load_index.return_value = True
        
        server = StrandsMCPServer()
        server._search_service._document_index = sample_document_index
        list_tool = server._tool_registry.get_tool("list_documentation")
        
        # Execute listing
        result = await list_tool.execute({
            "section_filter": None,
            "limit": 10
        })
        
        # Validate output structure
        assert hasattr(result, 'documents')
        assert hasattr(result, 'total_available')
        assert hasattr(result, 'sections')
        assert hasattr(result, 'applied_filter')
        
        # Validate output values
        assert isinstance(result.documents, list)
        assert isinstance(result.total_available, int)
        assert isinstance(result.sections, list)
        assert result.applied_filter is None
        
        assert result.total_available > 0
        assert len(result.sections) > 0
        
        # Validate individual document info
        for doc_info in result.documents:
            assert hasattr(doc_info, 'title')
            assert hasattr(doc_info, 'section')
            assert hasattr(doc_info, 'source_url')
            assert hasattr(doc_info, 'content_preview')
            
            assert isinstance(doc_info.title, str)
            assert isinstance(doc_info.section, str)
            assert isinstance(doc_info.source_url, str)
            assert isinstance(doc_info.content_preview, str)
            
            assert len(doc_info.title) > 0
            assert len(doc_info.section) > 0
            assert doc_info.source_url.startswith("https://")
            assert len(doc_info.content_preview) > 0
        
        # Validate sections list
        for section in result.sections:
            assert isinstance(section, str)
            assert len(section) > 0
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.semantic_search')
    @pytest.mark.asyncio
    async def test_search_tool_error_handling(self, mock_search, mock_load_index):
        """Test search tool error handling and validation."""
        # Setup mocks
        mock_load_index.return_value = True
        
        server = StrandsMCPServer()
        search_tool = server._tool_registry.get_tool("search_documentation")
        
        # Test input validation errors
        with pytest.raises(Exception):  # Should raise ValidationError
            await search_tool.execute({
                "query": "",  # Empty query
                "limit": 10
            })
        
        with pytest.raises(Exception):  # Should raise ValidationError
            await search_tool.execute({
                "query": "test",
                "limit": 0  # Invalid limit
            })
        
        with pytest.raises(Exception):  # Should raise ValidationError
            await search_tool.execute({
                "query": "test",
                "min_score": 1.5  # Invalid score
            })
        
        # Test service error handling
        mock_search.side_effect = Exception("Search service error")
        
        with pytest.raises(RuntimeError, match="Failed to execute search"):
            await search_tool.execute({
                "query": "test query",
                "limit": 5
            })
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @pytest.mark.asyncio
    async def test_list_tool_error_handling(self, mock_load_index):
        """Test list tool error handling and validation."""
        # Setup mocks
        mock_load_index.return_value = False  # No index available
        
        server = StrandsMCPServer()
        list_tool = server._tool_registry.get_tool("list_documentation")
        
        # Test no index error
        with pytest.raises(RuntimeError, match="No documentation index available"):
            await list_tool.execute({
                "limit": 10
            })
        
        # Test input validation errors
        with pytest.raises(Exception):  # Should raise ValidationError
            await list_tool.execute({
                "limit": 0  # Invalid limit
            })
        
        with pytest.raises(Exception):  # Should raise ValidationError
            await list_tool.execute({
                "limit": 200  # Limit too high
            })
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @patch('src.strands_mcp.services.search_service.SearchService.semantic_search')
    @pytest.mark.asyncio
    async def test_tool_performance_characteristics(self, mock_search, mock_load_index, mock_search_results):
        """Test tool performance characteristics and response times."""
        # Setup mocks
        mock_load_index.return_value = True
        mock_search.return_value = mock_search_results
        
        server = StrandsMCPServer()
        search_tool = server._tool_registry.get_tool("search_documentation")
        
        # Execute multiple searches and measure consistency
        search_times = []
        for i in range(5):
            result = await search_tool.execute({
                "query": f"test query {i}",
                "limit": 10
            })
            search_times.append(result.search_time_ms)
        
        # Verify all searches completed successfully
        assert len(search_times) == 5
        assert all(time > 0 for time in search_times)
        
        # Verify search service was called for each request
        assert mock_search.call_count == 5
    
    @patch('src.strands_mcp.services.search_service.SearchService.load_index')
    @pytest.mark.asyncio
    async def test_tool_section_filtering_accuracy(self, mock_load_index, sample_document_index):
        """Test accuracy of section filtering in list tool."""
        # Setup mocks
        mock_load_index.return_value = True
        
        server = StrandsMCPServer()
        server._search_service._document_index = sample_document_index
        list_tool = server._tool_registry.get_tool("list_documentation")
        
        # Test filtering by different sections
        test_cases = [
            ("Getting", ["Getting Started"]),
            ("Multi", ["Multi-Agent"]),
            ("Deploy", ["Deploy"]),
            ("Observ", ["Observability"]),
            ("agent", ["Multi-Agent"])  # Case insensitive
        ]
        
        for filter_term, expected_sections in test_cases:
            result = await list_tool.execute({
                "section_filter": filter_term,
                "limit": 20
            })
            
            # Verify filtering worked correctly
            assert result.applied_filter == filter_term
            
            # Check that all returned documents match the filter
            returned_sections = [doc.section for doc in result.documents]
            for section in returned_sections:
                assert any(expected in section for expected in expected_sections), \
                    f"Section '{section}' doesn't match filter '{filter_term}'"
    
    def test_tool_registry_mcp_compliance(self):
        """Test that tool registry provides MCP-compliant tool definitions."""
        server = StrandsMCPServer()
        registry = server._tool_registry
        
        # Get all tool schemas
        schemas = registry.get_tool_schemas()
        
        # Verify each schema is MCP compliant
        for schema in schemas:
            # Required MCP tool fields
            assert "name" in schema
            assert "description" in schema
            assert "inputSchema" in schema
            
            # Validate name format (should be valid identifier)
            assert isinstance(schema["name"], str)
            assert len(schema["name"]) > 0
            assert schema["name"].replace("_", "").isalnum()
            
            # Validate description
            assert isinstance(schema["description"], str)
            assert len(schema["description"]) > 10  # Should be descriptive
            
            # Validate input schema is valid JSON Schema
            input_schema = schema["inputSchema"]
            assert isinstance(input_schema, dict)
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            
            if "properties" in input_schema:
                assert isinstance(input_schema["properties"], dict)
                
                # Validate each property has proper schema
                for prop_name, prop_schema in input_schema["properties"].items():
                    assert isinstance(prop_schema, dict)
                    # Pydantic may use "type" or "anyOf" for optional fields
                    assert "type" in prop_schema or "anyOf" in prop_schema
                    assert "description" in prop_schema
                    assert isinstance(prop_schema["description"], str)
                    assert len(prop_schema["description"]) > 0


@pytest.mark.asyncio
async def test_end_to_end_mcp_tool_workflow():
    """Test complete end-to-end workflow with both MCP tools."""
    with patch('src.strands_mcp.services.search_service.SearchService.load_index') as mock_load_index, \
         patch('src.strands_mcp.services.search_service.SearchService.semantic_search') as mock_search:
        
        # Setup test data
        sample_chunks = [
            DocumentChunk(
                id="chunk1",
                title="Getting Started Guide",
                content="Complete guide to getting started with Strands Agent SDK",
                source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
                section="Getting Started",
                file_path="docs/getting-started.md",
                last_modified=datetime.now(),
                embedding=[0.1, 0.2, 0.3]
            )
        ]
        
        sample_index = DocumentIndex(
            version="test-v1.0",
            last_updated=datetime.now(),
            chunks=sample_chunks,
            embedding_model="all-MiniLM-L6-v2"
        )
        
        sample_results = [
            SearchResult(
                title="Getting Started Guide",
                snippet="Complete guide to getting started with Strands Agent SDK",
                source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
                relevance_score=0.95,
                section="Getting Started"
            )
        ]
        
        # Setup mocks
        mock_load_index.return_value = True
        mock_search.return_value = sample_results
        
        # Initialize server
        server = StrandsMCPServer()
        server._search_service._document_index = sample_index
        
        # Test workflow: List -> Search -> Verify
        
        # Step 1: List available documentation
        list_tool = server._tool_registry.get_tool("list_documentation")
        list_result = await list_tool.execute({"limit": 10})
        
        assert len(list_result.documents) == 1
        assert list_result.documents[0].title == "Getting Started Guide"
        assert "Getting Started" in list_result.sections
        
        # Step 2: Search for specific content
        search_tool = server._tool_registry.get_tool("search_documentation")
        search_result = await search_tool.execute({
            "query": "getting started",
            "limit": 5,
            "min_score": 0.5
        })
        
        assert search_result.total_found == 1
        assert len(search_result.results) == 1
        assert search_result.results[0].title == "Getting Started Guide"
        assert search_result.results[0].relevance_score == 0.95
        
        # Step 3: Verify search service integration
        mock_search.assert_called_once()
        call_args = mock_search.call_args[0][0]
        assert call_args.query == "getting started"
        assert call_args.limit == 5
        assert call_args.min_score == 0.5
        
        # Step 4: Test filtered listing
        filtered_result = await list_tool.execute({
            "section_filter": "Getting",
            "limit": 10
        })
        
        assert len(filtered_result.documents) == 1
        assert filtered_result.applied_filter == "Getting"
        assert filtered_result.documents[0].section == "Getting Started"


def test_mcp_server_tool_registration():
    """Test that MCP server properly registers all documentation tools."""
    server = StrandsMCPServer()
    
    # Verify server has FastMCP instance
    assert server._mcp_server is not None
    
    # Verify server info is configured
    server_info = server._mcp_server.server_info
    assert server_info["name"] == "strands-mcp-server"
    assert server_info["version"] == "0.1.0"
    assert "Strands Agent SDK" in server_info["description"]
    
    # Verify tool registry is properly initialized
    assert server._tool_registry is not None
    tools = server._tool_registry.get_all_tools()
    assert len(tools) == 2
    assert "search_documentation" in tools
    assert "list_documentation" in tools
    
    # Verify each tool has proper MCP schema
    for tool_name, tool in tools.items():
        schema = tool.get_schema()
        assert schema["name"] == tool_name
        assert len(schema["description"]) > 0
        assert "inputSchema" in schema