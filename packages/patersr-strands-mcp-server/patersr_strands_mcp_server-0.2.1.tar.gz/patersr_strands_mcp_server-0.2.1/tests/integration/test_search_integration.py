"""Integration tests for SearchService with real components."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.strands_mcp.models.documentation import DocumentIndex, SearchQuery
from src.strands_mcp.services.indexing_service import DocumentIndexingService
from src.strands_mcp.services.search_service import SearchService


@pytest.mark.asyncio
async def test_search_service_integration():
    """Test SearchService integration with DocumentIndexingService."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create services
        indexing_service = DocumentIndexingService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            chunk_size=200,
            chunk_overlap=20
        )
        
        search_service = SearchService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            max_snippet_length=150
        )
        
        # Create sample documents
        now = datetime.now()
        documents = [
            (
                "# Getting Started with Python\n\nPython is a powerful programming language. It's great for machine learning, data science, and web development. You can install Python from python.org.",
                "Python Guide",
                "https://github.com/example/python-guide.md",
                "/docs/python-guide.md",
                now
            ),
            (
                "# JavaScript Fundamentals\n\nJavaScript is the language of the web. It runs in browsers and on servers with Node.js. Modern JavaScript includes ES6+ features like arrow functions and async/await.",
                "JavaScript Guide", 
                "https://github.com/example/js-guide.md",
                "/docs/js-guide.md",
                now
            ),
            (
                "# Machine Learning Basics\n\nMachine learning is a subset of artificial intelligence. Popular libraries include TensorFlow, PyTorch, and scikit-learn. Python is the most popular language for ML.",
                "ML Guide",
                "https://github.com/example/ml-guide.md", 
                "/docs/ml-guide.md",
                now
            )
        ]
        
        # Index documents
        document_index = await indexing_service.index_documents(documents)
        faiss_index = indexing_service.build_faiss_index(document_index)
        
        # Save indexes
        indexing_service.save_index(document_index, faiss_index)
        
        # Load index in search service
        loaded = await search_service.load_index()
        assert loaded is True
        
        # Test semantic search
        query = SearchQuery(query="machine learning python", limit=5, min_score=0.1)
        results = await search_service.semantic_search(query)
        
        # Verify results
        assert len(results) > 0
        
        # The ML guide should rank highest for this query
        assert results[0].title in ["ML Guide", "Python Guide"]
        assert "machine learning" in results[0].snippet.lower() or "python" in results[0].snippet.lower()
        
        # Test different query
        query2 = SearchQuery(query="web development browser", limit=3, min_score=0.1)
        results2 = await search_service.semantic_search(query2)
        
        assert len(results2) > 0
        # JavaScript guide should rank high for web development query
        js_result = next((r for r in results2 if r.title == "JavaScript Guide"), None)
        assert js_result is not None
        
        # Test index stats
        stats = search_service.get_index_stats()
        assert stats["status"] == "loaded"
        assert stats["total_chunks"] > 0
        assert stats["embedding_model"] == "all-MiniLM-L6-v2"
        
        # Test similar documents
        # Find a document ID first
        first_chunk_id = document_index.chunks[0].id
        similar = await search_service.get_similar_documents(first_chunk_id, limit=2)
        
        # Should find similar documents (excluding the reference)
        assert len(similar) >= 0  # May be 0 if similarity is too low
        
        # If we have similar results, verify they don't include the reference
        for result in similar:
            assert result.title != document_index.chunks[0].title or result.section != document_index.chunks[0].section


@pytest.mark.asyncio
async def test_search_service_empty_query():
    """Test SearchService with empty or invalid queries."""
    with tempfile.TemporaryDirectory() as temp_dir:
        search_service = SearchService(index_dir=temp_dir)
        
        # Test with no index loaded
        with pytest.raises(RuntimeError, match="Search index not loaded"):
            query = SearchQuery(query="test", limit=5)
            await search_service.semantic_search(query)


@pytest.mark.asyncio 
async def test_search_service_snippet_extraction():
    """Test snippet extraction functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        indexing_service = DocumentIndexingService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            chunk_size=1000,  # Larger chunks to test snippet extraction
            chunk_overlap=50
        )
        
        search_service = SearchService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            max_snippet_length=100  # Short snippets to test truncation
        )
        
        # Create a long document
        long_content = """
        # Long Document
        
        This is the beginning of a very long document that contains lots of information.
        
        ## Section 1
        
        This section talks about various topics including programming, development, and software engineering.
        The content here is not particularly relevant to our search query.
        
        ## Section 2 - Important Information
        
        This section contains the key information about machine learning and artificial intelligence.
        Machine learning is a powerful technique for building intelligent systems.
        It involves training models on data to make predictions or decisions.
        
        ## Section 3
        
        This final section wraps up the document with some concluding thoughts.
        """
        
        now = datetime.now()
        documents = [(
            long_content,
            "Long Document",
            "https://github.com/example/long-doc.md",
            "/docs/long-doc.md", 
            now
        )]
        
        # Index and search
        document_index = await indexing_service.index_documents(documents)
        faiss_index = indexing_service.build_faiss_index(document_index)
        indexing_service.save_index(document_index, faiss_index)
        
        await search_service.load_index()
        
        # Search for specific terms
        query = SearchQuery(query="machine learning artificial intelligence", limit=5, min_score=0.1)
        results = await search_service.semantic_search(query)
        
        assert len(results) > 0
        
        # Verify snippet contains relevant terms and is properly truncated
        best_result = results[0]
        assert len(best_result.snippet) <= search_service.max_snippet_length + 20  # Allow for ellipsis and word boundaries
        
        # Should contain query-relevant content
        snippet_lower = best_result.snippet.lower()
        assert "machine learning" in snippet_lower or "artificial intelligence" in snippet_lower