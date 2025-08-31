"""MCP server implementation for Strands documentation search."""

import asyncio
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from pydantic import BaseModel

from .services.documentation_service import DocumentationService
from .services.search_service import SearchService
from .services.indexing_service import DocumentIndexingService
from .tools.documentation import DocumentationToolRegistry, SearchDocumentationInput, SearchDocumentationOutput, ListDocumentationInput, ListDocumentationOutput


logger = logging.getLogger(__name__)


class ServerHealth(BaseModel):
    """Server health status model."""
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str = "0.1.0"


class StrandsMCPServer:
    """Main MCP server class for Strands documentation search."""
    
    def __init__(self) -> None:
        """Initialize the MCP server."""
        self._start_time: Optional[datetime] = None
        self._mcp_server: Optional[FastMCP] = None
        self._running = False
        self._services_initialized = False
        self._last_update_check: Optional[datetime] = None
        
        # Initialize services
        self._documentation_service = DocumentationService()
        self._indexing_service = DocumentIndexingService()
        self._search_service = SearchService()
        # Wire the same indexing service instance to the search service
        self._search_service._indexing_service = self._indexing_service
        self._tool_registry = DocumentationToolRegistry(self._search_service)
        
        # Initialize FastMCP server
        self._mcp_server = FastMCP("Strands Documentation Search")
        
        # Register server info
        self._mcp_server.server_info = {
            "name": "strands-mcp-server",
            "version": "0.1.0",
            "description": "MCP server for Strands Agent SDK documentation search and project assistance"
        }
        
        # Register tools
        self._register_health_check()
        self._register_documentation_tools()
        
        logger.info("Initialized Strands MCP Server with FastMCP")
    
    def _register_health_check(self) -> None:
        """Register health check tool."""
        
        @self._mcp_server.tool()
        def health_check() -> ServerHealth:
            """Check server health status."""
            uptime = 0.0
            if self._start_time:
                uptime = (datetime.now() - self._start_time).total_seconds()
            
            status = "healthy" if self._running and self._services_initialized else "starting"
            if not self._running:
                status = "stopped"
            
            return ServerHealth(
                status=status,
                timestamp=datetime.now(),
                uptime_seconds=uptime
            )
    
    def _register_documentation_tools(self) -> None:
        """Register documentation search and listing tools."""
        
        @self._mcp_server.tool()
        async def search_documentation(
            query: str,
            limit: int = 10,
            min_score: float = 0.3
        ) -> SearchDocumentationOutput:
            """Search Strands Agent SDK documentation using semantic search.
            
            Args:
                query: Search query to find relevant documentation
                limit: Maximum number of results to return (1-50)
                min_score: Minimum relevance score (0.0-1.0)
                
            Returns:
                Search results with relevance scores and snippets
            """
            # Ensure services are initialized
            await self._ensure_services_initialized()
            
            tool = self._tool_registry.get_tool("search_documentation")
            arguments = {
                "query": query,
                "limit": limit,
                "min_score": min_score
            }
            return await tool.execute(arguments)
        
        @self._mcp_server.tool()
        async def list_documentation(
            section_filter: str = None,
            limit: int = 20
        ) -> ListDocumentationOutput:
            """Browse available Strands Agent SDK documentation sections and documents.
            
            Args:
                section_filter: Optional filter to show only specific sections
                limit: Maximum number of documents to return (1-100)
                
            Returns:
                List of available documentation with previews
            """
            # Ensure services are initialized
            await self._ensure_services_initialized()
            
            tool = self._tool_registry.get_tool("list_documentation")
            arguments = {
                "section_filter": section_filter,
                "limit": limit
            }
            return await tool.execute(arguments)
    
    async def _ensure_services_initialized(self) -> None:
        """Ensure services are initialized, initializing them if needed."""
        if self._services_initialized:
            return
        
        await self._initialize_services()
    
    async def _initialize_services(self) -> None:
        """Initialize all services and perform startup sequence."""
        try:
            logger.info("Initializing services and performing startup sequence")
            
            # Check if we need to update documentation
            await self._check_and_update_documentation()
            
            # Load the search index
            index_loaded = await self._search_service.load_index()
            
            if not index_loaded:
                logger.warning("No search index found - attempting to create one")
                await self._create_initial_index()
            else:
                stats = self._search_service.get_index_stats()
                logger.info(f"Search index loaded: {stats['total_chunks']} chunks from {stats['unique_documents']} documents")
            
            self._services_initialized = True
            logger.info("Services initialization completed successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            # Don't fail startup completely - allow server to run with limited functionality
            self._services_initialized = False
    
    def _should_check_for_updates(self) -> bool:
        """Determine if we should check for documentation updates.
        
        Returns:
            True if we should check for updates, False otherwise
        """
        # Check on first startup
        if self._last_update_check is None:
            return True
        
        # Check if it's been more than 24 hours since last check
        now = datetime.now(timezone.utc)
        hours_since_check = (now - self._last_update_check).total_seconds() / 3600
        
        return hours_since_check >= 24
    
    async def _check_and_update_documentation(self) -> None:
        """Check for documentation updates and update if necessary."""
        try:
            if not self._should_check_for_updates():
                logger.info("Skipping documentation update check (checked recently)")
                return
            
            logger.info("Checking for documentation updates")
            self._last_update_check = datetime.now(timezone.utc)
            
            # Check if updates are available
            updates_available = await self._documentation_service.check_for_updates()
            
            if updates_available:
                logger.info("Documentation updates available, fetching latest version")
                await self._update_documentation()
            else:
                logger.info("Documentation is up to date")
                
        except Exception as e:
            logger.error(f"Error during documentation update check: {e}")
            # Continue with cached documentation if available
    
    async def _update_documentation(self) -> None:
        """Update documentation from remote source."""
        try:
            # Fetch latest documentation
            chunks = await self._documentation_service.fetch_latest_docs()
            
            if not chunks:
                logger.warning("No documentation chunks fetched during update")
                return
            
            # Save to cache
            await self._documentation_service.save_docs_to_cache(chunks)
            
            # Rebuild search index
            logger.info("Rebuilding search index with updated documentation")
            try:
                # Convert chunks to the format expected by index_documents
                # Format: (content, title, source_url, file_path, last_modified)
                documents = [
                    (chunk.content, chunk.title, chunk.source_url, chunk.file_path, chunk.last_modified)
                    for chunk in chunks
                ]
                await self._indexing_service.index_documents(documents)
                logger.info(f"Documentation updated successfully: {len(chunks)} chunks indexed")
                
                # Reload the index into the search service
                await self._search_service.load_index()
                logger.info("Updated search index loaded into search service")
            except Exception as index_error:
                logger.error(f"Failed to rebuild search index after update: {index_error}")
                # Don't raise - cache was updated successfully
            
        except Exception as e:
            logger.error(f"Failed to update documentation: {e}")
            logger.info("Continuing with existing cached documentation if available")
            # Don't raise - allow server to continue with existing cache
    
    async def _create_initial_index(self) -> None:
        """Create initial search index if none exists."""
        try:
            logger.info("Creating initial search index")
            
            # Try to get cached documentation first
            cached_chunks = await self._documentation_service.get_cached_docs()
            
            if cached_chunks:
                logger.info(f"Using cached documentation: {len(cached_chunks)} chunks")
                chunks = cached_chunks
            else:
                logger.info("No cached documentation found, attempting to fetch from remote")
                try:
                    chunks = await self._documentation_service.fetch_latest_docs()
                    
                    if chunks:
                        await self._documentation_service.save_docs_to_cache(chunks)
                        logger.info(f"Successfully fetched and cached {len(chunks)} chunks")
                    else:
                        logger.warning("No documentation chunks were fetched from remote")
                        chunks = []
                except Exception as fetch_error:
                    logger.warning(f"Failed to fetch remote documentation: {fetch_error}")
                    logger.info("Server will continue without documentation index")
                    chunks = []
            
            if chunks:
                # Build search index
                try:
                    # Convert chunks to the format expected by index_documents
                    # Format: (content, title, source_url, file_path, last_modified)
                    documents = [
                        (chunk.content, chunk.title, chunk.source_url, chunk.file_path, chunk.last_modified)
                        for chunk in chunks
                    ]
                    await self._indexing_service.index_documents(documents)
                    logger.info(f"Initial search index created with {len(chunks)} chunks")
                    
                    # Load the index into the search service
                    await self._search_service.load_index()
                    logger.info("Search index loaded into search service")
                    
                except Exception as index_error:
                    logger.error(f"Failed to build search index: {index_error}")
                    logger.info("Server will continue without search functionality")
            else:
                logger.info("No documentation available to index - server will run with limited functionality")
                
        except Exception as e:
            logger.error(f"Error during initial index creation: {e}")
            logger.info("Server will continue with limited functionality")
            # Don't re-raise - allow server to continue
    
    def start(self) -> None:
        """Start the MCP server."""
        try:
            self._start_time = datetime.now()
            self._running = True
            
            logger.info("Starting Strands MCP Server with stdio transport")
            
            # Services will be initialized lazily on first tool call
            # This allows the server to start quickly and handle initialization errors gracefully
            
            # Run the FastMCP server with stdio transport
            # FastMCP.run() handles the event loop internally
            self._mcp_server.run(transport="stdio")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self._running = False
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping Strands MCP Server")
        self._running = False
        
        # Clean up services
        try:
            await self._cleanup_services()
        except Exception as e:
            logger.error(f"Error during service cleanup: {e}")
        
        # FastMCP handles cleanup automatically when the transport closes
        logger.info("Strands MCP Server stopped")
    
    async def _cleanup_services(self) -> None:
        """Clean up services and resources."""
        try:
            # Close documentation service HTTP client
            if hasattr(self._documentation_service, 'close'):
                await self._documentation_service.close()
            
            logger.info("Services cleanup completed")
        except Exception as e:
            logger.error(f"Error during service cleanup: {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    @property
    def uptime(self) -> float:
        """Get server uptime in seconds."""
        if not self._start_time:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
    
    @property
    def services_initialized(self) -> bool:
        """Check if services are initialized."""
        return self._services_initialized