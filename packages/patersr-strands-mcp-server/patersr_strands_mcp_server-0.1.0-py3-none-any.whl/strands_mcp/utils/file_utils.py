"""File system utilities for documentation caching and management."""

import asyncio
import json
import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union
import aiofiles
import aiofiles.os


logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local file cache with version tracking and TTL."""
    
    def __init__(
        self,
        cache_dir: Union[str, Path],
        default_ttl_hours: int = 24,
        max_cache_size_mb: int = 500
    ):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cached files
            default_ttl_hours: Default TTL for cached items in hours
            max_cache_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_hours = default_ttl_hours
        self.max_cache_size_mb = max_cache_size_mb
        self.metadata_file = self.cache_dir / ".cache_metadata.json"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_cache_metadata(self) -> Dict:
        """Get cache metadata from disk.
        
        Returns:
            Cache metadata dictionary
        """
        if not self.metadata_file.exists():
            return {
                "version": "1.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "last_cleanup": datetime.now(timezone.utc).isoformat(),
                "items": {}
            }
        
        try:
            async with aiofiles.open(self.metadata_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error reading cache metadata: {e}")
            return {
                "version": "1.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "last_cleanup": datetime.now(timezone.utc).isoformat(),
                "items": {}
            }
    
    async def save_cache_metadata(self, metadata: Dict) -> None:
        """Save cache metadata to disk.
        
        Args:
            metadata: Cache metadata dictionary
        """
        try:
            async with aiofiles.open(self.metadata_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error saving cache metadata: {e}")
    
    async def is_cache_valid(self, cache_key: str, ttl_hours: Optional[int] = None) -> bool:
        """Check if a cached item is still valid.
        
        Args:
            cache_key: Unique identifier for the cached item
            ttl_hours: TTL in hours, uses default if None
            
        Returns:
            True if cache is valid, False otherwise
        """
        metadata = await self.get_cache_metadata()
        
        if cache_key not in metadata["items"]:
            return False
        
        item_info = metadata["items"][cache_key]
        cached_time = datetime.fromisoformat(item_info["cached_at"])
        ttl = ttl_hours or self.default_ttl_hours
        
        expiry_time = cached_time + timedelta(hours=ttl)
        return datetime.now(timezone.utc) < expiry_time
    
    async def add_to_cache(
        self,
        cache_key: str,
        file_path: Union[str, Path],
        metadata: Optional[Dict] = None,
        ttl_hours: Optional[int] = None
    ) -> None:
        """Add an item to the cache with metadata.
        
        Args:
            cache_key: Unique identifier for the cached item
            file_path: Path to the cached file
            metadata: Additional metadata for the cached item
            ttl_hours: TTL in hours, uses default if None
        """
        cache_metadata = await self.get_cache_metadata()
        
        # Get file size
        file_path = Path(file_path)
        file_size = 0
        if file_path.exists():
            stat = await aiofiles.os.stat(file_path)
            file_size = stat.st_size
        
        cache_metadata["items"][cache_key] = {
            "file_path": str(file_path),
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "ttl_hours": ttl_hours or self.default_ttl_hours,
            "file_size": file_size,
            "metadata": metadata or {}
        }
        
        await self.save_cache_metadata(cache_metadata)
    
    async def remove_from_cache(self, cache_key: str) -> bool:
        """Remove an item from the cache.
        
        Args:
            cache_key: Unique identifier for the cached item
            
        Returns:
            True if item was removed, False if not found
        """
        cache_metadata = await self.get_cache_metadata()
        
        if cache_key not in cache_metadata["items"]:
            return False
        
        item_info = cache_metadata["items"][cache_key]
        file_path = Path(item_info["file_path"])
        
        # Remove file if it exists
        if file_path.exists():
            try:
                await aiofiles.os.remove(file_path)
            except Exception as e:
                logger.warning(f"Error removing cached file {file_path}: {e}")
        
        # Remove from metadata
        del cache_metadata["items"][cache_key]
        await self.save_cache_metadata(cache_metadata)
        
        return True
    
    async def get_cache_size_mb(self) -> float:
        """Get total cache size in megabytes.
        
        Returns:
            Cache size in MB
        """
        total_size = 0
        
        try:
            for item in self.cache_dir.rglob("*"):
                if item.is_file() and item.name != ".cache_metadata.json":
                    stat = await aiofiles.os.stat(item)
                    total_size += stat.st_size
        except Exception as e:
            logger.error(f"Error calculating cache size: {e}")
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def cleanup_expired_items(self) -> int:
        """Remove expired items from cache.
        
        Returns:
            Number of items removed
        """
        cache_metadata = await self.get_cache_metadata()
        expired_keys = []
        
        for cache_key, item_info in cache_metadata["items"].items():
            cached_time = datetime.fromisoformat(item_info["cached_at"])
            ttl_hours = item_info.get("ttl_hours", self.default_ttl_hours)
            expiry_time = cached_time + timedelta(hours=ttl_hours)
            
            if datetime.now(timezone.utc) >= expiry_time:
                expired_keys.append(cache_key)
        
        # Remove expired items
        removed_count = 0
        for cache_key in expired_keys:
            if await self.remove_from_cache(cache_key):
                removed_count += 1
        
        # Update last cleanup time
        cache_metadata = await self.get_cache_metadata()
        cache_metadata["last_cleanup"] = datetime.now(timezone.utc).isoformat()
        await self.save_cache_metadata(cache_metadata)
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired cache items")
        
        return removed_count
    
    async def cleanup_by_size(self) -> int:
        """Remove oldest items if cache exceeds size limit.
        
        Returns:
            Number of items removed
        """
        current_size = await self.get_cache_size_mb()
        
        if current_size <= self.max_cache_size_mb:
            return 0
        
        cache_metadata = await self.get_cache_metadata()
        
        # Sort items by cached_at timestamp (oldest first)
        items_by_age = sorted(
            cache_metadata["items"].items(),
            key=lambda x: x[1]["cached_at"]
        )
        
        removed_count = 0
        for cache_key, _ in items_by_age:
            if await self.remove_from_cache(cache_key):
                removed_count += 1
                current_size = await self.get_cache_size_mb()
                
                if current_size <= self.max_cache_size_mb:
                    break
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} items to reduce cache size")
        
        return removed_count
    
    async def clear_cache(self) -> int:
        """Clear all cached items.
        
        Returns:
            Number of items removed
        """
        cache_metadata = await self.get_cache_metadata()
        item_count = len(cache_metadata["items"])
        
        # Remove all files
        try:
            for item in self.cache_dir.rglob("*"):
                if item.is_file() and item.name != ".cache_metadata.json":
                    await aiofiles.os.remove(item)
        except Exception as e:
            logger.error(f"Error clearing cache files: {e}")
        
        # Reset metadata
        cache_metadata["items"] = {}
        cache_metadata["last_cleanup"] = datetime.now(timezone.utc).isoformat()
        await self.save_cache_metadata(cache_metadata)
        
        logger.info(f"Cleared {item_count} items from cache")
        return item_count


class MarkdownFileManager:
    """Utilities for reading and writing markdown files."""
    
    @staticmethod
    async def read_markdown_file(file_path: Union[str, Path]) -> str:
        """Read content from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            raise IOError(f"Error reading markdown file {file_path}: {e}")
    
    @staticmethod
    async def write_markdown_file(
        file_path: Union[str, Path],
        content: str,
        create_dirs: bool = True
    ) -> None:
        """Write content to a markdown file.
        
        Args:
            file_path: Path to the markdown file
            content: Content to write
            create_dirs: Whether to create parent directories
            
        Raises:
            IOError: If file cannot be written
        """
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
        except Exception as e:
            raise IOError(f"Error writing markdown file {file_path}: {e}")
    
    @staticmethod
    async def list_markdown_files(directory: Union[str, Path]) -> List[Path]:
        """List all markdown files in a directory recursively.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of markdown file paths
        """
        directory = Path(directory)
        markdown_files = []
        
        if not directory.exists():
            return markdown_files
        
        try:
            for item in directory.rglob("*.md"):
                if item.is_file():
                    markdown_files.append(item)
        except Exception as e:
            logger.error(f"Error listing markdown files in {directory}: {e}")
        
        return sorted(markdown_files)
    
    @staticmethod
    async def get_file_metadata(file_path: Union[str, Path]) -> Dict:
        """Get metadata for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {}
        
        try:
            stat = await aiofiles.os.stat(file_path)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                "name": file_path.name,
                "stem": file_path.stem,
                "suffix": file_path.suffix,
                "parent": str(file_path.parent)
            }
        except Exception as e:
            logger.error(f"Error getting file metadata for {file_path}: {e}")
            return {}


async def ensure_directory_exists(directory: Union[str, Path]) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)


async def safe_remove_file(file_path: Union[str, Path]) -> bool:
    """Safely remove a file, ignoring errors if file doesn't exist.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        True if file was removed or didn't exist, False on error
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return True
    
    try:
        await aiofiles.os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error removing file {file_path}: {e}")
        return False


async def safe_remove_directory(directory: Union[str, Path]) -> bool:
    """Safely remove a directory and its contents.
    
    Args:
        directory: Directory path to remove
        
    Returns:
        True if directory was removed or didn't exist, False on error
    """
    directory = Path(directory)
    
    if not directory.exists():
        return True
    
    try:
        shutil.rmtree(directory)
        return True
    except Exception as e:
        logger.error(f"Error removing directory {directory}: {e}")
        return False