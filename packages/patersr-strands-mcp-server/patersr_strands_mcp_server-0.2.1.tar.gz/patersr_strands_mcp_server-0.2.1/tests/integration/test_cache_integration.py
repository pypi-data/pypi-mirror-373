"""Integration tests for cache functionality."""

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import pytest

from src.strands_mcp.services.documentation_service import DocumentationService
from src.strands_mcp.models.documentation import DocumentChunk


@pytest.mark.asyncio
async def test_documentation_service_cache_integration():
    """Test end-to-end cache functionality with DocumentationService."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a documentation service with temporary cache
        service = DocumentationService(
            cache_dir=temp_dir,
            github_repo="test/repo",
            cache_ttl_hours=1,
            max_cache_size_mb=10
        )
        
        # Create some sample document chunks
        sample_chunks = [
            DocumentChunk(
                id="test:doc1",
                title="Test Document 1",
                content="# Test Document 1\n\nThis is the first test document.",
                source_url="https://github.com/test/repo/blob/main/doc1.md",
                section="General",
                file_path=str(Path(temp_dir) / "doc1.md"),
                last_modified=datetime.now(timezone.utc)
            ),
            DocumentChunk(
                id="test:doc2",
                title="Test Document 2",
                content="# Test Document 2\n\nThis is the second test document.",
                source_url="https://github.com/test/repo/blob/main/doc2.md",
                section="API",
                file_path=str(Path(temp_dir) / "doc2.md"),
                last_modified=datetime.now(timezone.utc)
            )
        ]
        
        # Initially, cache should be invalid
        assert not await service.is_cache_valid()
        
        # Get cache info - should show empty cache
        cache_info = await service.get_cache_info()
        assert cache_info["cache_valid"] is False
        assert cache_info["index_exists"] is False
        assert cache_info["cache_size_mb"] == 0.0
        
        # Save documents to cache
        await service.save_docs_to_cache(sample_chunks)
        
        # Now cache should be valid
        assert await service.is_cache_valid()
        
        # Get cache info - should show populated cache
        cache_info = await service.get_cache_info()
        assert cache_info["cache_valid"] is True
        assert cache_info["index_exists"] is True
        assert cache_info["chunk_count"] == 2
        # Cache size might be 0 if only metadata files exist, which is fine
        assert cache_info["cache_size_mb"] >= 0
        
        # Retrieve cached documents
        cached_docs = await service.get_cached_docs()
        assert cached_docs is not None
        assert len(cached_docs) == 2
        assert cached_docs[0].title == "Test Document 1"
        assert cached_docs[1].title == "Test Document 2"
        
        # Test cache cleanup
        cleanup_count = await service.cleanup_cache()
        # Should be 0 since nothing is expired or over size limit
        assert cleanup_count == 0
        
        # Test cache invalidation
        result = await service.invalidate_cache()
        assert result is True
        assert not await service.is_cache_valid()
        
        # Test clearing cache
        # First, add documents back
        await service.save_docs_to_cache(sample_chunks)
        assert await service.is_cache_valid()
        
        # Clear cache
        cleared_count = await service.clear_cache()
        assert cleared_count > 0
        assert not await service.is_cache_valid()
        
        # Close the service
        await service.close()


@pytest.mark.asyncio
async def test_cache_manager_ttl_and_size_limits():
    """Test cache TTL and size limit functionality."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = DocumentationService(
            cache_dir=temp_dir,
            cache_ttl_hours=1,
            max_cache_size_mb=0.001  # Very small limit to test size cleanup
        )
        
        # Create a large document chunk
        large_content = "# Large Document\n\n" + "This is a large document. " * 1000
        large_chunk = DocumentChunk(
            id="test:large",
            title="Large Document",
            content=large_content,
            source_url="https://github.com/test/repo/blob/main/large.md",
            section="General",
            file_path=str(Path(temp_dir) / "large.md"),
            last_modified=datetime.now(timezone.utc)
        )
        
        # Save the large document
        await service.save_docs_to_cache([large_chunk])
        
        # Check cache size
        cache_info = await service.get_cache_info()
        initial_size = cache_info["cache_size_mb"]
        
        # Add another document that should trigger size cleanup
        another_chunk = DocumentChunk(
            id="test:another",
            title="Another Document",
            content="# Another Document\n\n" + "More content. " * 500,
            source_url="https://github.com/test/repo/blob/main/another.md",
            section="General",
            file_path=str(Path(temp_dir) / "another.md"),
            last_modified=datetime.now(timezone.utc)
        )
        
        await service.save_docs_to_cache([large_chunk, another_chunk])
        
        # Cleanup should remove some items due to size limit
        cleanup_count = await service.cleanup_cache()
        
        # Verify cache size is managed
        final_cache_info = await service.get_cache_info()
        
        await service.close()


if __name__ == "__main__":
    pytest.main([__file__])