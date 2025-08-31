"""Unit tests for documentation models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
import tempfile
import os
import json

from src.strands_mcp.models.documentation import (
    DocumentChunk,
    DocumentIndex,
    SearchQuery,
    SearchResult
)


class TestDocumentChunk:
    """Test cases for DocumentChunk model."""
    
    def test_valid_document_chunk(self):
        """Test creating a valid DocumentChunk."""
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=datetime.now()
        )
        
        assert chunk.id == "test-1"
        assert chunk.title == "Test Document"
        assert chunk.content == "This is test content"
        assert chunk.embedding is None
    
    def test_document_chunk_with_embedding(self):
        """Test DocumentChunk with embedding vector."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=datetime.now(),
            embedding=embedding
        )
        
        assert chunk.embedding == embedding
    
    def test_empty_content_validation(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentChunk(
                id="test-1",
                title="Test Document",
                content="",
                source_url="https://github.com/test/repo",
                section="Introduction",
                file_path="/path/to/file.md",
                last_modified=datetime.now()
            )
        
        assert "Content cannot be empty" in str(exc_info.value)
    
    def test_whitespace_only_content_validation(self):
        """Test that whitespace-only content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentChunk(
                id="test-1",
                title="Test Document",
                content="   \n\t  ",
                source_url="https://github.com/test/repo",
                section="Introduction",
                file_path="/path/to/file.md",
                last_modified=datetime.now()
            )
        
        assert "Content cannot be empty" in str(exc_info.value)
    
    def test_invalid_url_validation(self):
        """Test that invalid URLs raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentChunk(
                id="test-1",
                title="Test Document",
                content="Test content",
                source_url="not-a-url",
                section="Introduction",
                file_path="/path/to/file.md",
                last_modified=datetime.now()
            )
        
        assert "Source URL must be a valid HTTP/HTTPS URL" in str(exc_info.value)
    
    def test_empty_embedding_validation(self):
        """Test that empty embedding list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentChunk(
                id="test-1",
                title="Test Document",
                content="Test content",
                source_url="https://github.com/test/repo",
                section="Introduction",
                file_path="/path/to/file.md",
                last_modified=datetime.now(),
                embedding=[]
            )
        
        assert "Embedding cannot be an empty list" in str(exc_info.value)
    
    def test_to_dict_serialization(self):
        """Test converting DocumentChunk to dictionary."""
        now = datetime.now()
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=now,
            embedding=[0.1, 0.2, 0.3]
        )
        
        result = chunk.to_dict()
        
        assert result['id'] == "test-1"
        assert result['title'] == "Test Document"
        assert result['last_modified'] == now.isoformat()
        assert result['embedding'] == [0.1, 0.2, 0.3]
    
    def test_from_dict_deserialization(self):
        """Test creating DocumentChunk from dictionary."""
        now = datetime.now()
        data = {
            'id': "test-1",
            'title': "Test Document",
            'content': "This is test content",
            'source_url': "https://github.com/test/repo",
            'section': "Introduction",
            'file_path': "/path/to/file.md",
            'last_modified': now.isoformat(),
            'embedding': [0.1, 0.2, 0.3]
        }
        
        chunk = DocumentChunk.from_dict(data)
        
        assert chunk.id == "test-1"
        assert chunk.title == "Test Document"
        assert chunk.last_modified == now
        assert chunk.embedding == [0.1, 0.2, 0.3]


class TestDocumentIndex:
    """Test cases for DocumentIndex model."""
    
    def test_valid_document_index(self):
        """Test creating a valid DocumentIndex."""
        now = datetime.now()
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=now
        )
        
        index = DocumentIndex(
            version="1.0.0",
            last_updated=now,
            chunks=[chunk],
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        assert index.version == "1.0.0"
        assert len(index.chunks) == 1
        assert index.chunks[0].id == "test-1"
    
    def test_empty_version_validation(self):
        """Test that empty version raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentIndex(
                version="",
                last_updated=datetime.now(),
                embedding_model="test-model"
            )
        
        assert "Version cannot be empty" in str(exc_info.value)
    
    def test_empty_embedding_model_validation(self):
        """Test that empty embedding model raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentIndex(
                version="1.0.0",
                last_updated=datetime.now(),
                embedding_model=""
            )
        
        assert "Embedding model cannot be empty" in str(exc_info.value)
    
    def test_to_dict_serialization(self):
        """Test converting DocumentIndex to dictionary."""
        now = datetime.now()
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=now
        )
        
        index = DocumentIndex(
            version="1.0.0",
            last_updated=now,
            chunks=[chunk],
            embedding_model="test-model"
        )
        
        result = index.to_dict()
        
        assert result['version'] == "1.0.0"
        assert result['last_updated'] == now.isoformat()
        assert len(result['chunks']) == 1
        assert result['chunks'][0]['id'] == "test-1"
    
    def test_from_dict_deserialization(self):
        """Test creating DocumentIndex from dictionary."""
        now = datetime.now()
        data = {
            'version': "1.0.0",
            'last_updated': now.isoformat(),
            'chunks': [{
                'id': "test-1",
                'title': "Test Document",
                'content': "This is test content",
                'source_url': "https://github.com/test/repo",
                'section': "Introduction",
                'file_path': "/path/to/file.md",
                'last_modified': now.isoformat(),
                'embedding': None
            }],
            'embedding_model': "test-model"
        }
        
        index = DocumentIndex.from_dict(data)
        
        assert index.version == "1.0.0"
        assert index.last_updated == now
        assert len(index.chunks) == 1
        assert index.chunks[0].id == "test-1"
    
    def test_save_and_load_file(self):
        """Test saving and loading DocumentIndex to/from file."""
        now = datetime.now()
        chunk = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content",
            source_url="https://github.com/test/repo",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=now
        )
        
        original_index = DocumentIndex(
            version="1.0.0",
            last_updated=now,
            chunks=[chunk],
            embedding_model="test-model"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Save to file
            original_index.save_to_file(temp_path)
            
            # Load from file
            loaded_index = DocumentIndex.load_from_file(temp_path)
            
            assert loaded_index.version == original_index.version
            assert loaded_index.last_updated == original_index.last_updated
            assert len(loaded_index.chunks) == len(original_index.chunks)
            assert loaded_index.chunks[0].id == original_index.chunks[0].id
        finally:
            os.unlink(temp_path)


class TestSearchQuery:
    """Test cases for SearchQuery model."""
    
    def test_valid_search_query(self):
        """Test creating a valid SearchQuery."""
        query = SearchQuery(
            query="test search",
            limit=5,
            min_score=0.7
        )
        
        assert query.query == "test search"
        assert query.limit == 5
        assert query.min_score == 0.7
    
    def test_default_values(self):
        """Test SearchQuery with default values."""
        query = SearchQuery(query="test search")
        
        assert query.query == "test search"
        assert query.limit == 10
        assert query.min_score == 0.5
    
    def test_empty_query_validation(self):
        """Test that empty query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SearchQuery(query="")
        
        assert "Query cannot be empty" in str(exc_info.value)
    
    def test_whitespace_query_validation(self):
        """Test that whitespace-only query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SearchQuery(query="   \n\t  ")
        
        assert "Query cannot be empty" in str(exc_info.value)
    
    def test_query_length_validation(self):
        """Test query length validation."""
        # Test maximum length
        long_query = "a" * 1001
        with pytest.raises(ValidationError):
            SearchQuery(query=long_query)
    
    def test_limit_validation(self):
        """Test limit validation."""
        # Test minimum limit
        with pytest.raises(ValidationError):
            SearchQuery(query="test", limit=0)
        
        # Test maximum limit
        with pytest.raises(ValidationError):
            SearchQuery(query="test", limit=101)
    
    def test_min_score_validation(self):
        """Test min_score validation."""
        # Test minimum score
        with pytest.raises(ValidationError):
            SearchQuery(query="test", min_score=-0.1)
        
        # Test maximum score
        with pytest.raises(ValidationError):
            SearchQuery(query="test", min_score=1.1)
    
    def test_query_trimming(self):
        """Test that query is trimmed of whitespace."""
        query = SearchQuery(query="  test search  ")
        assert query.query == "test search"


class TestSearchResult:
    """Test cases for SearchResult model."""
    
    def test_valid_search_result(self):
        """Test creating a valid SearchResult."""
        result = SearchResult(
            title="Test Document",
            snippet="This is a test snippet",
            source_url="https://github.com/test/repo",
            relevance_score=0.85,
            section="Introduction"
        )
        
        assert result.title == "Test Document"
        assert result.snippet == "This is a test snippet"
        assert result.relevance_score == 0.85
    
    def test_snippet_truncation(self):
        """Test that long snippets are truncated."""
        long_snippet = "a" * 600
        result = SearchResult(
            title="Test Document",
            snippet=long_snippet,
            source_url="https://github.com/test/repo",
            relevance_score=0.85,
            section="Introduction"
        )
        
        assert len(result.snippet) == 500
        assert result.snippet.endswith("...")
    
    def test_invalid_url_validation(self):
        """Test that invalid URLs raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(
                title="Test Document",
                snippet="Test snippet",
                source_url="not-a-url",
                relevance_score=0.85,
                section="Introduction"
            )
        
        assert "Source URL must be a valid HTTP/HTTPS URL" in str(exc_info.value)
    
    def test_relevance_score_validation(self):
        """Test relevance score validation."""
        # Test minimum score
        with pytest.raises(ValidationError):
            SearchResult(
                title="Test Document",
                snippet="Test snippet",
                source_url="https://github.com/test/repo",
                relevance_score=-0.1,
                section="Introduction"
            )
        
        # Test maximum score
        with pytest.raises(ValidationError):
            SearchResult(
                title="Test Document",
                snippet="Test snippet",
                source_url="https://github.com/test/repo",
                relevance_score=1.1,
                section="Introduction"
            )


class TestEdgeCases:
    """Test edge cases and integration scenarios."""
    
    def test_document_chunk_round_trip_serialization(self):
        """Test that DocumentChunk can be serialized and deserialized without data loss."""
        now = datetime.now()
        original = DocumentChunk(
            id="test-1",
            title="Test Document",
            content="This is test content with special chars: éñ中文",
            source_url="https://github.com/test/repo/blob/main/file.md",
            section="Introduction",
            file_path="/path/to/file.md",
            last_modified=now,
            embedding=[0.1, 0.2, 0.3, -0.4, 0.5]
        )
        
        # Serialize to dict and back
        data = original.to_dict()
        restored = DocumentChunk.from_dict(data)
        
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.content == original.content
        assert restored.source_url == original.source_url
        assert restored.section == original.section
        assert restored.file_path == original.file_path
        assert restored.last_modified == original.last_modified
        assert restored.embedding == original.embedding
    
    def test_document_index_with_empty_chunks(self):
        """Test DocumentIndex with no chunks."""
        now = datetime.now()
        index = DocumentIndex(
            version="1.0.0",
            last_updated=now,
            chunks=[],
            embedding_model="test-model"
        )
        
        assert len(index.chunks) == 0
        
        # Test serialization
        data = index.to_dict()
        restored = DocumentIndex.from_dict(data)
        assert len(restored.chunks) == 0
    
    def test_search_query_boundary_values(self):
        """Test SearchQuery with boundary values."""
        # Test minimum valid values
        query = SearchQuery(
            query="a",
            limit=1,
            min_score=0.0
        )
        assert query.query == "a"
        assert query.limit == 1
        assert query.min_score == 0.0
        
        # Test maximum valid values
        query = SearchQuery(
            query="a" * 1000,
            limit=100,
            min_score=1.0
        )
        assert len(query.query) == 1000
        assert query.limit == 100
        assert query.min_score == 1.0
    
    def test_search_result_with_unicode_content(self):
        """Test SearchResult with Unicode content."""
        result = SearchResult(
            title="文档标题 - Document Title",
            snippet="This contains Unicode: éñ中文 and emojis: 🚀📚",
            source_url="https://github.com/test/repo",
            relevance_score=0.95,
            section="国际化 Section"
        )
        
        assert "文档" in result.title
        assert "中文" in result.snippet
        assert "🚀" in result.snippet
        assert "国际化" in result.section
    
    def test_document_index_file_operations_with_unicode(self):
        """Test file operations with Unicode content."""
        now = datetime.now()
        chunk = DocumentChunk(
            id="unicode-test",
            title="Unicode Document: 中文测试",
            content="Content with Unicode: éñ中文 and special chars: ñáéíóú",
            source_url="https://github.com/test/repo",
            section="测试部分",
            file_path="/path/to/unicode-file.md",
            last_modified=now
        )
        
        index = DocumentIndex(
            version="1.0.0-unicode",
            last_updated=now,
            chunks=[chunk],
            embedding_model="multilingual-model"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            # Save and load with Unicode content
            index.save_to_file(temp_path)
            loaded_index = DocumentIndex.load_from_file(temp_path)
            
            assert loaded_index.chunks[0].title == chunk.title
            assert loaded_index.chunks[0].content == chunk.content
            assert loaded_index.chunks[0].section == chunk.section
            assert "中文" in loaded_index.chunks[0].title
        finally:
            os.unlink(temp_path)