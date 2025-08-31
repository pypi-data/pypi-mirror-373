"""MCP tools for documentation search and browsing."""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError

from ..models.documentation import SearchQuery, SearchResult
from ..services.search_service import SearchService

logger = logging.getLogger(__name__)


class SearchDocumentationInput(BaseModel):
    """Input schema for documentation search tool."""
    
    query: str = Field(
        ..., 
        description="Search query to find relevant documentation",
        min_length=1,
        max_length=1000
    )
    limit: int = Field(
        10,
        description="Maximum number of results to return",
        ge=1,
        le=50
    )
    min_score: float = Field(
        0.3,
        description="Minimum relevance score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class SearchDocumentationOutput(BaseModel):
    """Output schema for documentation search tool."""
    
    results: List[SearchResult] = Field(
        ...,
        description="List of search results ranked by relevance"
    )
    total_found: int = Field(
        ...,
        description="Total number of results found"
    )
    query: str = Field(
        ...,
        description="Original search query"
    )
    search_time_ms: float = Field(
        ...,
        description="Search execution time in milliseconds"
    )


class ListDocumentationInput(BaseModel):
    """Input schema for listing documentation tool."""
    
    section_filter: Optional[str] = Field(
        None,
        description="Optional filter to show only specific sections",
        max_length=100
    )
    limit: int = Field(
        20,
        description="Maximum number of documents to return",
        ge=1,
        le=100
    )


class DocumentInfo(BaseModel):
    """Information about a documentation document."""
    
    title: str = Field(..., description="Document title")
    section: str = Field(..., description="Document section")
    source_url: str = Field(..., description="Link to full document")
    content_preview: str = Field(..., description="Brief preview of content")


class ListDocumentationOutput(BaseModel):
    """Output schema for listing documentation tool."""
    
    documents: List[DocumentInfo] = Field(
        ...,
        description="List of available documentation"
    )
    total_available: int = Field(
        ...,
        description="Total number of documents available"
    )
    sections: List[str] = Field(
        ...,
        description="List of available sections"
    )
    applied_filter: Optional[str] = Field(
        None,
        description="Section filter that was applied"
    )


class SearchDocumentationTool:
    """MCP tool for searching Strands documentation."""
    
    def __init__(self, search_service: SearchService):
        """Initialize the search tool.
        
        Args:
            search_service: Service for performing searches
        """
        self.search_service = search_service
        self.name = "search_documentation"
        self.description = "Search Strands Agent SDK documentation using semantic search"
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the MCP tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": SearchDocumentationInput.model_json_schema()
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> SearchDocumentationOutput:
        """Execute the documentation search.
        
        Args:
            arguments: Tool input arguments
            
        Returns:
            Search results
            
        Raises:
            ValidationError: If input validation fails
            RuntimeError: If search service is not available
        """
        import time
        
        start_time = time.time()
        
        try:
            # Validate input
            search_input = SearchDocumentationInput(**arguments)
            logger.info(f"Executing documentation search for: '{search_input.query}'")
            
            # Create search query
            search_query = SearchQuery(
                query=search_input.query,
                limit=search_input.limit,
                min_score=search_input.min_score
            )
            
            # Perform search
            results = await self.search_service.semantic_search(search_query)
            
            # Calculate search time
            search_time_ms = (time.time() - start_time) * 1000
            
            # Create output
            output = SearchDocumentationOutput(
                results=results,
                total_found=len(results),
                query=search_input.query,
                search_time_ms=search_time_ms
            )
            
            logger.info(f"Search completed in {search_time_ms:.2f}ms, found {len(results)} results")
            return output
            
        except ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            raise RuntimeError(f"Failed to execute search: {str(e)}")


class ListDocumentationTool:
    """MCP tool for browsing available documentation."""
    
    def __init__(self, search_service: SearchService):
        """Initialize the list tool.
        
        Args:
            search_service: Service for accessing documentation index
        """
        self.search_service = search_service
        self.name = "list_documentation"
        self.description = "Browse available Strands Agent SDK documentation sections and documents"
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the MCP tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": ListDocumentationInput.model_json_schema()
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> ListDocumentationOutput:
        """Execute the documentation listing.
        
        Args:
            arguments: Tool input arguments
            
        Returns:
            List of available documentation
            
        Raises:
            ValidationError: If input validation fails
            RuntimeError: If search service is not available
        """
        try:
            # Validate input
            list_input = ListDocumentationInput(**arguments)
            logger.info(f"Listing documentation with filter: {list_input.section_filter}")
            
            # Ensure index is loaded
            if self.search_service._document_index is None:
                await self.search_service.load_index()
            
            if self.search_service._document_index is None:
                raise RuntimeError("No documentation index available")
            
            # Get all chunks
            all_chunks = self.search_service._document_index.chunks
            
            # Apply section filter if provided
            filtered_chunks = all_chunks
            if list_input.section_filter:
                filter_lower = list_input.section_filter.lower()
                filtered_chunks = [
                    chunk for chunk in all_chunks
                    if filter_lower in chunk.section.lower()
                ]
            
            # Get unique documents (by title and section combination)
            seen_docs = set()
            unique_documents = []
            
            for chunk in filtered_chunks:
                doc_key = (chunk.title, chunk.section)
                if doc_key not in seen_docs:
                    seen_docs.add(doc_key)
                    
                    # Create content preview (first 200 chars)
                    preview = chunk.content[:200].strip()
                    if len(chunk.content) > 200:
                        preview += "..."
                    
                    doc_info = DocumentInfo(
                        title=chunk.title,
                        section=chunk.section,
                        source_url=chunk.source_url,
                        content_preview=preview
                    )
                    unique_documents.append(doc_info)
            
            # Sort by section then title
            unique_documents.sort(key=lambda x: (x.section, x.title))
            
            # Apply limit
            limited_documents = unique_documents[:list_input.limit]
            
            # Get all available sections
            all_sections = sorted(list(set(chunk.section for chunk in all_chunks)))
            
            # Create output
            output = ListDocumentationOutput(
                documents=limited_documents,
                total_available=len(unique_documents),
                sections=all_sections,
                applied_filter=list_input.section_filter
            )
            
            logger.info(f"Listed {len(limited_documents)} documents from {len(all_sections)} sections")
            return output
            
        except ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Documentation listing failed: {e}")
            raise RuntimeError(f"Failed to list documentation: {str(e)}")


class DocumentationToolRegistry:
    """Registry for documentation-related MCP tools."""
    
    def __init__(self, search_service: SearchService):
        """Initialize the tool registry.
        
        Args:
            search_service: Service for search operations
        """
        self.search_service = search_service
        self.tools = {
            "search_documentation": SearchDocumentationTool(search_service),
            "list_documentation": ListDocumentationTool(search_service)
        }
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all registered tools.
        
        Returns:
            Dictionary of tool name to tool instance
        """
        return self.tools.copy()
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools.
        
        Returns:
            List of tool schemas for MCP registration
        """
        return [tool.get_schema() for tool in self.tools.values()]