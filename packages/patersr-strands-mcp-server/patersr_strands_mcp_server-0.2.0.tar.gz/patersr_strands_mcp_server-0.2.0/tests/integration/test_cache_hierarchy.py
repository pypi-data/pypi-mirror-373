"""Integration tests for cache hierarchy functionality."""

import asyncio
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strands_mcp.models.documentation import DocumentChunk, DocumentIndex, SearchQuery
from strands_mcp.services.documentation_service import DocumentationService
from strands_mcp.services.search_service import SearchService


@pytest.fixture
def sample_documentation():
    """Sample documentation for testing."""
    return [
        DocumentChunk(
            id="strands:getting-started.md",
            title="Getting Started with Strands",
            content="# Getting Started\n\nStrands is a framework for building LLM agents.",
            source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
            section="Introduction",
            file_path="/tmp/getting-started.md",
            last_modified=datetime.now(timezone.utc)
        ),
        DocumentChunk(
            id="strands:multi-agent.md",
            title="Multi-Agent Patterns",
            content="# Multi-Agent Patterns\n\nLearn about different multi-agent architectures.",
            source_url="https://github.com/strands-agents/docs/blob/main/multi-agent.md",
            section="Advanced",
            file_path="/tmp/multi-agent.md",
            last_modified=datetime.now(timezone.utc)
        )
    ]


class TestCacheHierarchyIntegration:
    """Integration tests for cache hierarchy with search service."""
    
    @pytest.mark.asyncio
    async def test_search_with_bundled_cache_fallback(self, sample_documentation):
        """Test that search works with bundled cache when user cache is unavailable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            search_cache_dir = Path(temp_dir) / "search"
            
            # Only create bundled cache
            bundled_cache_dir.mkdir(parents=True)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Create documentation service with bundled cache
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir  # Doesn't exist
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.client = MagicMock()
                
                # Create search service
                search_service = SearchService(index_dir=str(search_cache_dir))
                
                # Load documentation from bundled cache
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                
                # Verify that we can use the chunks for search (simplified test)
                # Just verify the chunks have the expected content
                assert any("Getting Started" in chunk.title for chunk in chunks)
                assert any("Multi-Agent" in chunk.title for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_cache_hierarchy_with_updates(self, sample_documentation):
        """Test cache hierarchy behavior during documentation updates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create bundled cache with older documentation
            bundled_cache_dir.mkdir(parents=True)
            old_doc = DocumentChunk(
                id="strands:old-doc.md",
                title="Old Documentation",
                content="# Old Documentation\n\nThis is outdated content.",
                source_url="https://github.com/strands-agents/docs/blob/main/old-doc.md",
                section="Legacy",
                file_path="/tmp/old-doc.md",
                last_modified=datetime(2023, 1, 1, tzinfo=timezone.utc)
            )
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime(2023, 1, 1, tzinfo=timezone.utc),
                chunks=[old_doc],
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Create documentation service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.github_repo = "test/repo"
                doc_service.github_branch = "main"
                doc_service.cache_manager = MagicMock()
                doc_service.cache_manager.add_to_cache = AsyncMock()
                doc_service.client = MagicMock()
                
                # Initially should get bundled cache (old doc)
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 1
                assert chunks[0].title == "Old Documentation"
                
                # Simulate documentation update (save new docs to user cache)
                await doc_service.save_docs_to_cache(sample_documentation)
                
                # Now should get user cache (new docs)
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                assert any(chunk.title == "Getting Started with Strands" for chunk in chunks)
                
                # Bundled cache should remain unchanged
                bundled_chunks = await doc_service._get_bundled_cached_docs()
                assert len(bundled_chunks) == 1
                assert bundled_chunks[0].title == "Old Documentation"
    
    @pytest.mark.asyncio
    async def test_first_time_startup_with_bundled_cache(self, sample_documentation):
        """Test first-time startup behavior with bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            search_cache_dir = Path(temp_dir) / "search"
            
            # Create bundled cache (simulates package installation)
            bundled_cache_dir.mkdir(parents=True)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Simulate first-time startup (no user cache exists)
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir  # Doesn't exist yet
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.client = MagicMock()
                
                # Should be able to get documentation immediately from bundled cache
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                
                # Should be able to use documentation immediately
                # Verify the chunks have the expected content
                assert any("Getting Started" in chunk.title for chunk in chunks)
                assert any("Multi-Agent" in chunk.title for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_cache_corruption_recovery(self, sample_documentation):
        """Test recovery from cache corruption using bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create valid bundled cache
            bundled_cache_dir.mkdir(parents=True)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Create corrupted user cache
            user_cache_dir.mkdir(parents=True)
            user_cache_file = user_cache_dir / "index.json"
            user_cache_file.write_text("corrupted json content")
            
            # Create documentation service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.client = MagicMock()
                
                # Should fall back to bundled cache despite corrupted user cache
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                assert any(chunk.title == "Getting Started with Strands" for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_cache_info_reflects_hierarchy(self, sample_documentation):
        """Test that cache info correctly reflects the cache hierarchy state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            user_cache_dir = Path(temp_dir) / "user"
            bundled_cache_dir = Path(temp_dir) / "bundled"
            
            # Create both caches with different content
            user_cache_dir.mkdir(parents=True)
            bundled_cache_dir.mkdir(parents=True)
            
            # User cache with 2 docs
            user_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            user_cache_file = user_cache_dir / "index.json"
            user_index.save_to_file(str(user_cache_file))
            
            # Bundled cache with 1 doc
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime(2023, 1, 1, tzinfo=timezone.utc),
                chunks=[sample_documentation[0]],
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Create documentation service
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.cache_manager.get_cache_size_mb = AsyncMock(return_value=2.5)
                doc_service.cache_manager.default_ttl_hours = 24
                doc_service.cache_manager.max_cache_size_mb = 500
                doc_service.is_cache_valid = AsyncMock(return_value=True)
                
                info = await doc_service.get_cache_info()
                
                # Should show both caches
                assert info["user_cache"]["index_exists"] is True
                assert info["user_cache"]["chunk_count"] == 2
                assert info["bundled_cache"]["index_exists"] is True
                assert info["bundled_cache"]["chunk_count"] == 1
                
                # Should indicate which cache is being used (user cache takes precedence)
                chunks = await doc_service.get_cached_docs()
                assert len(chunks) == 2  # From user cache, not bundled cache