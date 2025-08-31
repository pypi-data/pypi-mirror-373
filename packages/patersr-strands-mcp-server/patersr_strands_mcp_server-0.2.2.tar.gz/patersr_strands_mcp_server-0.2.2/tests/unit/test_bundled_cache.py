"""Tests for bundled cache functionality."""

import asyncio
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strands_mcp.models.documentation import DocumentChunk, DocumentIndex
from strands_mcp.services.documentation_service import DocumentationService


@pytest.fixture
def sample_chunks():
    """Sample document chunks for testing."""
    return [
        DocumentChunk(
            id="test:doc1.md",
            title="Test Document 1",
            content="# Test Document 1\n\nThis is test content.",
            source_url="https://github.com/test/repo/blob/main/doc1.md",
            section="General",
            file_path="/tmp/doc1.md",
            last_modified=datetime.now(timezone.utc)
        ),
        DocumentChunk(
            id="test:doc2.md",
            title="Test Document 2",
            content="# Test Document 2\n\nThis is more test content.",
            source_url="https://github.com/test/repo/blob/main/doc2.md",
            section="Advanced",
            file_path="/tmp/doc2.md",
            last_modified=datetime.now(timezone.utc)
        )
    ]


@pytest.fixture
def sample_index(sample_chunks):
    """Sample document index for testing."""
    return DocumentIndex(
        version="1.0",
        last_updated=datetime.now(timezone.utc),
        chunks=sample_chunks,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )


class TestBundledCacheHierarchy:
    """Test cache hierarchy: user cache → bundled cache → None."""
    
    @pytest.mark.asyncio
    async def test_user_cache_takes_precedence(self, sample_index):
        """Test that user cache is preferred over bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create both caches
            user_cache_dir.mkdir(parents=True)
            bundled_cache_dir.mkdir(parents=True)
            
            # User cache with 2 chunks
            user_index = sample_index
            user_cache_file = user_cache_dir / "index.json"
            user_index.save_to_file(str(user_cache_file))
            
            # Bundled cache with 1 chunk (should be ignored)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=[sample_index.chunks[0]],  # Only first chunk
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Mock the bundled cache directory in the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                
                # Get cached docs should return user cache (2 chunks)
                chunks = await service.get_cached_docs()
                
                assert chunks is not None
                assert len(chunks) == 2
                assert chunks[0].id == "test:doc1.md"
                assert chunks[1].id == "test:doc2.md"
    
    @pytest.mark.asyncio
    async def test_bundled_cache_fallback(self, sample_index):
        """Test that bundled cache is used when user cache is not available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Only create bundled cache
            bundled_cache_dir.mkdir(parents=True)
            bundled_cache_file = bundled_cache_dir / "index.json"
            sample_index.save_to_file(str(bundled_cache_file))
            
            # Mock the bundled cache directory in the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir  # Doesn't exist
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                
                # Get cached docs should return bundled cache
                chunks = await service.get_cached_docs()
                
                assert chunks is not None
                assert len(chunks) == 2
                assert chunks[0].id == "test:doc1.md"
    
    @pytest.mark.asyncio
    async def test_no_cache_available(self):
        """Test behavior when no cache is available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Neither cache exists
            
            # Mock the bundled cache directory in the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                
                # Get cached docs should return None
                chunks = await service.get_cached_docs()
                
                assert chunks is None
    
    @pytest.mark.asyncio
    async def test_corrupted_user_cache_falls_back_to_bundled(self, sample_index):
        """Test that corrupted user cache falls back to bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create directories
            user_cache_dir.mkdir(parents=True)
            bundled_cache_dir.mkdir(parents=True)
            
            # Create corrupted user cache
            user_cache_file = user_cache_dir / "index.json"
            user_cache_file.write_text("invalid json content")
            
            # Create valid bundled cache
            bundled_cache_file = bundled_cache_dir / "index.json"
            sample_index.save_to_file(str(bundled_cache_file))
            
            # Mock the bundled cache directory in the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                
                # Get cached docs should return bundled cache
                chunks = await service.get_cached_docs()
                
                assert chunks is not None
                assert len(chunks) == 2
                assert chunks[0].id == "test:doc1.md"


class TestCacheInfo:
    """Test cache information reporting."""
    
    @pytest.mark.asyncio
    async def test_cache_info_with_both_caches(self, sample_index):
        """Test cache info when both user and bundled caches exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create both caches
            user_cache_dir.mkdir(parents=True)
            bundled_cache_dir.mkdir(parents=True)
            
            user_cache_file = user_cache_dir / "index.json"
            sample_index.save_to_file(str(user_cache_file))
            
            bundled_cache_file = bundled_cache_dir / "index.json"
            sample_index.save_to_file(str(bundled_cache_file))
            
            # Mock the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                service.cache_manager.get_cache_size_mb = AsyncMock(return_value=1.5)
                service.cache_manager.default_ttl_hours = 24
                service.cache_manager.max_cache_size_mb = 500
                
                # Mock is_cache_valid
                service.is_cache_valid = AsyncMock(return_value=True)
                
                info = await service.get_cache_info()
                
                assert info["cache_size_mb"] == 1.5
                assert info["cache_valid"] is True
                assert info["user_cache"]["index_exists"] is True
                assert info["user_cache"]["chunk_count"] == 2
                assert info["bundled_cache"]["index_exists"] is True
                assert info["bundled_cache"]["chunk_count"] == 2
    
    @pytest.mark.asyncio
    async def test_cache_info_bundled_only(self, sample_index):
        """Test cache info when only bundled cache exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Only create bundled cache
            bundled_cache_dir.mkdir(parents=True)
            bundled_cache_file = bundled_cache_dir / "index.json"
            sample_index.save_to_file(str(bundled_cache_file))
            
            # Mock the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.cache_manager = MagicMock()
                service.cache_manager.get_cache_size_mb = AsyncMock(return_value=0.0)
                service.cache_manager.default_ttl_hours = 24
                service.cache_manager.max_cache_size_mb = 500
                
                # Mock is_cache_valid
                service.is_cache_valid = AsyncMock(return_value=False)
                
                info = await service.get_cache_info()
                
                assert info["user_cache"]["index_exists"] is False
                assert "chunk_count" not in info["user_cache"]
                assert info["bundled_cache"]["index_exists"] is True
                assert info["bundled_cache"]["chunk_count"] == 2


class TestBundledCacheReadOnly:
    """Test that bundled cache is read-only and never modified."""
    
    @pytest.mark.asyncio
    async def test_save_docs_only_updates_user_cache(self, sample_chunks):
        """Test that saving docs only updates user cache, not bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create directories
            user_cache_dir.mkdir(parents=True)
            bundled_cache_dir.mkdir(parents=True)
            
            # Create initial bundled cache
            initial_bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime(2023, 1, 1, tzinfo=timezone.utc),
                chunks=[],
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            initial_bundled_index.save_to_file(str(bundled_cache_file))
            
            # Get initial bundled cache modification time
            initial_mtime = bundled_cache_file.stat().st_mtime
            
            # Mock the service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                service = DocumentationService()
                service.cache_dir = user_cache_dir
                service.bundled_cache_dir = bundled_cache_dir
                service.github_repo = "test/repo"
                service.github_branch = "main"
                service.cache_manager = MagicMock()
                service.cache_manager.add_to_cache = AsyncMock()
                
                # Save docs to cache
                await service.save_docs_to_cache(sample_chunks)
                
                # Check that user cache was created
                user_cache_file = user_cache_dir / "index.json"
                assert user_cache_file.exists()
                
                user_index = DocumentIndex.load_from_file(str(user_cache_file))
                assert len(user_index.chunks) == 2
                
                # Check that bundled cache was not modified
                assert bundled_cache_file.stat().st_mtime == initial_mtime
                
                bundled_index = DocumentIndex.load_from_file(str(bundled_cache_file))
                assert len(bundled_index.chunks) == 0  # Still empty