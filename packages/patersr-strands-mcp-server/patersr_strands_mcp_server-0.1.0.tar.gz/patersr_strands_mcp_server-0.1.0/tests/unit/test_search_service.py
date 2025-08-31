"""Unit tests for SearchService."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import faiss
import numpy as np
import pytest

from src.strands_mcp.models.documentation import DocumentChunk, DocumentIndex, SearchQuery
from src.strands_mcp.services.search_service import SearchService


@pytest.fixture
def temp_index_dir():
    """Create a temporary directory for index files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_chunks():
    """Create sample document chunks for testing."""
    now = datetime.now()
    
    chunks = [
        DocumentChunk(
            id="chunk1",
            title="Getting Started Guide",
            content="This is a comprehensive guide to getting started with the Strands SDK. It covers installation, setup, and basic usage patterns.",
            source_url="https://github.com/strands/docs/getting-started.md",
            section="Introduction",
            file_path="/docs/getting-started.md",
            last_modified=now,
            embedding=[0.1, 0.2, 0.3, 0.4]  # Mock embedding
        ),
        DocumentChunk(
            id="chunk2",
            title="Advanced Configuration",
            content="Advanced configuration options for the Strands SDK including custom models, deployment settings, and performance tuning.",
            source_url="https://github.com/strands/docs/advanced.md",
            section="Configuration",
            file_path="/docs/advanced.md",
            last_modified=now,
            embedding=[0.2, 0.3, 0.4, 0.5]  # Mock embedding
        ),
        DocumentChunk(
            id="chunk3",
            title="API Reference",
            content="Complete API reference for all Strands SDK classes and methods. Includes examples and parameter descriptions.",
            source_url="https://github.com/strands/docs/api.md",
            section="Reference",
            file_path="/docs/api.md",
            last_modified=now,
            embedding=[0.3, 0.4, 0.5, 0.6]  # Mock embedding
        )
    ]
    
    return chunks


@pytest.fixture
def sample_document_index(sample_chunks):
    """Create a sample document index."""
    return DocumentIndex(
        version="20240101_120000_000000",
        last_updated=datetime.now(),
        chunks=sample_chunks,
        embedding_model="all-MiniLM-L6-v2"
    )


@pytest.fixture
def mock_faiss_index():
    """Create a mock FAISS index."""
    # Create a real FAISS index for testing
    embeddings = np.array([
        [0.1, 0.2, 0.3, 0.4],
        [0.2, 0.3, 0.4, 0.5],
        [0.3, 0.4, 0.5, 0.6]
    ], dtype=np.float32)
    
    faiss.normalize_L2(embeddings)
    
    index = faiss.IndexFlatIP(4)  # 4-dimensional vectors
    index.add(embeddings)
    
    return index


@pytest.fixture
def search_service(temp_index_dir):
    """Create a SearchService instance for testing."""
    return SearchService(
        model_name="all-MiniLM-L6-v2",
        index_dir=temp_index_dir,
        max_snippet_length=100
    )


class TestSearchService:
    """Test cases for SearchService."""
    
    def test_init(self, temp_index_dir):
        """Test SearchService initialization."""
        service = SearchService(
            model_name="test-model",
            index_dir=temp_index_dir,
            max_snippet_length=200
        )
        
        assert service.model_name == "test-model"
        assert service.index_dir == Path(temp_index_dir)
        assert service.max_snippet_length == 200
        assert service._model is None
        assert service._document_index is None
        assert service._faiss_index is None
    
    @patch('src.strands_mcp.services.search_service.SentenceTransformer')
    def test_model_lazy_loading(self, mock_transformer, search_service):
        """Test that the sentence transformer model is loaded lazily."""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        
        # First access should load the model
        model = search_service.model
        assert model == mock_model
        mock_transformer.assert_called_once_with("all-MiniLM-L6-v2")
        
        # Second access should return cached model
        model2 = search_service.model
        assert model2 == mock_model
        assert mock_transformer.call_count == 1
    
    @pytest.mark.asyncio
    async def test_load_index_success(self, search_service, sample_document_index, mock_faiss_index):
        """Test successful index loading."""
        with patch('src.strands_mcp.services.search_service.DocumentIndexingService') as mock_indexing_class:
            mock_indexing = MagicMock()
            mock_indexing.load_latest_index.return_value = (sample_document_index, mock_faiss_index)
            mock_indexing_class.return_value = mock_indexing
            
            # Reset the cached indexing service
            search_service._indexing_service = None
            
            result = await search_service.load_index()
            
            assert result is True
            assert search_service._document_index == sample_document_index
            assert search_service._faiss_index == mock_faiss_index
    
    @pytest.mark.asyncio
    async def test_load_index_failure(self, search_service):
        """Test index loading failure."""
        with patch('src.strands_mcp.services.search_service.DocumentIndexingService') as mock_indexing_class:
            mock_indexing = MagicMock()
            mock_indexing.load_latest_index.return_value = (None, None)
            mock_indexing_class.return_value = mock_indexing
            
            # Reset the cached indexing service
            search_service._indexing_service = None
            
            result = await search_service.load_index()
            
            assert result is False
            assert search_service._document_index is None
            assert search_service._faiss_index is None
    
    @pytest.mark.asyncio
    async def test_load_index_exception(self, search_service):
        """Test index loading with exception."""
        with patch('src.strands_mcp.services.search_service.DocumentIndexingService') as mock_indexing_class:
            mock_indexing = MagicMock()
            mock_indexing.load_latest_index.side_effect = Exception("Load error")
            mock_indexing_class.return_value = mock_indexing
            
            # Reset the cached indexing service
            search_service._indexing_service = None
            
            result = await search_service.load_index()
            
            assert result is False
    
    def test_ensure_index_loaded_success(self, search_service, sample_document_index, mock_faiss_index):
        """Test _ensure_index_loaded when index is loaded."""
        search_service._document_index = sample_document_index
        search_service._faiss_index = mock_faiss_index
        
        # Should not raise an exception
        search_service._ensure_index_loaded()
    
    def test_ensure_index_loaded_failure(self, search_service):
        """Test _ensure_index_loaded when index is not loaded."""
        with pytest.raises(RuntimeError, match="Search index not loaded"):
            search_service._ensure_index_loaded()
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.search_service.SentenceTransformer')
    async def test_create_query_embedding(self, mock_transformer, search_service):
        """Test query embedding creation."""
        mock_model = MagicMock()
        mock_embedding = np.array([[0.1, 0.2, 0.3, 0.4]], dtype=np.float32)
        mock_model.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_model
        
        result = await search_service._create_query_embedding("test query")
        
        assert isinstance(result, np.ndarray)
        mock_model.encode.assert_called_once_with(["test query"], convert_to_numpy=True)
    
    def test_extract_snippet_short_content(self, search_service):
        """Test snippet extraction with short content."""
        content = "Short content that fits in snippet."
        query = "content"
        
        result = search_service._extract_snippet(content, query)
        
        assert result == content
    
    def test_extract_snippet_long_content(self, search_service):
        """Test snippet extraction with long content."""
        content = "This is a very long piece of content that exceeds the maximum snippet length and should be truncated appropriately while maintaining readability and context for the user."
        query = "content"
        
        result = search_service._extract_snippet(content, query)
        
        assert len(result) <= search_service.max_snippet_length + 10  # Allow for ellipsis
        assert "content" in result.lower()
        assert result.endswith("...")
    
    def test_extract_snippet_with_query_terms(self, search_service):
        """Test snippet extraction prioritizes query terms."""
        content = "The beginning of this content is not very relevant. However, the middle section contains important information about configuration and setup that matches the user query perfectly."
        query = "configuration setup"
        
        result = search_service._extract_snippet(content, query)
        
        assert "configuration" in result.lower()
        assert "setup" in result.lower()
    
    def test_rank_results_empty(self, search_service, sample_document_index):
        """Test ranking with empty results."""
        search_service._document_index = sample_document_index
        
        result = search_service._rank_results([], "test query")
        
        assert result == []
    
    def test_rank_results_with_boosts(self, search_service, sample_document_index):
        """Test result ranking with various boost factors."""
        search_service._document_index = sample_document_index
        
        # Mock results with different similarity scores
        results = [(0, 0.7), (1, 0.8), (2, 0.6)]  # chunk indices and scores
        
        ranked = search_service._rank_results(results, "getting started")
        
        # Should be sorted by enhanced score (chunk 0 should get boost for "getting started")
        assert len(ranked) == 3
        assert all(isinstance(item, tuple) for item in ranked)
        assert all(len(item) == 2 for item in ranked)
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.search_service.SentenceTransformer')
    async def test_semantic_search_success(self, mock_transformer, search_service, sample_document_index, mock_faiss_index):
        """Test successful semantic search."""
        # Setup mocks
        mock_model = MagicMock()
        mock_embedding = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        mock_model.encode.return_value = np.array([mock_embedding])
        mock_transformer.return_value = mock_model
        
        # Setup search service
        search_service._document_index = sample_document_index
        search_service._faiss_index = mock_faiss_index
        
        # Create search query
        query = SearchQuery(query="getting started", limit=2, min_score=0.5)
        
        # Perform search
        results = await search_service.semantic_search(query)
        
        # Verify results
        assert isinstance(results, list)
        assert len(results) <= query.limit
        
        for result in results:
            assert hasattr(result, 'title')
            assert hasattr(result, 'snippet')
            assert hasattr(result, 'source_url')
            assert hasattr(result, 'relevance_score')
            assert hasattr(result, 'section')
            assert result.relevance_score >= query.min_score
    
    @pytest.mark.asyncio
    async def test_semantic_search_no_index(self, search_service):
        """Test semantic search without loaded index."""
        query = SearchQuery(query="test", limit=5)
        
        with pytest.raises(RuntimeError, match="Search index not loaded"):
            await search_service.semantic_search(query)
    
    @pytest.mark.asyncio
    async def test_get_similar_documents_success(self, search_service, sample_document_index, mock_faiss_index):
        """Test finding similar documents."""
        search_service._document_index = sample_document_index
        search_service._faiss_index = mock_faiss_index
        
        results = await search_service.get_similar_documents("chunk1", limit=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        
        # Should not include the reference document itself
        for result in results:
            assert result.title != "Getting Started Guide"  # Reference document title
    
    @pytest.mark.asyncio
    async def test_get_similar_documents_not_found(self, search_service, sample_document_index, mock_faiss_index):
        """Test finding similar documents with non-existent document ID."""
        search_service._document_index = sample_document_index
        search_service._faiss_index = mock_faiss_index
        
        results = await search_service.get_similar_documents("nonexistent", limit=2)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_get_similar_documents_no_embedding(self, search_service, sample_document_index, mock_faiss_index):
        """Test finding similar documents when reference has no embedding."""
        # Create a chunk without embedding
        chunk_no_embedding = DocumentChunk(
            id="no_embedding",
            title="No Embedding",
            content="Content without embedding",
            source_url="https://example.com",
            section="Test",
            file_path="/test.md",
            last_modified=datetime.now(),
            embedding=None
        )
        
        sample_document_index.chunks.append(chunk_no_embedding)
        search_service._document_index = sample_document_index
        search_service._faiss_index = mock_faiss_index
        
        results = await search_service.get_similar_documents("no_embedding", limit=2)
        
        assert results == []
    
    def test_get_index_stats_no_index(self, search_service):
        """Test getting index stats when no index is loaded."""
        stats = search_service.get_index_stats()
        
        assert stats == {"status": "no_index_loaded"}
    
    def test_get_index_stats_with_index(self, search_service, sample_document_index):
        """Test getting index stats with loaded index."""
        search_service._document_index = sample_document_index
        
        stats = search_service.get_index_stats()
        
        assert stats["status"] == "loaded"
        assert stats["version"] == sample_document_index.version
        assert stats["total_chunks"] == len(sample_document_index.chunks)
        assert stats["embedding_model"] == sample_document_index.embedding_model
        assert "unique_documents" in stats
        assert "unique_sections" in stats
        assert "last_updated" in stats


class TestSearchServiceIntegration:
    """Integration tests for SearchService with real components."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_search_workflow(self, temp_index_dir):
        """Test complete search workflow with real sentence transformer."""
        # This test requires actual model loading and is marked as slow
        service = SearchService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_index_dir,
            max_snippet_length=200
        )
        
        # Create sample documents
        now = datetime.now()
        chunks = [
            DocumentChunk(
                id="test1",
                title="Python Guide",
                content="Python is a programming language. It's great for machine learning and data science.",
                source_url="https://example.com/python.md",
                section="Introduction",
                file_path="/python.md",
                last_modified=now
            ),
            DocumentChunk(
                id="test2",
                title="JavaScript Guide",
                content="JavaScript is a programming language. It's great for web development and frontend applications.",
                source_url="https://example.com/js.md",
                section="Introduction",
                file_path="/js.md",
                last_modified=now
            )
        ]
        
        # Create embeddings
        embeddings = await service.indexing_service.create_embeddings([chunk.content for chunk in chunks])
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i].tolist()
        
        # Create document index
        doc_index = DocumentIndex(
            version="test_version",
            last_updated=now,
            chunks=chunks,
            embedding_model="all-MiniLM-L6-v2"
        )
        
        # Build FAISS index
        faiss_index = service.indexing_service.build_faiss_index(doc_index)
        
        # Set up service
        service._document_index = doc_index
        service._faiss_index = faiss_index
        
        # Perform search
        query = SearchQuery(query="machine learning", limit=5, min_score=0.1)
        results = await service.semantic_search(query)
        
        # Verify results
        assert len(results) > 0
        assert results[0].title == "Python Guide"  # Should rank higher for ML query
        assert "machine learning" in results[0].snippet.lower()