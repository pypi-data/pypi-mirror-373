"""Integration tests for bundled cache building."""

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
            id="strands:deployment.md",
            title="Deployment Guide",
            content="# Deployment\n\nLearn how to deploy Strands agents to production.",
            source_url="https://github.com/strands-agents/docs/blob/main/deployment.md",
            section="Operations",
            file_path="/tmp/deployment.md",
            last_modified=datetime.now(timezone.utc)
        )
    ]


class TestBundledCacheBuild:
    """Test building and using bundled cache."""
    
    @pytest.mark.asyncio
    async def test_build_bundled_cache_workflow(self, sample_documentation):
        """Test the complete workflow of building and using bundled cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundled_cache_dir = Path(temp_dir) / "bundled"
            user_cache_dir = Path(temp_dir) / "user"
            
            # Step 1: Simulate building bundled cache (like CI/CD would do)
            bundled_cache_dir.mkdir(parents=True)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Step 2: Simulate first-time user startup (no user cache)
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir  # Doesn't exist
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.client = MagicMock()
                
                # Should get documentation from bundled cache
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                assert any("Getting Started" in chunk.title for chunk in chunks)
                assert any("Deployment" in chunk.title for chunk in chunks)
                
                # Cache info should show bundled cache is being used
                doc_service.cache_manager.get_cache_size_mb = AsyncMock(return_value=0.0)
                doc_service.cache_manager.default_ttl_hours = 24
                doc_service.cache_manager.max_cache_size_mb = 500
                doc_service.is_cache_valid = AsyncMock(return_value=False)
                
                info = await doc_service.get_cache_info()
                assert info["user_cache"]["index_exists"] is False
                assert info["bundled_cache"]["index_exists"] is True
                assert info["bundled_cache"]["chunk_count"] == 2
    
    @pytest.mark.asyncio
    async def test_bundled_cache_provides_offline_capability(self, sample_documentation):
        """Test that bundled cache enables offline operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundled_cache_dir = Path(temp_dir) / "bundled"
            user_cache_dir = Path(temp_dir) / "user"
            
            # Create bundled cache
            bundled_cache_dir.mkdir(parents=True)
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime.now(timezone.utc),
                chunks=sample_documentation,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Simulate network failure (no user cache, can't fetch from GitHub)
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.cache_manager = MagicMock()
                doc_service.client = MagicMock()
                
                # Should still be able to get documentation from bundled cache
                chunks = await doc_service.get_cached_docs()
                assert chunks is not None
                assert len(chunks) == 2
                
                # Verify content is accessible
                getting_started_chunk = next(
                    chunk for chunk in chunks 
                    if "Getting Started" in chunk.title
                )
                assert "framework for building LLM agents" in getting_started_chunk.content
    
    @pytest.mark.asyncio
    async def test_bundled_cache_never_modified_by_updates(self, sample_documentation):
        """Test that bundled cache is never modified by documentation updates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundled_cache_dir = Path(temp_dir) / "bundled"
            user_cache_dir = Path(temp_dir) / "user"
            
            # Create initial bundled cache with old content
            bundled_cache_dir.mkdir(parents=True)
            old_chunk = DocumentChunk(
                id="strands:old.md",
                title="Old Documentation",
                content="# Old\n\nThis is old content.",
                source_url="https://github.com/strands-agents/docs/blob/main/old.md",
                section="Legacy",
                file_path="/tmp/old.md",
                last_modified=datetime(2023, 1, 1, tzinfo=timezone.utc)
            )
            bundled_index = DocumentIndex(
                version="1.0",
                last_updated=datetime(2023, 1, 1, tzinfo=timezone.utc),
                chunks=[old_chunk],
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            bundled_cache_file = bundled_cache_dir / "index.json"
            bundled_index.save_to_file(str(bundled_cache_file))
            
            # Get initial bundled cache content
            initial_content = bundled_cache_file.read_text()
            initial_mtime = bundled_cache_file.stat().st_mtime
            
            # Simulate documentation update
            with patch.object(DocumentationService, '__init__', lambda self, **kwargs: None):
                doc_service = DocumentationService()
                doc_service.cache_dir = user_cache_dir
                doc_service.bundled_cache_dir = bundled_cache_dir
                doc_service.github_repo = "test/repo"
                doc_service.github_branch = "main"
                doc_service.cache_manager = MagicMock()
                doc_service.cache_manager.add_to_cache = AsyncMock()
                doc_service.client = MagicMock()
                
                # Save new documentation to user cache
                await doc_service.save_docs_to_cache(sample_documentation)
                
                # Verify bundled cache was not modified
                assert bundled_cache_file.read_text() == initial_content
                assert bundled_cache_file.stat().st_mtime == initial_mtime
                
                # Verify user cache was created with new content
                user_cache_file = user_cache_dir / "index.json"
                assert user_cache_file.exists()
                
                user_index = DocumentIndex.load_from_file(str(user_cache_file))
                assert len(user_index.chunks) == 2
                assert any("Getting Started" in chunk.title for chunk in user_index.chunks)
                
                # Verify cache hierarchy works correctly
                chunks = await doc_service.get_cached_docs()
                assert len(chunks) == 2  # Should get user cache, not bundled cache
                assert any("Getting Started" in chunk.title for chunk in chunks)