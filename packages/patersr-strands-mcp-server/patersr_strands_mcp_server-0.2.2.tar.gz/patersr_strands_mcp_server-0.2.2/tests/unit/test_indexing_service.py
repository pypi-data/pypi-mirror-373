"""Tests for the document indexing service."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest
import faiss

from src.strands_mcp.services.indexing_service import DocumentIndexingService
from src.strands_mcp.models.documentation import DocumentChunk, DocumentIndex


@pytest.fixture
def temp_index_dir():
    """Create a temporary directory for index storage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def indexing_service(temp_index_dir):
    """Create an indexing service with temporary directory."""
    return DocumentIndexingService(
        model_name="all-MiniLM-L6-v2",
        index_dir=temp_index_dir,
        chunk_size=100,
        chunk_overlap=20
    )


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        (
            "# Introduction\nThis is the introduction to Strands SDK.\n\n# Getting Started\nHere's how to get started with Strands.",
            "Strands SDK Guide",
            "https://github.com/strands-agents/docs/blob/main/guide.md",
            "/path/to/guide.md",
            datetime(2024, 1, 1, 12, 0, 0)
        ),
        (
            "# API Reference\nThe Strands API provides methods for agent creation.\n\n# Examples\nHere are some examples.",
            "API Documentation",
            "https://github.com/strands-agents/docs/blob/main/api.md",
            "/path/to/api.md",
            datetime(2024, 1, 2, 12, 0, 0)
        )
    ]


class TestDocumentIndexingService:
    """Test cases for DocumentIndexingService."""
    
    def test_initialization(self, temp_index_dir):
        """Test service initialization."""
        service = DocumentIndexingService(
            model_name="test-model",
            index_dir=temp_index_dir,
            chunk_size=200,
            chunk_overlap=30
        )
        
        assert service.model_name == "test-model"
        assert service.index_dir == Path(temp_index_dir)
        assert service.chunk_size == 200
        assert service.chunk_overlap == 30
        assert Path(temp_index_dir).exists()
    
    def test_chunk_text_short(self, indexing_service):
        """Test text chunking with short text."""
        text = "This is a short text."
        title = "Test Title"
        
        chunks = indexing_service._chunk_text(text, title)
        
        assert len(chunks) == 1
        assert chunks[0] == f"{title}\n\n{text}"
    
    def test_chunk_text_long(self, indexing_service):
        """Test text chunking with long text."""
        # Create text longer than chunk_size (100)
        text = "This is a very long text that should be split into multiple chunks. " * 5
        title = "Test Title"
        
        chunks = indexing_service._chunk_text(text, title)
        
        assert len(chunks) > 1
        assert chunks[0].startswith(title)
        
        # Check that chunks have reasonable overlap
        for i in range(len(chunks) - 1):
            # Some overlap should exist between consecutive chunks
            assert len(chunks[i]) <= indexing_service.chunk_size + 50  # Allow some flexibility
    
    def test_chunk_text_no_title(self, indexing_service):
        """Test text chunking without title."""
        text = "This is a text without title."
        
        chunks = indexing_service._chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_generate_chunk_id(self, indexing_service):
        """Test chunk ID generation."""
        content = "Test content"
        source_url = "https://example.com/doc.md"
        section = "Test Section"
        
        chunk_id = indexing_service._generate_chunk_id(content, source_url, section)
        
        assert isinstance(chunk_id, str)
        assert len(chunk_id) > 0
        assert "_" in chunk_id
        
        # Same inputs should generate same ID
        chunk_id2 = indexing_service._generate_chunk_id(content, source_url, section)
        assert chunk_id == chunk_id2
        
        # Different inputs should generate different IDs
        chunk_id3 = indexing_service._generate_chunk_id("Different content", source_url, section)
        assert chunk_id != chunk_id3
    
    def test_extract_sections(self, indexing_service):
        """Test section extraction from markdown."""
        content = """# Introduction
This is the introduction.

# Getting Started
Here's how to get started.

## Subsection
This is a subsection.

# Conclusion
This is the conclusion."""
        
        sections = indexing_service._extract_sections(content)
        
        assert "Introduction" in sections
        assert "Getting Started" in sections
        assert "Subsection" in sections
        assert "Conclusion" in sections
        
        assert "This is the introduction." in sections["Introduction"]
        assert "Here's how to get started." in sections["Getting Started"]
    
    def test_extract_sections_no_headers(self, indexing_service):
        """Test section extraction with no headers."""
        content = "This is content without headers."
        
        sections = indexing_service._extract_sections(content)
        
        assert "Introduction" in sections
        assert sections["Introduction"] == content
    
    def test_create_document_chunks(self, indexing_service):
        """Test document chunk creation."""
        content = "# Section 1\nContent for section 1.\n\n# Section 2\nContent for section 2."
        title = "Test Document"
        source_url = "https://example.com/doc.md"
        file_path = "/path/to/doc.md"
        last_modified = datetime(2024, 1, 1, 12, 0, 0)
        
        chunks = indexing_service._create_document_chunks(
            content, title, source_url, file_path, last_modified
        )
        
        assert len(chunks) >= 2  # At least one chunk per section
        
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.title == title
            assert chunk.source_url == source_url
            assert chunk.file_path == file_path
            assert chunk.last_modified == last_modified
            assert chunk.embedding is None  # Not set yet
    
    @pytest.mark.asyncio
    async def test_create_embeddings_empty(self, indexing_service):
        """Test embedding creation with empty input."""
        embeddings = await indexing_service.create_embeddings([])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.size == 0
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.indexing_service.SentenceTransformer')
    async def test_create_embeddings(self, mock_transformer_class, indexing_service):
        """Test embedding creation."""
        # Mock the sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_transformer_class.return_value = mock_model
        
        # Force model reload
        indexing_service._model = None
        
        texts = ["First text", "Second text"]
        embeddings = await indexing_service.create_embeddings(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 3)
        mock_model.encode.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.indexing_service.SentenceTransformer')
    async def test_index_documents(self, mock_transformer_class, indexing_service, sample_documents):
        """Test document indexing."""
        # Pre-calculate the number of chunks that will be created
        total_chunks = 0
        for content, title, source_url, file_path, last_modified in sample_documents:
            chunks = indexing_service._create_document_chunks(
                content, title, source_url, file_path, last_modified
            )
            total_chunks += len(chunks)
        
        # Mock the sentence transformer
        mock_model = Mock()
        mock_embeddings = np.random.rand(total_chunks, 384).astype(np.float32)
        mock_model.encode.return_value = mock_embeddings
        mock_transformer_class.return_value = mock_model
        
        # Force model reload
        indexing_service._model = None
        
        document_index = await indexing_service.index_documents(sample_documents)
        
        assert isinstance(document_index, DocumentIndex)
        assert len(document_index.chunks) > 0
        assert document_index.embedding_model == indexing_service.model_name
        assert document_index.version is not None
        
        # Check that all chunks have embeddings
        for chunk in document_index.chunks:
            assert chunk.embedding is not None
            assert len(chunk.embedding) > 0
    
    def test_build_faiss_index_empty(self, indexing_service):
        """Test FAISS index building with empty document index."""
        document_index = DocumentIndex(
            version="test",
            last_updated=datetime.now(),
            chunks=[],
            embedding_model="test-model"
        )
        
        with pytest.raises(ValueError, match="No chunks to index"):
            indexing_service.build_faiss_index(document_index)
    
    def test_build_faiss_index_no_embeddings(self, indexing_service):
        """Test FAISS index building with chunks without embeddings."""
        chunk = DocumentChunk(
            id="test-chunk",
            title="Test",
            content="Test content",
            source_url="https://example.com",
            section="Test Section",
            file_path="/test.md",
            last_modified=datetime.now(),
            embedding=None
        )
        
        document_index = DocumentIndex(
            version="test",
            last_updated=datetime.now(),
            chunks=[chunk],
            embedding_model="test-model"
        )
        
        with pytest.raises(ValueError, match="has no embedding"):
            indexing_service.build_faiss_index(document_index)
    
    def test_build_faiss_index_success(self, indexing_service):
        """Test successful FAISS index building."""
        # Create chunks with embeddings
        chunks = []
        for i in range(3):
            chunk = DocumentChunk(
                id=f"test-chunk-{i}",
                title="Test",
                content=f"Test content {i}",
                source_url="https://example.com",
                section="Test Section",
                file_path="/test.md",
                last_modified=datetime.now(),
                embedding=[0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i]
            )
            chunks.append(chunk)
        
        document_index = DocumentIndex(
            version="test",
            last_updated=datetime.now(),
            chunks=chunks,
            embedding_model="test-model"
        )
        
        faiss_index = indexing_service.build_faiss_index(document_index)
        
        assert isinstance(faiss_index, faiss.IndexFlatIP)
        assert faiss_index.ntotal == 3
        assert faiss_index.d == 4  # Dimension of embeddings
    
    def test_save_and_load_index(self, indexing_service):
        """Test saving and loading index."""
        # Create a simple document index
        chunk = DocumentChunk(
            id="test-chunk",
            title="Test",
            content="Test content",
            source_url="https://example.com",
            section="Test Section",
            file_path="/test.md",
            last_modified=datetime.now(),
            embedding=[0.1, 0.2, 0.3, 0.4]
        )
        
        document_index = DocumentIndex(
            version="test_version",
            last_updated=datetime.now(),
            chunks=[chunk],
            embedding_model="test-model"
        )
        
        # Build FAISS index
        faiss_index = indexing_service.build_faiss_index(document_index)
        
        # Save index
        indexing_service.save_index(document_index, faiss_index)
        
        # Load index
        loaded_doc_index, loaded_faiss_index = indexing_service.load_latest_index()
        
        assert loaded_doc_index is not None
        assert loaded_faiss_index is not None
        assert loaded_doc_index.version == document_index.version
        assert len(loaded_doc_index.chunks) == len(document_index.chunks)
        assert loaded_faiss_index.ntotal == faiss_index.ntotal
    
    def test_load_index_not_found(self, indexing_service):
        """Test loading index when files don't exist."""
        doc_index, faiss_index = indexing_service.load_latest_index()
        
        assert doc_index is None
        assert faiss_index is None
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.indexing_service.SentenceTransformer')
    async def test_update_index_incremental_no_existing(self, mock_transformer_class, indexing_service, sample_documents):
        """Test incremental update with no existing index."""
        # Pre-calculate the number of chunks that will be created
        total_chunks = 0
        for content, title, source_url, file_path, last_modified in sample_documents:
            chunks = indexing_service._create_document_chunks(
                content, title, source_url, file_path, last_modified
            )
            total_chunks += len(chunks)
        
        # Mock the sentence transformer
        mock_model = Mock()
        mock_embeddings = np.random.rand(total_chunks, 384).astype(np.float32)
        mock_model.encode.return_value = mock_embeddings
        mock_transformer_class.return_value = mock_model
        
        # Force model reload
        indexing_service._model = None
        
        updated_index = await indexing_service.update_index_incremental(sample_documents)
        
        assert isinstance(updated_index, DocumentIndex)
        assert len(updated_index.chunks) > 0
    
    @pytest.mark.asyncio
    @patch('src.strands_mcp.services.indexing_service.SentenceTransformer')
    async def test_update_index_incremental_with_existing(self, mock_transformer_class, indexing_service):
        """Test incremental update with existing index."""
        # Create existing index
        existing_chunk = DocumentChunk(
            id="existing-chunk",
            title="Existing",
            content="Existing content",
            source_url="https://example.com/existing",
            section="Existing Section",
            file_path="/existing.md",
            last_modified=datetime.now(),
            embedding=[0.1, 0.2, 0.3, 0.4]
        )
        
        existing_index = DocumentIndex(
            version="existing",
            last_updated=datetime.now(),
            chunks=[existing_chunk],
            embedding_model="test-model"
        )
        
        # New documents to add
        new_documents = [
            (
                "# New Section\nNew content here.",
                "New Document",
                "https://example.com/new",
                "/new.md",
                datetime.now()
            )
        ]
        
        # Pre-calculate the number of chunks for new documents
        new_chunk_count = 0
        for content, title, source_url, file_path, last_modified in new_documents:
            chunks = indexing_service._create_document_chunks(
                content, title, source_url, file_path, last_modified
            )
            new_chunk_count += len(chunks)
        
        # Mock the sentence transformer
        mock_model = Mock()
        mock_embeddings = np.random.rand(new_chunk_count, 384).astype(np.float32)
        mock_model.encode.return_value = mock_embeddings
        mock_transformer_class.return_value = mock_model
        
        # Force model reload
        indexing_service._model = None
        
        updated_index = await indexing_service.update_index_incremental(new_documents, existing_index)
        
        assert isinstance(updated_index, DocumentIndex)
        assert len(updated_index.chunks) > len(existing_index.chunks)
        
        # Check that existing chunk is still there
        existing_ids = [chunk.id for chunk in existing_index.chunks]
        updated_ids = [chunk.id for chunk in updated_index.chunks]
        
        for existing_id in existing_ids:
            assert existing_id in updated_ids


if __name__ == "__main__":
    pytest.main([__file__])