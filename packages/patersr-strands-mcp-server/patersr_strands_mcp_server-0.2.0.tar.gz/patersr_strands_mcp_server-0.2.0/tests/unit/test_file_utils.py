"""Tests for file utilities and cache management."""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

from src.strands_mcp.utils.file_utils import (
    CacheManager,
    MarkdownFileManager,
    ensure_directory_exists,
    safe_remove_file,
    safe_remove_directory
)


class TestCacheManager:
    """Test cases for CacheManager."""
    
    @pytest_asyncio.fixture
    async def cache_manager(self):
        """Create a temporary cache manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CacheManager(
                cache_dir=temp_dir,
                default_ttl_hours=1,
                max_cache_size_mb=1
            )
            yield manager
    
    @pytest_asyncio.fixture
    async def sample_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document.")
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_cache_metadata_creation(self, cache_manager):
        """Test cache metadata creation."""
        metadata = await cache_manager.get_cache_metadata()
        
        assert metadata["version"] == "1.0"
        assert "created" in metadata
        assert "last_cleanup" in metadata
        assert metadata["items"] == {}
    
    @pytest.mark.asyncio
    async def test_add_to_cache(self, cache_manager, sample_file):
        """Test adding items to cache."""
        cache_key = "test_doc"
        
        await cache_manager.add_to_cache(
            cache_key=cache_key,
            file_path=sample_file,
            metadata={"type": "test"},
            ttl_hours=2
        )
        
        metadata = await cache_manager.get_cache_metadata()
        assert cache_key in metadata["items"]
        
        item = metadata["items"][cache_key]
        assert item["file_path"] == str(sample_file)
        assert item["ttl_hours"] == 2
        assert item["metadata"]["type"] == "test"
        assert item["file_size"] > 0
    
    @pytest.mark.asyncio
    async def test_cache_validity(self, cache_manager, sample_file):
        """Test cache validity checking."""
        cache_key = "test_doc"
        
        # Item not in cache should be invalid
        assert not await cache_manager.is_cache_valid(cache_key)
        
        # Add item with short TTL
        await cache_manager.add_to_cache(
            cache_key=cache_key,
            file_path=sample_file,
            ttl_hours=1
        )
        
        # Should be valid immediately
        assert await cache_manager.is_cache_valid(cache_key)
        
        # Mock time to simulate expiry
        with patch('src.strands_mcp.utils.file_utils.datetime') as mock_datetime:
            future_time = datetime.now(timezone.utc) + timedelta(hours=2)
            mock_datetime.now.return_value = future_time
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            assert not await cache_manager.is_cache_valid(cache_key)
    
    @pytest.mark.asyncio
    async def test_remove_from_cache(self, cache_manager, sample_file):
        """Test removing items from cache."""
        cache_key = "test_doc"
        
        # Add item to cache
        await cache_manager.add_to_cache(cache_key, sample_file)
        assert await cache_manager.is_cache_valid(cache_key)
        
        # Remove item
        result = await cache_manager.remove_from_cache(cache_key)
        assert result is True
        assert not await cache_manager.is_cache_valid(cache_key)
        
        # Try to remove non-existent item
        result = await cache_manager.remove_from_cache("non_existent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_items(self, cache_manager, sample_file):
        """Test cleanup of expired cache items."""
        cache_key = "test_doc"
        
        # Add item with short TTL
        await cache_manager.add_to_cache(
            cache_key=cache_key,
            file_path=sample_file,
            ttl_hours=1
        )
        
        # Mock time to simulate expiry
        with patch('src.strands_mcp.utils.file_utils.datetime') as mock_datetime:
            future_time = datetime.now(timezone.utc) + timedelta(hours=2)
            mock_datetime.now.return_value = future_time
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            removed_count = await cache_manager.cleanup_expired_items()
            assert removed_count == 1
            assert not await cache_manager.is_cache_valid(cache_key)
    
    @pytest.mark.asyncio
    async def test_cache_size_calculation(self, cache_manager, sample_file):
        """Test cache size calculation."""
        initial_size = await cache_manager.get_cache_size_mb()
        
        # Copy the sample file to the cache directory
        cache_file = cache_manager.cache_dir / "test_doc.md"
        await MarkdownFileManager.write_markdown_file(cache_file, "# Test Document\n\nThis is a test document.")
        
        await cache_manager.add_to_cache("test_doc", cache_file)
        
        final_size = await cache_manager.get_cache_size_mb()
        assert final_size > initial_size
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, cache_manager, sample_file):
        """Test clearing all cache items."""
        # Add multiple items
        await cache_manager.add_to_cache("doc1", sample_file)
        await cache_manager.add_to_cache("doc2", sample_file)
        
        metadata = await cache_manager.get_cache_metadata()
        assert len(metadata["items"]) == 2
        
        # Clear cache
        removed_count = await cache_manager.clear_cache()
        assert removed_count == 2
        
        metadata = await cache_manager.get_cache_metadata()
        assert len(metadata["items"]) == 0


class TestMarkdownFileManager:
    """Test cases for MarkdownFileManager."""
    
    @pytest_asyncio.fixture
    async def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.mark.asyncio
    async def test_read_markdown_file(self, temp_dir):
        """Test reading markdown files."""
        content = "# Test Document\n\nThis is a test."
        test_file = temp_dir / "test.md"
        
        # Write test file
        await MarkdownFileManager.write_markdown_file(test_file, content)
        
        # Read file
        read_content = await MarkdownFileManager.read_markdown_file(test_file)
        assert read_content == content
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, temp_dir):
        """Test reading non-existent file raises error."""
        non_existent = temp_dir / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError):
            await MarkdownFileManager.read_markdown_file(non_existent)
    
    @pytest.mark.asyncio
    async def test_write_markdown_file(self, temp_dir):
        """Test writing markdown files."""
        content = "# Test Document\n\nThis is a test."
        test_file = temp_dir / "subdir" / "test.md"
        
        # Write file (should create directories)
        await MarkdownFileManager.write_markdown_file(test_file, content)
        
        assert test_file.exists()
        assert test_file.read_text(encoding='utf-8') == content
    
    @pytest.mark.asyncio
    async def test_list_markdown_files(self, temp_dir):
        """Test listing markdown files."""
        # Create test files
        files = [
            temp_dir / "doc1.md",
            temp_dir / "subdir" / "doc2.md",
            temp_dir / "doc3.txt",  # Not markdown
            temp_dir / "subdir" / "doc4.md"
        ]
        
        for file_path in files:
            await MarkdownFileManager.write_markdown_file(file_path, "# Test")
        
        # List markdown files
        markdown_files = await MarkdownFileManager.list_markdown_files(temp_dir)
        
        # Should find 3 markdown files
        assert len(markdown_files) == 3
        assert all(f.suffix == ".md" for f in markdown_files)
    
    @pytest.mark.asyncio
    async def test_get_file_metadata(self, temp_dir):
        """Test getting file metadata."""
        content = "# Test Document\n\nThis is a test."
        test_file = temp_dir / "test.md"
        
        await MarkdownFileManager.write_markdown_file(test_file, content)
        
        metadata = await MarkdownFileManager.get_file_metadata(test_file)
        
        assert metadata["name"] == "test.md"
        assert metadata["stem"] == "test"
        assert metadata["suffix"] == ".md"
        assert metadata["size"] > 0
        assert "modified" in metadata
        assert "created" in metadata


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @pytest.mark.asyncio
    async def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "new" / "nested" / "dir"
            
            assert not test_dir.exists()
            
            await ensure_directory_exists(test_dir)
            
            assert test_dir.exists()
            assert test_dir.is_dir()
    
    @pytest.mark.asyncio
    async def test_safe_remove_file(self):
        """Test safe file removal."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        # File exists
        assert temp_path.exists()
        result = await safe_remove_file(temp_path)
        assert result is True
        assert not temp_path.exists()
        
        # File doesn't exist (should not raise error)
        result = await safe_remove_file(temp_path)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_safe_remove_directory(self):
        """Test safe directory removal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_dir"
            test_dir.mkdir()
            
            # Create a file in the directory
            (test_dir / "test.txt").write_text("test")
            
            assert test_dir.exists()
            result = await safe_remove_directory(test_dir)
            assert result is True
            assert not test_dir.exists()
        
        # Directory doesn't exist (should not raise error)
        result = await safe_remove_directory(Path("/nonexistent/dir"))
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])