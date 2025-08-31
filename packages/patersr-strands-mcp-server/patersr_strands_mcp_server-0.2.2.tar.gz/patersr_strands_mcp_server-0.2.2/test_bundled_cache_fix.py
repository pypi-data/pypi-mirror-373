#!/usr/bin/env python3
"""Test script to verify bundled cache copying functionality."""

import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Import our server
from src.strands_mcp.server import StrandsMCPServer
from src.strands_mcp.models.documentation import DocumentChunk, DocumentIndex


async def test_bundled_cache_copy():
    """Test the bundled cache copying functionality."""
    print("🧪 Testing bundled cache copying functionality...")
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        bundled_cache_dir = temp_path / "bundled_cache"
        user_cache_dir = temp_path / "user_cache"
        
        # Create mock bundled cache
        bundled_cache_dir.mkdir()
        
        # Create sample chunks
        chunks = [
            DocumentChunk(
                id="test:getting-started.md",
                title="Getting Started with Strands",
                content="# Getting Started\n\nThis is a getting started guide for Strands Agent SDK.",
                source_url="https://github.com/strands-agents/docs/blob/main/getting-started.md",
                section="Getting Started",
                file_path=str(bundled_cache_dir / "getting-started.md"),
                last_modified=datetime.now(timezone.utc)
            ),
            DocumentChunk(
                id="test:advanced-usage.md",
                title="Advanced Usage",
                content="# Advanced Usage\n\nAdvanced patterns and techniques for Strands.",
                source_url="https://github.com/strands-agents/docs/blob/main/advanced-usage.md",
                section="Advanced",
                file_path=str(bundled_cache_dir / "advanced-usage.md"),
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
        
        # Create sample markdown files
        (bundled_cache_dir / "getting-started.md").write_text("# Getting Started\n\nThis is a getting started guide for Strands Agent SDK.")
        (bundled_cache_dir / "advanced-usage.md").write_text("# Advanced Usage\n\nAdvanced patterns and techniques for Strands.")
        
        print(f"✅ Created mock bundled cache with {len(chunks)} chunks")
        
        # Create server and test the copying
        server = StrandsMCPServer()
        
        # Mock the bundled cache path to point to our test directory
        server._get_bundled_cache_path = lambda: bundled_cache_dir
        server._documentation_service.cache_dir = user_cache_dir
        
        print("🔄 Testing cache hierarchy (should find bundled cache and copy it)...")
        
        # Test the cache hierarchy - this should find bundled cache and copy it
        cached_docs = await server._get_cached_docs_with_hierarchy()
        
        if cached_docs:
            print(f"✅ Found {len(cached_docs)} documents from cache hierarchy")
            print(f"   - Document 1: {cached_docs[0].title}")
            print(f"   - Document 2: {cached_docs[1].title}")
        else:
            print("❌ No documents found from cache hierarchy")
            return False
        
        # Check if files were copied to user cache
        if (user_cache_dir / "index.json").exists():
            print("✅ Index file copied to user cache")
        else:
            print("❌ Index file not copied to user cache")
            return False
        
        if (user_cache_dir / "getting-started.md").exists():
            print("✅ Markdown files copied to user cache")
        else:
            print("❌ Markdown files not copied to user cache")
            return False
        
        # Verify the copied index content
        copied_index = DocumentIndex.load_from_file(str(user_cache_dir / "index.json"))
        if len(copied_index.chunks) == 2:
            print(f"✅ Copied index contains {len(copied_index.chunks)} chunks")
        else:
            print(f"❌ Copied index contains {len(copied_index.chunks)} chunks, expected 2")
            return False
        
        print("🎉 All tests passed! Bundled cache copying works correctly.")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_bundled_cache_copy())
    if success:
        print("\n✅ Bundled cache copying functionality is working correctly!")
        print("   The fix should resolve the empty cache issue on first deployment.")
    else:
        print("\n❌ Tests failed. There may be an issue with the implementation.")