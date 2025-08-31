"""Tests for bundled cache copying functionality."""

import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from src.strands_mcp.server import StrandsMCPServer
from src.strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from datetime import datetime, timezone


@pytest.fixture
def temp_bundled_cache():
    """Create a temporary bundled cache for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        bundled_cache_dir = Path(temp_dir) / "bundled_cache"
        bundled_cache_dir.mkdir()
        
        # Create sample chunks
        chunks = [
            DocumentChunk(
                id="test:doc1.md",
                title="Test Document 1",
                content="This is test content 1",
                source_url="https://github.com/test/repo/blob/main/doc1.md",
                section="Getting Started",
                file_path=str(bundled_cache_dir / "doc1.md"),
                last_modified=datetime.now(timezone.utc)
            ),
            DocumentChunk(
                id="test:doc2.md", 
                title="Test Document 2",
                content="This is test content 2",
                source_url="https://github.com/test/repo/blob/main/doc2.md",
                section="Advanced",
                file_path=str(bundled_cache_dir / "doc2.md"),
                last_modified=datetime.now(timezone.utc)
            )
        ]
        
        # Create index file
        index = DocumentIndex(
            version="1.0",
            last_updated=datetime.now(timezone.utc),
            chunks=chunks,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        index_file = bundled_cache_dir / "index.json"
        index.save_to_file(str(index_file))
        
        # Create some sample markdown files
        (bundled_cache_dir / "doc1.md").write_text("This is test content 1")
        (bundled_cache_dir / "doc2.md").write_text("This is test content 2")
        
        yield bundled_cache_dir


@pytest.fixture
def temp_user_cache():
    """Create a temporary user cache directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        user_cache_dir = Path(temp_dir) / "user_cache"
        yield user_cache_dir


class TestBundledCacheCopy:
    """Test bundled cache copying functionality."""
    
    @pytest.mark.asyncio
    async def test_copy_bundled_cache_to_user_cache_success(self, temp_bundled_cache, temp_user_cache):
        """Test successful copying of bundled cache to user cache."""
        server = StrandsMCPServer()
        
        # Mock the bundled cache path resolution
        server._get_bundled_cache_path = MagicMock(return_value=temp_bundled_cache)
        # Mock the documentation service cache directory
        server._documentation_service.cache_dir = temp_user_cache
        
        # Copy bundled cache
        await server._copy_bundled_cache_to_user_cache()
        
        # Verify files were copied
        assert (temp_user_cache / "index.json").exists()
        assert (temp_user_cache / "doc1.md").exists()
        assert (temp_user_cache / "doc2.md").exists()
        
        # Verify index content
        copied_index = DocumentIndex.load_from_file(str(temp_user_cache / "index.json"))
        assert len(copied_index.chunks) == 2
        assert copied_index.version == "1.0"
    
    @pytest.mark.asyncio
    async def test_copy_bundled_cache_no_source(self, temp_user_cache):
        """Test copying when no bundled cache exists."""
        server = StrandsMCPServer()
        
        # Mock non-existent bundled cache
        non_existent_path = Path("/non/existent/path")
        server._get_bundled_cache_path = MagicMock(return_value=non_existent_path)
        server._documentation_service.cache_dir = temp_user_cache
        
        # Should not raise exception
        await server._copy_bundled_cache_to_user_cache()
        
        # User cache should remain empty
        assert not (temp_user_cache / "index.json").exists()
    
    @pytest.mark.asyncio
    async def test_copy_bundled_cache_permission_error(self, temp_bundled_cache, temp_user_cache):
        """Test copying when permission error occurs."""
        server = StrandsMCPServer()
        
        server._get_bundled_cache_path = MagicMock(return_value=temp_bundled_cache)
        with patch('shutil.copy2', side_effect=PermissionError("Permission denied")):
            server._documentation_service.cache_dir = temp_user_cache
            
            # Should raise exception
            with pytest.raises(PermissionError):
                await server._copy_bundled_cache_to_user_cache()
    
    @pytest.mark.asyncio
    async def test_get_cached_docs_with_hierarchy_copies_bundled(self, temp_bundled_cache, temp_user_cache):
        """Test that cache hierarchy method copies bundled cache when user cache is empty."""
        server = StrandsMCPServer()
        
        # Mock documentation service to return empty user cache
        server._documentation_service.get_cached_docs = AsyncMock(return_value=None)
        server._documentation_service.cache_dir = temp_user_cache
        
        # Mock bundled cache loading
        server._get_bundled_cache_path = MagicMock(return_value=temp_bundled_cache)
        # Mock the copy method to track if it was called
        server._copy_bundled_cache_to_user_cache = AsyncMock()
        
        # Call hierarchy method
        result = await server._get_cached_docs_with_hierarchy()
        
        # Should have found bundled cache
        assert result is not None
        assert len(result) == 2
        
        # Should have attempted to copy bundled cache
        server._copy_bundled_cache_to_user_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cached_docs_with_hierarchy_skips_copy_when_user_cache_exists(self, temp_user_cache):
        """Test that cache hierarchy method skips copying when user cache exists."""
        server = StrandsMCPServer()
        
        # Create sample user cache chunks
        user_chunks = [
            DocumentChunk(
                id="user:doc1.md",
                title="User Document 1", 
                content="User content 1",
                source_url="https://github.com/user/repo/blob/main/doc1.md",
                section="User Section",
                file_path=str(temp_user_cache / "doc1.md"),
                last_modified=datetime.now(timezone.utc)
            )
        ]
        
        # Mock documentation service to return user cache
        server._documentation_service.get_cached_docs = AsyncMock(return_value=user_chunks)
        
        # Mock the copy method to track if it was called
        server._copy_bundled_cache_to_user_cache = AsyncMock()
        
        # Call hierarchy method
        result = await server._get_cached_docs_with_hierarchy()
        
        # Should have found user cache
        assert result is not None
        assert len(result) == 1
        assert result[0].title == "User Document 1"
        
        # Should NOT have attempted to copy bundled cache
        server._copy_bundled_cache_to_user_cache.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_copy_bundled_cache_handles_directories(self, temp_user_cache):
        """Test copying bundled cache with subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundled_cache_dir = Path(temp_dir) / "bundled_cache"
            bundled_cache_dir.mkdir()
            
            # Create subdirectory with files
            subdir = bundled_cache_dir / "subdir"
            subdir.mkdir()
            (subdir / "subfile.md").write_text("Subdirectory content")
            
            # Create main index
            (bundled_cache_dir / "index.json").write_text('{"version": "1.0", "chunks": []}')
            
            server = StrandsMCPServer()
            
            server._get_bundled_cache_path = MagicMock(return_value=bundled_cache_dir)
            server._documentation_service.cache_dir = temp_user_cache
            
            # Copy bundled cache
            await server._copy_bundled_cache_to_user_cache()
            
            # Verify subdirectory was copied
            assert (temp_user_cache / "subdir").exists()
            assert (temp_user_cache / "subdir" / "subfile.md").exists()
            assert (temp_user_cache / "subdir" / "subfile.md").read_text() == "Subdirectory content"