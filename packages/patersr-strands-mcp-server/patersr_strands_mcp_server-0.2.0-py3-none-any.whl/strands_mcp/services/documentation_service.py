"""Documentation service for fetching and managing Strands SDK docs."""

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import httpx
import aiofiles
from ..models.documentation import DocumentChunk, DocumentIndex
from ..utils.file_utils import CacheManager, MarkdownFileManager, ensure_directory_exists
from ..utils.error_handler import ErrorHandler, handle_errors, retry_with_backoff
from ..utils.errors import NetworkError, CacheError, ConfigurationError


logger = logging.getLogger(__name__)


class DocumentationService:
    """Service for fetching and managing Strands SDK documentation from GitHub."""
    
    def __init__(
        self,
        cache_dir: str = "data/docs",
        github_repo: str = "strands-agents/docs",
        github_branch: str = "main",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        cache_ttl_hours: int = 24,
        max_cache_size_mb: int = 500,
    ):
        """Initialize the documentation service.
        
        Args:
            cache_dir: Directory to store cached documentation
            github_repo: GitHub repository in format "owner/repo"
            github_branch: Branch to fetch from
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay for exponential backoff (seconds)
            cache_ttl_hours: Cache TTL in hours
            max_cache_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.github_repo = github_repo
        self.github_branch = github_branch
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        # Set up bundled cache directory (read-only, ships with package)
        self.bundled_cache_dir = Path(__file__).parent.parent / "data" / "cache"
        
        # GitHub API URLs
        self.api_base = "https://api.github.com"
        self.contents_url = f"{self.api_base}/repos/{github_repo}/contents"
        self.raw_base = f"https://raw.githubusercontent.com/{github_repo}/{github_branch}"
        
        # Initialize cache manager
        self.cache_manager = CacheManager(
            cache_dir=cache_dir,
            default_ttl_hours=cache_ttl_hours,
            max_cache_size_mb=max_cache_size_mb
        )
        
        # Initialize file manager
        self.file_manager = MarkdownFileManager()
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # HTTP client with reasonable timeouts and GitHub authentication
        headers = {}
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            logger.info("Using GitHub token for API authentication")
        else:
            logger.warning("No GitHub token found - API requests will be rate limited")
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            headers=headers
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0,
        exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def _make_github_request(self, operation, *args, **kwargs):
        """Execute GitHub API operation with retry logic.
        
        Args:
            operation: Async function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            NetworkError: If all retries fail
        """
        try:
            return await operation(*args, **kwargs)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Convert to our custom error type
            status_code = getattr(e, 'response', {}).get('status_code')
            url = str(getattr(e, 'request', {}).get('url', 'unknown'))
            
            raise NetworkError(
                message=f"GitHub API request failed: {e}",
                url=url,
                status_code=status_code,
                details={"original_error": str(e)}
            )
    
    @handle_errors("fetch_github_contents", "documentation_service")
    async def _fetch_github_contents(self, path: str = "") -> List[Dict]:
        """Fetch contents of a directory from GitHub API.
        
        Args:
            path: Path within the repository
            
        Returns:
            List of file/directory information
        """
        url = f"{self.contents_url}/{path}" if path else self.contents_url
        params = {"ref": self.github_branch}
        
        async def _make_request():
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
        return await self._make_github_request(_make_request)
    
    @handle_errors("fetch_file_content", "documentation_service")
    async def _fetch_file_content(self, file_path: str) -> str:
        """Fetch content of a specific file from GitHub.
        
        Args:
            file_path: Path to the file in the repository
            
        Returns:
            File content as string
        """
        url = f"{self.raw_base}/{file_path}"
        
        async def _make_request():
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        
        return await self._make_github_request(_make_request)
    
    async def _get_file_last_modified(self, file_path: str) -> datetime:
        """Get last modified timestamp for a file from GitHub API.
        
        Args:
            file_path: Path to the file in the repository
            
        Returns:
            Last modified timestamp
        """
        url = f"{self.api_base}/repos/{self.github_repo}/commits"
        params = {
            "path": file_path,
            "per_page": 1,
            "sha": self.github_branch
        }
        
        async def _make_request():
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            commits = response.json()
            if commits:
                commit_date = commits[0]["commit"]["committer"]["date"]
                return datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
            return datetime.now(timezone.utc)
        
        return await self._exponential_backoff_retry(_make_request)
    
    async def _discover_markdown_files(self, path: str = "") -> List[str]:
        """Recursively discover all markdown files in the repository.
        
        Args:
            path: Starting path for discovery
            
        Returns:
            List of markdown file paths
        """
        markdown_files = []
        
        try:
            contents = await self._fetch_github_contents(path)
            
            for item in contents:
                if item["type"] == "file" and item["name"].endswith(".md"):
                    markdown_files.append(item["path"])
                elif item["type"] == "dir":
                    # Recursively search subdirectories
                    subdir_files = await self._discover_markdown_files(item["path"])
                    markdown_files.extend(subdir_files)
        except Exception as e:
            logger.error(f"Error discovering files in {path}: {e}")
        
        return markdown_files
    
    @handle_errors("fetch_latest_docs", "documentation_service")
    async def fetch_latest_docs(self) -> List[DocumentChunk]:
        """Fetch the latest documentation from GitHub.
        
        Returns:
            List of document chunks with content and metadata
        """
        logger.info(
            f"Fetching latest documentation from {self.github_repo}",
            extra={
                "extra_fields": {
                    "operation": "fetch_latest_docs",
                    "component": "documentation_service",
                    "repo": self.github_repo,
                    "branch": self.github_branch
                }
            }
        )
        
        try:
            # Discover all markdown files
            markdown_files = await self._discover_markdown_files()
            logger.info(
                f"Found {len(markdown_files)} markdown files",
                extra={
                    "extra_fields": {
                        "operation": "discover_files",
                        "component": "documentation_service",
                        "file_count": len(markdown_files)
                    }
                }
            )
            
            chunks = []
            failed_files = []
            
            # Process each markdown file
            for file_path in markdown_files:
                try:
                    # Fetch file content and metadata
                    content = await self._fetch_file_content(file_path)
                    last_modified = await self._get_file_last_modified(file_path)
                    
                    # Create local cache path
                    local_path = self.cache_dir / file_path
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save to local cache
                    async with aiofiles.open(local_path, 'w', encoding='utf-8') as f:
                        await f.write(content)
                    
                    # Create document chunk
                    chunk = DocumentChunk(
                        id=f"{self.github_repo}:{file_path}",
                        title=self._extract_title_from_content(content, file_path),
                        content=content,
                        source_url=f"https://github.com/{self.github_repo}/blob/{self.github_branch}/{file_path}",
                        section=self._extract_section_from_path(file_path),
                        file_path=str(local_path),
                        last_modified=last_modified
                    )
                    
                    chunks.append(chunk)
                    logger.debug(f"Processed {file_path}")
                    
                except Exception as e:
                    failed_files.append(file_path)
                    ErrorHandler.log_error(
                        e, 
                        "process_file", 
                        "documentation_service",
                        extra_context={"file_path": file_path}
                    )
                    continue
            
            if failed_files:
                logger.warning(
                    f"Failed to process {len(failed_files)} files",
                    extra={
                        "extra_fields": {
                            "operation": "fetch_latest_docs",
                            "component": "documentation_service",
                            "failed_files": failed_files[:10],  # Log first 10 failed files
                            "failed_count": len(failed_files)
                        }
                    }
                )
            
            logger.info(
                f"Successfully fetched {len(chunks)} document chunks",
                extra={
                    "extra_fields": {
                        "operation": "fetch_latest_docs",
                        "component": "documentation_service",
                        "success_count": len(chunks),
                        "failed_count": len(failed_files)
                    }
                }
            )
            return chunks
            
        except Exception as e:
            ErrorHandler.log_error(e, "fetch_latest_docs", "documentation_service")
            raise
    
    def _extract_title_from_content(self, content: str, file_path: str) -> str:
        """Extract title from markdown content or file path.
        
        Args:
            content: Markdown content
            file_path: Path to the file
            
        Returns:
            Document title
        """
        lines = content.split('\n')
        
        # Look for first H1 heading
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to filename without extension
        return Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
    
    def _extract_section_from_path(self, file_path: str) -> str:
        """Extract section name from file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Section name
        """
        path_parts = Path(file_path).parts
        if len(path_parts) > 1:
            return path_parts[0].replace('-', ' ').replace('_', ' ').title()
        return "General"
    
    async def check_for_updates(self) -> bool:
        """Check if remote documentation has been updated since last fetch.
        
        Returns:
            True if updates are available, False otherwise
        """
        logger.info("Checking for documentation updates")
        
        try:
            # Get the latest commit for the docs repository
            url = f"{self.api_base}/repos/{self.github_repo}/commits/{self.github_branch}"
            
            async def _make_request():
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
            
            commit_info = await self._exponential_backoff_retry(_make_request)
            remote_last_modified = datetime.fromisoformat(
                commit_info["commit"]["committer"]["date"].replace("Z", "+00:00")
            )
            
            # Check if we have a local index with timestamp
            index_file = self.cache_dir / "index.json"
            if not index_file.exists():
                logger.info("No local index found, updates needed")
                return True
            
            try:
                local_index = DocumentIndex.load_from_file(str(index_file))
                local_last_updated = local_index.last_updated
                
                if remote_last_modified > local_last_updated:
                    logger.info(f"Updates available: remote={remote_last_modified}, local={local_last_updated}")
                    return True
                else:
                    logger.info("Documentation is up to date")
                    return False
                    
            except Exception as e:
                logger.warning(f"Error reading local index: {e}")
                return True
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            # If we can't check for updates, assume we need them
            return True
    
    async def get_cached_docs(self) -> Optional[List[DocumentChunk]]:
        """Get documentation from cache using hierarchy: user cache → bundled cache → None.
        
        Returns:
            List of cached document chunks, or None if no cache is available
        """
        # Try user cache first
        user_cache_chunks = await self._get_user_cached_docs()
        if user_cache_chunks is not None:
            logger.info(f"Loaded {len(user_cache_chunks)} chunks from user cache")
            return user_cache_chunks
        
        # Fall back to bundled cache
        bundled_cache_chunks = await self._get_bundled_cached_docs()
        if bundled_cache_chunks is not None:
            logger.info(f"Loaded {len(bundled_cache_chunks)} chunks from bundled cache")
            return bundled_cache_chunks
        
        logger.info("No cached documentation found in user or bundled cache")
        return None
    
    async def _get_user_cached_docs(self) -> Optional[List[DocumentChunk]]:
        """Get documentation from user cache.
        
        Returns:
            List of cached document chunks, or None if cache is invalid
        """
        index_file = self.cache_dir / "index.json"
        
        if not index_file.exists():
            logger.debug("No user cache documentation index found")
            return None
        
        try:
            index = DocumentIndex.load_from_file(str(index_file))
            logger.debug(f"Loaded {len(index.chunks)} cached document chunks from user cache")
            return index.chunks
        except Exception as e:
            logger.error(f"Error loading user cached documentation: {e}")
            return None
    
    async def _get_bundled_cached_docs(self) -> Optional[List[DocumentChunk]]:
        """Get documentation from bundled cache (read-only, ships with package).
        
        Returns:
            List of cached document chunks, or None if bundled cache is invalid
        """
        bundled_index_file = self.bundled_cache_dir / "index.json"
        
        if not bundled_index_file.exists():
            logger.debug("No bundled cache documentation index found")
            return None
        
        try:
            index = DocumentIndex.load_from_file(str(bundled_index_file))
            logger.debug(f"Loaded {len(index.chunks)} cached document chunks from bundled cache")
            return index.chunks
        except Exception as e:
            logger.error(f"Error loading bundled cached documentation: {e}")
            return None
    
    async def save_docs_to_cache(self, chunks: List[DocumentChunk]) -> None:
        """Save document chunks to local cache.
        
        Args:
            chunks: List of document chunks to cache
        """
        index = DocumentIndex(
            version="1.0",
            last_updated=datetime.now(timezone.utc),
            chunks=chunks,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # Default model
        )
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        index_file = self.cache_dir / "index.json"
        index.save_to_file(str(index_file))
        
        # Add to cache manager
        await self.cache_manager.add_to_cache(
            cache_key="documentation_index",
            file_path=index_file,
            metadata={
                "repo": self.github_repo,
                "branch": self.github_branch,
                "chunk_count": len(chunks)
            }
        )
        
        logger.info(f"Saved {len(chunks)} document chunks to cache")
    
    async def is_cache_valid(self) -> bool:
        """Check if the documentation cache is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        return await self.cache_manager.is_cache_valid("documentation_index")
    
    async def invalidate_cache(self) -> bool:
        """Invalidate the documentation cache.
        
        Returns:
            True if cache was invalidated, False if not found
        """
        logger.info("Invalidating documentation cache")
        return await self.cache_manager.remove_from_cache("documentation_index")
    
    async def cleanup_cache(self) -> int:
        """Clean up expired cache items.
        
        Returns:
            Number of items removed
        """
        logger.info("Cleaning up documentation cache")
        expired_count = await self.cache_manager.cleanup_expired_items()
        size_count = await self.cache_manager.cleanup_by_size()
        return expired_count + size_count
    
    async def get_cache_info(self) -> Dict:
        """Get information about the current cache state.
        
        Returns:
            Dictionary with cache information
        """
        cache_size = await self.cache_manager.get_cache_size_mb()
        cache_valid = await self.is_cache_valid()
        
        # User cache info
        user_index_file = self.cache_dir / "index.json"
        user_index_exists = user_index_file.exists()
        
        # Bundled cache info
        bundled_index_file = self.bundled_cache_dir / "index.json"
        bundled_index_exists = bundled_index_file.exists()
        
        info = {
            "cache_size_mb": round(cache_size, 2),
            "cache_valid": cache_valid,
            "user_cache": {
                "index_exists": user_index_exists,
                "cache_dir": str(self.cache_dir)
            },
            "bundled_cache": {
                "index_exists": bundled_index_exists,
                "cache_dir": str(self.bundled_cache_dir)
            },
            "max_cache_size_mb": self.cache_manager.max_cache_size_mb,
            "ttl_hours": self.cache_manager.default_ttl_hours
        }
        
        # Add user cache details if available
        if user_index_exists:
            try:
                index = DocumentIndex.load_from_file(str(user_index_file))
                info["user_cache"].update({
                    "chunk_count": len(index.chunks),
                    "last_updated": index.last_updated.isoformat(),
                    "version": index.version,
                    "embedding_model": index.embedding_model
                })
            except Exception as e:
                logger.error(f"Error reading user cache index for cache info: {e}")
        
        # Add bundled cache details if available
        if bundled_index_exists:
            try:
                index = DocumentIndex.load_from_file(str(bundled_index_file))
                info["bundled_cache"].update({
                    "chunk_count": len(index.chunks),
                    "last_updated": index.last_updated.isoformat(),
                    "version": index.version,
                    "embedding_model": index.embedding_model
                })
            except Exception as e:
                logger.error(f"Error reading bundled cache index for cache info: {e}")
        
        return info
    
    async def clear_cache(self) -> int:
        """Clear all cached documentation.
        
        Returns:
            Number of items removed
        """
        logger.info("Clearing all documentation cache")
        return await self.cache_manager.clear_cache()