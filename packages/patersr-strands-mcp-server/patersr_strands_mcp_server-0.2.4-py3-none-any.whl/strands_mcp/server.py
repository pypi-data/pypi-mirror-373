"""MCP server implementation for Strands documentation search."""

import asyncio
import logging
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from pydantic import BaseModel

from .services.documentation_service import DocumentationService
from .services.search_service import SearchService
from .services.indexing_service import DocumentIndexingService
from .tools.documentation import DocumentationToolRegistry, SearchDocumentationInput, SearchDocumentationOutput, ListDocumentationInput, ListDocumentationOutput
from .models.documentation import DocumentChunk, DocumentIndex
from .utils.error_handler import ErrorHandler, handle_errors
from .utils.health_check import HealthChecker, SystemHealth
from .utils.errors import StrandsMCPError, ServiceUnavailableError


logger = logging.getLogger(__name__)


class ServerHealth(BaseModel):
    """Server health status model."""
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str = "0.2.2"
    components: List[Dict[str, Any]] = []
    error_count_24h: int = 0
    last_error: Optional[str] = None


class StrandsMCPServer:
    """Main MCP server class for Strands documentation search."""
    
    def __init__(self) -> None:
        """Initialize the MCP server."""
        self._start_time: Optional[datetime] = None
        self._mcp_server: Optional[FastMCP] = None
        self._running = False
        self._services_initialized = False
        self._last_update_check: Optional[datetime] = None
        self._background_update_task: Optional[asyncio.Task] = None
        self._error_count = 0
        self._last_error: Optional[str] = None
        
        # Initialize services with cache hierarchy support
        self._documentation_service = DocumentationService()
        self._indexing_service = DocumentIndexingService()
        self._search_service = SearchService()
        # Wire the same indexing service instance to the search service
        self._search_service._indexing_service = self._indexing_service
        self._tool_registry = DocumentationToolRegistry(self._search_service)
        
        # Initialize health checker
        self._health_checker = HealthChecker(
            documentation_service=self._documentation_service,
            search_service=self._search_service,
            indexing_service=self._indexing_service
        )
        
        # Initialize FastMCP server
        self._mcp_server = FastMCP("Strands Documentation Search")
        
        # Register server info
        self._mcp_server.server_info = {
            "name": "strands-mcp-server",
            "version": "0.2.2",
            "description": "MCP server for Strands Agent SDK documentation search and project assistance"
        }
        
        # Register tools
        self._register_health_check()
        self._register_documentation_tools()
        
        logger.info(
            "Initialized Strands MCP Server with FastMCP",
            extra={
                "extra_fields": {
                    "operation": "server_init",
                    "component": "mcp_server",
                    "version": "0.2.1"
                }
            }
        )
    
    def _register_health_check(self) -> None:
        """Register health check tool."""
        
        @self._mcp_server.tool()
        async def health_check() -> ServerHealth:
            """Check server health status."""
            try:
                uptime = 0.0
                if self._start_time:
                    uptime = (datetime.now() - self._start_time).total_seconds()
                
                # Perform comprehensive health check
                system_health = await self._health_checker.perform_full_health_check()
                
                return ServerHealth(
                    status=system_health.overall_status,
                    timestamp=datetime.now(),
                    uptime_seconds=uptime,
                    components=[comp.to_dict() for comp in system_health.components],
                    error_count_24h=self._error_count,
                    last_error=self._last_error
                )
            except Exception as e:
                self._record_error(f"Health check failed: {e}")
                ErrorHandler.log_error(e, "health_check", "mcp_server")
                
                return ServerHealth(
                    status="unhealthy",
                    timestamp=datetime.now(),
                    uptime_seconds=uptime,
                    error_count_24h=self._error_count,
                    last_error=str(e)
                )
        
        @self._mcp_server.tool()
        async def readiness_check() -> Dict[str, Any]:
            """Check if server is ready to serve requests."""
            try:
                is_ready = await self._health_checker.check_readiness()
                return {
                    "ready": is_ready,
                    "timestamp": datetime.now().isoformat(),
                    "services_initialized": self._services_initialized
                }
            except Exception as e:
                self._record_error(f"Readiness check failed: {e}")
                ErrorHandler.log_error(e, "readiness_check", "mcp_server")
                return {
                    "ready": False,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
        
        @self._mcp_server.tool()
        async def liveness_check() -> Dict[str, Any]:
            """Check if server is alive and responsive."""
            try:
                is_alive = await self._health_checker.check_liveness()
                return {
                    "alive": is_alive,
                    "timestamp": datetime.now().isoformat(),
                    "running": self._running
                }
            except Exception as e:
                self._record_error(f"Liveness check failed: {e}")
                ErrorHandler.log_error(e, "liveness_check", "mcp_server")
                return {
                    "alive": False,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
    
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
            try:
                # Ensure services are initialized
                await self._ensure_services_initialized()
                
                tool = self._tool_registry.get_tool("search_documentation")
                arguments = {
                    "query": query,
                    "limit": limit,
                    "min_score": min_score
                }
                return await tool.execute(arguments)
            except Exception as e:
                self._record_error(f"Search documentation failed: {e}")
                ErrorHandler.log_error(
                    e, 
                    "search_documentation", 
                    "mcp_server",
                    extra_context={"query": query, "limit": limit, "min_score": min_score}
                )
                
                # Return user-friendly error
                error_info = ErrorHandler.create_user_friendly_error(e)
                raise StrandsMCPError(
                    message=f"Search failed: {e}",
                    error_code=error_info["error"],
                    user_message=error_info["message"],
                    details=error_info["details"]
                )
        
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
            try:
                # Ensure services are initialized
                await self._ensure_services_initialized()
                
                tool = self._tool_registry.get_tool("list_documentation")
                arguments = {
                    "section_filter": section_filter,
                    "limit": limit
                }
                return await tool.execute(arguments)
            except Exception as e:
                self._record_error(f"List documentation failed: {e}")
                ErrorHandler.log_error(
                    e, 
                    "list_documentation", 
                    "mcp_server",
                    extra_context={"section_filter": section_filter, "limit": limit}
                )
                
                # Return user-friendly error
                error_info = ErrorHandler.create_user_friendly_error(e)
                raise StrandsMCPError(
                    message=f"List documentation failed: {e}",
                    error_code=error_info["error"],
                    user_message=error_info["message"],
                    details=error_info["details"]
                )
    
    def _record_error(self, error_message: str) -> None:
        """Record an error for monitoring purposes."""
        self._error_count += 1
        self._last_error = error_message
        logger.error(
            f"Error recorded: {error_message}",
            extra={
                "extra_fields": {
                    "component": "mcp_server",
                    "error_count": self._error_count,
                    "operation": "error_recording"
                }
            }
        )
    
    @handle_errors("ensure_services_initialized", "mcp_server", reraise=False)
    async def _ensure_services_initialized(self) -> None:
        """Ensure services are initialized, initializing them if needed."""
        if self._services_initialized:
            return
        
        # Initialize services quickly (just load cache) with 5-second timeout for fast startup
        try:
            await asyncio.wait_for(self._initialize_services_fast(), timeout=5.0)
            
            # Start background cache update on first initialization
            if self._background_update_task is None:
                self._background_update_task = asyncio.create_task(self._background_cache_update())
                
        except asyncio.TimeoutError:
            self._record_error("Fast service initialization timed out")
            logger.warning(
                "Fast service initialization timed out - continuing with limited functionality",
                extra={
                    "extra_fields": {
                        "operation": "service_initialization",
                        "component": "mcp_server",
                        "timeout_seconds": 5.0
                    }
                }
            )
            self._services_initialized = True  # Allow server to continue
            # Still start background update
            if self._background_update_task is None:
                self._background_update_task = asyncio.create_task(self._background_cache_update())
        except Exception as e:
            self._record_error(f"Service initialization failed: {e}")
            ErrorHandler.log_error(e, "service_initialization", "mcp_server")
            self._services_initialized = True  # Allow server to continue
            # Still start background update
            if self._background_update_task is None:
                self._background_update_task = asyncio.create_task(self._background_cache_update())
    
    @handle_errors("initialize_services_fast", "mcp_server", reraise=False)
    async def _initialize_services_fast(self) -> None:
        """Initialize services with fast startup - prioritize loading existing cache/index."""
        try:
            logger.info(
                "Fast startup: loading existing cache/index",
                extra={
                    "extra_fields": {
                        "operation": "fast_startup",
                        "component": "mcp_server"
                    }
                }
            )
            
            # Step 1: Try to load existing search index first (fastest operation)
            index_loaded = await self._search_service.load_index()
            
            if index_loaded:
                stats = self._search_service.get_index_stats()
                logger.info(
                    f"Search index loaded: {stats['total_chunks']} chunks from {stats['unique_documents']} documents",
                    extra={
                        "extra_fields": {
                            "operation": "index_loaded",
                            "component": "mcp_server",
                            "chunk_count": stats['total_chunks'],
                            "document_count": stats['unique_documents']
                        }
                    }
                )
                self._services_initialized = True
                return
            
            # Step 2: Try cache hierarchy - user cache first, then bundled cache
            cached_chunks = await self._get_cached_docs_with_hierarchy()
            
            if cached_chunks:
                logger.info(
                    f"Building search index from {len(cached_chunks)} cached chunks",
                    extra={
                        "extra_fields": {
                            "operation": "build_index_from_cache",
                            "component": "mcp_server",
                            "chunk_count": len(cached_chunks)
                        }
                    }
                )
                # Build search index from cache (fast operation for reasonable cache sizes)
                documents = [
                    (chunk.content, chunk.title, chunk.source_url, chunk.file_path, chunk.last_modified)
                    for chunk in cached_chunks
                ]
                await self._indexing_service.index_documents(documents)
                await self._search_service.load_index()
                logger.info("Search index created from cache")
            else:
                logger.warning(
                    "No cached documentation found - server will have limited functionality until background update completes",
                    extra={
                        "extra_fields": {
                            "operation": "no_cache_found",
                            "component": "mcp_server"
                        }
                    }
                )
                
            self._services_initialized = True
                
        except Exception as e:
            self._record_error(f"Failed to initialize services: {e}")
            ErrorHandler.log_error(e, "initialize_services_fast", "mcp_server")
            # Don't fail startup - allow server to run with limited functionality
            self._services_initialized = True
    
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
            
            # Background cache update will be started on first tool call
            
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
    
    async def _get_cached_docs_with_hierarchy(self) -> Optional[List[DocumentChunk]]:
        """Get cached documentation using cache hierarchy: user cache → bundled cache → empty.
        
        Returns:
            List of cached document chunks, or None if no cache is available
        """
        # Step 1: Try user cache first
        logger.info("Checking user cache for documentation")
        user_cached_chunks = await self._documentation_service.get_cached_docs()
        
        if user_cached_chunks:
            logger.info(f"Found {len(user_cached_chunks)} chunks in user cache")
            return user_cached_chunks
        
        # Step 2: Try bundled cache and copy to user cache if available
        logger.info("User cache not found, checking bundled cache")
        bundled_cached_chunks = await self._get_bundled_cache()
        
        if bundled_cached_chunks:
            logger.info(f"Found {len(bundled_cached_chunks)} chunks in bundled cache")
            
            # Copy bundled cache to user cache for future use
            try:
                await self._copy_bundled_cache_to_user_cache()
                logger.info("Successfully copied bundled cache to user cache")
            except Exception as e:
                logger.warning(f"Failed to copy bundled cache to user cache: {e}")
            
            return bundled_cached_chunks
        
        # Step 3: No cache available
        logger.info("No cache found in hierarchy")
        return None
    
    async def _get_bundled_cache(self) -> Optional[List[DocumentChunk]]:
        """Get documentation from bundled cache (shipped with package).
        
        Returns:
            List of bundled document chunks, or None if bundled cache is not available
        """
        try:
            # Look for bundled cache in package data directory
            bundled_cache_path = self._get_bundled_cache_path() / 'index.json'
            
            if not bundled_cache_path.exists():
                logger.debug("No bundled cache found")
                return None
            
            logger.info(f"Loading bundled cache from {bundled_cache_path}")
            index = DocumentIndex.load_from_file(str(bundled_cache_path))
            logger.info(f"Loaded {len(index.chunks)} chunks from bundled cache")
            return index.chunks
            
        except Exception as e:
            logger.warning(f"Failed to load bundled cache: {e}")
            return None
    
    def _get_bundled_cache_path(self) -> Path:
        """Get the path to the bundled cache directory using modern importlib.resources API.
        
        This method uses the modern importlib.resources.files() API instead of the
        deprecated path() method, with proper fallback mechanisms for compatibility.
        
        Returns:
            Path to bundled cache directory
            
        Raises:
            StrandsMCPError: If resource access fails completely
        """
        try:
            # Try modern importlib.resources.files() first (Python 3.9+)
            try:
                import importlib.resources as resources
                
                # Use files() instead of deprecated path()
                if hasattr(resources, 'files'):
                    try:
                        # Get the package files reference
                        package_files = resources.files('strands_mcp.data')
                        cache_files = package_files / 'cache'
                        
                        # For packaged installations, we need to extract to a temporary location
                        # if the resource is inside a zip file
                        if hasattr(cache_files, 'is_file') and not cache_files.is_dir():
                            # Resource is in a zip file, need to use as_file context manager
                            # Create a temporary directory for extracted resources
                            temp_dir = Path(tempfile.mkdtemp(prefix='strands_mcp_cache_'))
                            
                            # Extract all cache files to temp directory
                            try:
                                for item in cache_files.iterdir():
                                    if item.is_file():
                                        with item.open('rb') as src:
                                            dest_file = temp_dir / item.name
                                            with open(dest_file, 'wb') as dst:
                                                shutil.copyfileobj(src, dst)
                                
                                logger.debug(f"Extracted bundled cache to temporary directory: {temp_dir}")
                                return temp_dir
                            except Exception as extract_error:
                                logger.warning(f"Failed to extract bundled cache: {extract_error}")
                                # Clean up temp directory on failure
                                if temp_dir.exists():
                                    shutil.rmtree(temp_dir, ignore_errors=True)
                                raise
                        else:
                            # Resource is accessible as a regular directory
                            # Convert Traversable to Path
                            if hasattr(cache_files, '__fspath__'):
                                return Path(cache_files)
                            else:
                                # For development environments, resolve to actual path
                                return Path(str(cache_files))
                                
                    except (FileNotFoundError, AttributeError) as e:
                        logger.debug(f"Modern importlib.resources.files() failed: {e}")
                        raise
                        
                else:
                    # files() not available, try deprecated path() method
                    logger.debug("files() not available, trying deprecated path() method")
                    raise AttributeError("files() method not available")
                    
            except (ImportError, AttributeError, FileNotFoundError) as modern_error:
                logger.debug(f"Modern importlib.resources approach failed: {modern_error}")
                
                # Try deprecated importlib_resources.path() as fallback
                try:
                    import importlib_resources
                    if hasattr(importlib_resources, 'files'):
                        # Use backport's files() method
                        package_files = importlib_resources.files('strands_mcp.data')
                        cache_path = package_files / 'cache'
                        return Path(str(cache_path))
                    else:
                        # Use deprecated path() method from backport
                        with importlib_resources.path('strands_mcp.data', 'cache') as cache_path:
                            return Path(cache_path)
                except (ImportError, FileNotFoundError) as backport_error:
                    logger.debug(f"importlib_resources backport failed: {backport_error}")
                    pass
            
            # Try pkg_resources as fallback for older environments
            try:
                import pkg_resources
                cache_path = pkg_resources.resource_filename('strands_mcp', 'data/cache')
                resolved_path = Path(cache_path)
                
                # Verify the path exists or can be created
                if resolved_path.exists() or resolved_path.parent.exists():
                    logger.debug(f"Using pkg_resources path: {resolved_path}")
                    return resolved_path
                else:
                    logger.warning(f"pkg_resources path does not exist: {resolved_path}")
                    raise FileNotFoundError(f"pkg_resources path not found: {resolved_path}")
                    
            except (ImportError, FileNotFoundError) as pkg_error:
                logger.debug(f"pkg_resources fallback failed: {pkg_error}")
                pass
            
            # Final fallback to relative path (development environment)
            fallback_path = Path(__file__).parent / 'data' / 'cache'
            logger.debug(f"Using fallback relative path: {fallback_path}")
            return fallback_path
            
        except Exception as e:
            error_msg = f"Failed to resolve bundled cache path: {e}"
            logger.error(error_msg)
            
            # Try one last fallback
            try:
                fallback_path = Path(__file__).parent / 'data' / 'cache'
                logger.warning(f"Using emergency fallback path: {fallback_path}")
                return fallback_path
            except Exception as fallback_error:
                # Complete failure - raise a user-friendly error
                raise StrandsMCPError(
                    message="Cannot access bundled cache resources",
                    error_code="RESOURCE_ACCESS_ERROR",
                    user_message="Unable to locate bundled documentation cache. Please check installation.",
                    details={
                        "original_error": str(e),
                        "fallback_error": str(fallback_error),
                        "attempted_methods": ["importlib.resources.files()", "importlib_resources", "pkg_resources", "relative_path"]
                    }
                )
    
    async def _copy_bundled_cache_to_user_cache(self) -> None:
        """Copy bundled cache to user cache directory for future use.
        
        This enables faster startup on subsequent runs by having a local copy
        of the bundled cache that can be updated independently.
        """
        try:
            import shutil
            
            # Get bundled cache directory
            bundled_cache_dir = self._get_bundled_cache_path()
            
            if not bundled_cache_dir.exists():
                logger.debug("No bundled cache directory to copy")
                return
            
            # Get user cache directory
            user_cache_dir = self._documentation_service.cache_dir
            
            logger.info(
                f"Copying bundled cache from {bundled_cache_dir} to {user_cache_dir}",
                extra={
                    "extra_fields": {
                        "operation": "copy_bundled_cache",
                        "component": "mcp_server",
                        "source": str(bundled_cache_dir),
                        "destination": str(user_cache_dir)
                    }
                }
            )
            
            # Ensure user cache directory exists
            user_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from bundled cache to user cache
            for item in bundled_cache_dir.iterdir():
                if item.is_file():
                    dest_file = user_cache_dir / item.name
                    shutil.copy2(item, dest_file)
                    logger.debug(f"Copied {item.name} to user cache")
                elif item.is_dir():
                    dest_dir = user_cache_dir / item.name
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(item, dest_dir)
                    logger.debug(f"Copied directory {item.name} to user cache")
            
            logger.info(
                "Successfully copied bundled cache to user cache",
                extra={
                    "extra_fields": {
                        "operation": "copy_bundled_cache_complete",
                        "component": "mcp_server"
                    }
                }
            )
            
        except Exception as e:
            logger.error(
                f"Failed to copy bundled cache to user cache: {e}",
                extra={
                    "extra_fields": {
                        "operation": "copy_bundled_cache_error",
                        "component": "mcp_server",
                        "error": str(e)
                    }
                }
            )
            raise
    
    async def _background_cache_update(self) -> None:
        """Update documentation cache in the background."""
        try:
            # Wait a bit to let the server fully start
            await asyncio.sleep(2)
            
            logger.info("Starting background documentation cache update")
            
            # If services aren't initialized yet, try to initialize them first
            if not self._services_initialized:
                logger.info("Services not initialized, attempting initialization in background")
                try:
                    await self._initialize_services_fast()
                except Exception as e:
                    logger.warning(f"Background service initialization failed: {e}")
            
            # Check if we need to update documentation
            if self._should_check_for_updates():
                logger.info("Checking for documentation updates in background")
                updates_available = await self._documentation_service.check_for_updates()
                
                if updates_available:
                    logger.info("Documentation updates available, fetching in background")
                    await self._update_documentation()
                    logger.info("Background documentation update completed")
                else:
                    logger.info("Documentation is up to date")
            else:
                logger.info("Skipping background update check (checked recently)")
                
        except Exception as e:
            logger.error(f"Background cache update failed: {e}")
            # Don't crash the server - this is non-critical
    
    async def _cleanup_services(self) -> None:
        """Clean up services and resources."""
        try:
            # Cancel background update task if running
            if self._background_update_task and not self._background_update_task.done():
                logger.info("Cancelling background update task")
                self._background_update_task.cancel()
                try:
                    await self._background_update_task
                except asyncio.CancelledError:
                    pass
            
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