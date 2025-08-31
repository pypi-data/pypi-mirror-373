"""Integration tests for MCP documentation tools."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.strands_mcp.tools.documentation import (
    SearchDocumentationTool,
    ListDocumentationTool,
    DocumentationToolRegistry,
    SearchDocumentationInput,
    SearchDocumentationOutput,
    ListDocumentationInput,
    ListDocumentationOutput
)
from src.strands_mcp.models.documentation import (
    DocumentChunk,
    DocumentIndex,
    SearchResult,
    SearchQuery
)
from src.strands_mcp.services.search_service import SearchService


@pytest.fixture
def mock_search_service():
    """Create a mock search service for testing."""
    service = MagicMock(spec=SearchService)
    service._document_index = None
    return service


@pytest.fixture
def sample_document_chunks():
    """Create sample document chunks for testing."""
    return [
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
        ),
        DocumentChunk(
            id="chunk3",
            title="Deployment Guide",
            content="Deploy your Strands agents to production environments. This guide covers AWS deployment options and best practices.",
            source_url="https://github.com/strands-agents/docs/blob/main/deployment.md",
            section="Deploy",
            file_path="docs/deployment.md",
            last_modified=datetime.now(),
            embedding=[0.7, 0.8, 0.9]
        )
    ]


@pytest.fixture
def sample_document_index(sample_document_chunks):
    """Create a sample document index for testing."""
    return DocumentIndex(
        version="test-v1.0",
        last_updated=datetime.now(),
        chunks=sample_document_chunks,
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
        ),
        SearchResult(
            title="Multi-Agent Patterns",
            snippet="Learn about different multi-agent patterns available in Strands...",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent.md",
            relevance_score=0.87,
            section="Multi-Agent"
        )
    ]


class TestSearchDocumentationTool:
    """Test cases for SearchDocumentationTool."""
    
    @pytest.mark.asyncio
    async def test_search_tool_initialization(self, mock_search_service):
        """Test search tool initialization."""
        tool = SearchDocumentationTool(mock_search_service)
        
        assert tool.name == "search_documentation"
        assert tool.description == "Search Strands Agent SDK documentation using semantic search"
        assert tool.search_service == mock_search_service
    
    def test_search_tool_schema(self, mock_search_service):
        """Test search tool schema generation."""
        tool = SearchDocumentationTool(mock_search_service)
        schema = tool.get_schema()
        
        assert schema["name"] == "search_documentation"
        assert "description" in schema
        assert "inputSchema" in schema
        
        # Verify input schema structure
        input_schema = schema["inputSchema"]
        assert "properties" in input_schema
        assert "query" in input_schema["properties"]
        assert "limit" in input_schema["properties"]
        assert "min_score" in input_schema["properties"]
    
    @pytest.mark.asyncio
    async def test_search_tool_execution_success(self, mock_search_service, sample_search_results):
        """Test successful search tool execution."""
        # Setup mock
        mock_search_service.semantic_search = AsyncMock(return_value=sample_search_results)
        
        tool = SearchDocumentationTool(mock_search_service)
        
        # Execute search
        arguments = {
            "query": "getting started",
            "limit": 10,
            "min_score": 0.5
        }
        
        result = await tool.execute(arguments)
        
        # Verify result
        assert isinstance(result, SearchDocumentationOutput)
        assert result.query == "getting started"
        assert result.total_found == 2
        assert len(result.results) == 2
        assert result.search_time_ms > 0
        
        # Verify search service was called correctly
        mock_search_service.semantic_search.assert_called_once()
        call_args = mock_search_service.semantic_search.call_args[0][0]
        assert isinstance(call_args, SearchQuery)
        assert call_args.query == "getting started"
        assert call_args.limit == 10
        assert call_args.min_score == 0.5
    
    @pytest.mark.asyncio
    async def test_search_tool_input_validation(self, mock_search_service):
        """Test search tool input validation."""
        tool = SearchDocumentationTool(mock_search_service)
        
        # Test empty query
        with pytest.raises(Exception):  # ValidationError
            await tool.execute({"query": "", "limit": 10})
        
        # Test invalid limit
        with pytest.raises(Exception):  # ValidationError
            await tool.execute({"query": "test", "limit": 0})
        
        # Test invalid min_score
        with pytest.raises(Exception):  # ValidationError
            await tool.execute({"query": "test", "min_score": 1.5})
    
    @pytest.mark.asyncio
    async def test_search_tool_service_error(self, mock_search_service):
        """Test search tool handling of service errors."""
        # Setup mock to raise exception
        mock_search_service.semantic_search = AsyncMock(side_effect=Exception("Search failed"))
        
        tool = SearchDocumentationTool(mock_search_service)
        
        arguments = {
            "query": "test query",
            "limit": 10,
            "min_score": 0.5
        }
        
        with pytest.raises(RuntimeError, match="Failed to execute search"):
            await tool.execute(arguments)


class TestListDocumentationTool:
    """Test cases for ListDocumentationTool."""
    
    @pytest.mark.asyncio
    async def test_list_tool_initialization(self, mock_search_service):
        """Test list tool initialization."""
        tool = ListDocumentationTool(mock_search_service)
        
        assert tool.name == "list_documentation"
        assert tool.description == "Browse available Strands Agent SDK documentation sections and documents"
        assert tool.search_service == mock_search_service
    
    def test_list_tool_schema(self, mock_search_service):
        """Test list tool schema generation."""
        tool = ListDocumentationTool(mock_search_service)
        schema = tool.get_schema()
        
        assert schema["name"] == "list_documentation"
        assert "description" in schema
        assert "inputSchema" in schema
        
        # Verify input schema structure
        input_schema = schema["inputSchema"]
        assert "properties" in input_schema
        assert "section_filter" in input_schema["properties"]
        assert "limit" in input_schema["properties"]
    
    @pytest.mark.asyncio
    async def test_list_tool_execution_success(self, mock_search_service, sample_document_index):
        """Test successful list tool execution."""
        # Setup mock
        mock_search_service._document_index = sample_document_index
        mock_search_service.load_index = AsyncMock(return_value=True)
        
        tool = ListDocumentationTool(mock_search_service)
        
        # Execute listing
        arguments = {
            "section_filter": None,
            "limit": 20
        }
        
        result = await tool.execute(arguments)
        
        # Verify result
        assert isinstance(result, ListDocumentationOutput)
        assert len(result.documents) == 3  # All unique documents
        assert result.total_available == 3
        assert len(result.sections) == 3  # Getting Started, Multi-Agent, Deploy
        assert result.applied_filter is None
        
        # Verify document info
        doc_titles = [doc.title for doc in result.documents]
        assert "Getting Started with Strands" in doc_titles
        assert "Multi-Agent Patterns" in doc_titles
        assert "Deployment Guide" in doc_titles
    
    @pytest.mark.asyncio
    async def test_list_tool_with_section_filter(self, mock_search_service, sample_document_index):
        """Test list tool with section filter."""
        # Setup mock
        mock_search_service._document_index = sample_document_index
        mock_search_service.load_index = AsyncMock(return_value=True)
        
        tool = ListDocumentationTool(mock_search_service)
        
        # Execute listing with filter
        arguments = {
            "section_filter": "Multi",
            "limit": 20
        }
        
        result = await tool.execute(arguments)
        
        # Verify result
        assert isinstance(result, ListDocumentationOutput)
        assert len(result.documents) == 1  # Only Multi-Agent document
        assert result.documents[0].title == "Multi-Agent Patterns"
        assert result.applied_filter == "Multi"
    
    @pytest.mark.asyncio
    async def test_list_tool_no_index(self, mock_search_service):
        """Test list tool when no index is available."""
        # Setup mock with no index
        mock_search_service._document_index = None
        mock_search_service.load_index = AsyncMock(return_value=False)
        
        tool = ListDocumentationTool(mock_search_service)
        
        arguments = {
            "section_filter": None,
            "limit": 20
        }
        
        with pytest.raises(RuntimeError, match="No documentation index available"):
            await tool.execute(arguments)
    
    @pytest.mark.asyncio
    async def test_list_tool_input_validation(self, mock_search_service):
        """Test list tool input validation."""
        tool = ListDocumentationTool(mock_search_service)
        
        # Test invalid limit
        with pytest.raises(Exception):  # ValidationError
            await tool.execute({"limit": 0})
        
        # Test limit too high
        with pytest.raises(Exception):  # ValidationError
            await tool.execute({"limit": 200})


class TestDocumentationToolRegistry:
    """Test cases for DocumentationToolRegistry."""
    
    def test_registry_initialization(self, mock_search_service):
        """Test registry initialization."""
        registry = DocumentationToolRegistry(mock_search_service)
        
        assert registry.search_service == mock_search_service
        assert len(registry.tools) == 2
        assert "search_documentation" in registry.tools
        assert "list_documentation" in registry.tools
    
    def test_get_tool(self, mock_search_service):
        """Test getting tools from registry."""
        registry = DocumentationToolRegistry(mock_search_service)
        
        search_tool = registry.get_tool("search_documentation")
        assert isinstance(search_tool, SearchDocumentationTool)
        
        list_tool = registry.get_tool("list_documentation")
        assert isinstance(list_tool, ListDocumentationTool)
        
        # Test non-existent tool
        assert registry.get_tool("non_existent") is None
    
    def test_get_all_tools(self, mock_search_service):
        """Test getting all tools from registry."""
        registry = DocumentationToolRegistry(mock_search_service)
        
        all_tools = registry.get_all_tools()
        assert len(all_tools) == 2
        assert "search_documentation" in all_tools
        assert "list_documentation" in all_tools
        
        # Verify it returns a copy
        all_tools["new_tool"] = "test"
        assert "new_tool" not in registry.tools
    
    def test_get_tool_schemas(self, mock_search_service):
        """Test getting tool schemas from registry."""
        registry = DocumentationToolRegistry(mock_search_service)
        
        schemas = registry.get_tool_schemas()
        assert len(schemas) == 2
        
        schema_names = [schema["name"] for schema in schemas]
        assert "search_documentation" in schema_names
        assert "list_documentation" in schema_names
        
        # Verify schema structure
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "inputSchema" in schema


@pytest.mark.asyncio
async def test_end_to_end_tool_workflow(mock_search_service, sample_document_index, sample_search_results):
    """Test end-to-end workflow with both tools."""
    # Setup mocks
    mock_search_service._document_index = sample_document_index
    mock_search_service.load_index = AsyncMock(return_value=True)
    mock_search_service.semantic_search = AsyncMock(return_value=sample_search_results)
    
    # Create registry
    registry = DocumentationToolRegistry(mock_search_service)
    
    # Test listing documentation first
    list_tool = registry.get_tool("list_documentation")
    list_result = await list_tool.execute({"limit": 10})
    
    assert len(list_result.documents) == 3
    assert len(list_result.sections) == 3
    
    # Test searching documentation
    search_tool = registry.get_tool("search_documentation")
    search_result = await search_tool.execute({
        "query": "getting started",
        "limit": 5,
        "min_score": 0.5
    })
    
    assert search_result.total_found == 2
    assert len(search_result.results) == 2
    assert search_result.query == "getting started"
    
    # Verify search service was called correctly
    mock_search_service.semantic_search.assert_called_once()