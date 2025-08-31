"""Unit tests for DocumentationService."""

import asyncio
import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import httpx

from src.strands_mcp.services.documentation_service import DocumentationService
from src.strands_mcp.models.documentation import DocumentChunk, DocumentIndex


@pytest.fixture
def doc_service():
    """Create a DocumentationService instance for testing."""
    return DocumentationService(
        cache_dir="test_cache",
        github_repo="test-owner/test-repo",
        github_branch="main",
        max_retries=2,
        base_delay=0.1,
        max_delay=1.0
    )


@pytest.fixture
def sample_github_contents():
    """Sample GitHub API contents response."""
    return [
        {
            "name": "README.md",
            "path": "README.md",
            "type": "file",
            "sha": "abc123"
        },
        {
            "name": "docs",
            "path": "docs",
            "type": "dir"
        },
        {
            "name": "guide.md",
            "path": "docs/guide.md",
            "type": "file",
            "sha": "def456"
        }
    ]


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content."""
    return """# Test Document

This is a test document with some content.

## Section 1

Some content here.

## Section 2

More content here.
"""


@pytest.fixture
def sample_commit_response():
    """Sample GitHub commit API response."""
    return {
        "commit": {
            "committer": {
                "date": "2024-01-15T10:30:00Z"
            }
        }
    }


class TestDocumentationService:
    """Test cases for DocumentationService."""
    
    def test_init(self, doc_service):
        """Test service initialization."""
        assert doc_service.github_repo == "test-owner/test-repo"
        assert doc_service.github_branch == "main"
        assert doc_service.max_retries == 2
        assert doc_service.base_delay == 0.1
        assert doc_service.max_delay == 1.0
        assert doc_service.cache_dir == Path("test_cache")
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        async with DocumentationService() as service:
            assert service.client is not None
        # Client should be closed after exiting context
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_success_first_try(self, doc_service):
        """Test exponential backoff with successful first attempt."""
        mock_operation = AsyncMock(return_value="success")
        
        result = await doc_service._exponential_backoff_retry(mock_operation, "arg1", kwarg1="value1")
        
        assert result == "success"
        mock_operation.assert_called_once_with("arg1", kwarg1="value1")
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_retry_then_success(self, doc_service):
        """Test exponential backoff with retry then success."""
        mock_operation = AsyncMock(side_effect=[
            httpx.RequestError("Network error"),
            "success"
        ])
        
        result = await doc_service._exponential_backoff_retry(mock_operation)
        
        assert result == "success"
        assert mock_operation.call_count == 2
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_all_retries_fail(self, doc_service):
        """Test exponential backoff when all retries fail."""
        mock_operation = AsyncMock(side_effect=httpx.RequestError("Persistent error"))
        
        with pytest.raises(httpx.RequestError, match="Persistent error"):
            await doc_service._exponential_backoff_retry(mock_operation)
        
        assert mock_operation.call_count == doc_service.max_retries
    
    @pytest.mark.asyncio
    async def test_fetch_github_contents(self, doc_service, sample_github_contents):
        """Test fetching GitHub contents."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_github_contents
        mock_response.raise_for_status.return_value = None
        
        with patch.object(doc_service.client, 'get', return_value=mock_response) as mock_get:
            result = await doc_service._fetch_github_contents("docs")
            
            assert result == sample_github_contents
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/test-owner/test-repo/contents/docs",
                params={"ref": "main"}
            )
    
    @pytest.mark.asyncio
    async def test_fetch_file_content(self, doc_service, sample_markdown_content):
        """Test fetching file content."""
        mock_response = MagicMock()
        mock_response.text = sample_markdown_content
        mock_response.raise_for_status.return_value = None
        
        with patch.object(doc_service.client, 'get', return_value=mock_response) as mock_get:
            result = await doc_service._fetch_file_content("docs/guide.md")
            
            assert result == sample_markdown_content
            mock_get.assert_called_once_with(
                "https://raw.githubusercontent.com/test-owner/test-repo/main/docs/guide.md"
            )
    
    @pytest.mark.asyncio
    async def test_get_file_last_modified(self, doc_service, sample_commit_response):
        """Test getting file last modified timestamp."""
        mock_response = MagicMock()
        mock_response.json.return_value = [sample_commit_response]
        mock_response.raise_for_status.return_value = None
        
        with patch.object(doc_service.client, 'get', return_value=mock_response) as mock_get:
            result = await doc_service._get_file_last_modified("docs/guide.md")
            
            expected_date = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
            assert result == expected_date
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/test-owner/test-repo/commits",
                params={
                    "path": "docs/guide.md",
                    "per_page": 1,
                    "sha": "main"
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_file_last_modified_no_commits(self, doc_service):
        """Test getting file last modified when no commits found."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        
        with patch.object(doc_service.client, 'get', return_value=mock_response):
            result = await doc_service._get_file_last_modified("docs/guide.md")
            
            # Should return current time when no commits found
            assert isinstance(result, datetime)
            assert result.tzinfo == timezone.utc
    
    @pytest.mark.asyncio
    async def test_discover_markdown_files(self, doc_service):
        """Test discovering markdown files recursively."""
        # Mock responses for different directory levels
        root_contents = [
            {"name": "README.md", "path": "README.md", "type": "file"},
            {"name": "docs", "path": "docs", "type": "dir"}
        ]
        docs_contents = [
            {"name": "guide.md", "path": "docs/guide.md", "type": "file"},
            {"name": "api.md", "path": "docs/api.md", "type": "file"}
        ]
        
        async def mock_fetch_contents(path=""):
            if path == "":
                return root_contents
            elif path == "docs":
                return docs_contents
            return []
        
        with patch.object(doc_service, '_fetch_github_contents', side_effect=mock_fetch_contents):
            result = await doc_service._discover_markdown_files()
            
            expected = ["README.md", "docs/guide.md", "docs/api.md"]
            assert sorted(result) == sorted(expected)
    
    @pytest.mark.asyncio
    async def test_fetch_latest_docs(self, doc_service, sample_markdown_content):
        """Test fetching latest documentation."""
        markdown_files = ["README.md", "docs/guide.md"]
        
        # Create an async mock for aiofiles.open
        async_mock_file = AsyncMock()
        async_mock_file.__aenter__ = AsyncMock(return_value=async_mock_file)
        async_mock_file.__aexit__ = AsyncMock(return_value=None)
        async_mock_file.write = AsyncMock()
        
        with patch.object(doc_service, '_discover_markdown_files', return_value=markdown_files), \
             patch.object(doc_service, '_fetch_file_content', return_value=sample_markdown_content), \
             patch.object(doc_service, '_get_file_last_modified', return_value=datetime.now(timezone.utc)), \
             patch('aiofiles.open', return_value=async_mock_file), \
             patch('pathlib.Path.mkdir'):
            
            result = await doc_service.fetch_latest_docs()
            
            assert len(result) == 2
            assert all(isinstance(chunk, DocumentChunk) for chunk in result)
            assert result[0].title == "Test Document"
            assert result[0].content == sample_markdown_content
            assert "test-owner/test-repo" in result[0].source_url
    
    @pytest.mark.asyncio
    async def test_check_for_updates_no_local_index(self, doc_service, sample_commit_response):
        """Test checking for updates when no local index exists."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_commit_response
        mock_response.raise_for_status.return_value = None
        
        with patch.object(doc_service.client, 'get', return_value=mock_response), \
             patch.object(Path, 'exists', return_value=False):
            
            result = await doc_service.check_for_updates()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_for_updates_with_newer_remote(self, doc_service, sample_commit_response):
        """Test checking for updates when remote is newer."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_commit_response
        mock_response.raise_for_status.return_value = None
        
        # Create a mock local index with older timestamp
        old_index = DocumentIndex(
            version="1.0",
            last_updated=datetime(2024, 1, 1, tzinfo=timezone.utc),
            chunks=[],
            embedding_model="test-model"
        )
        
        with patch.object(doc_service.client, 'get', return_value=mock_response), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(DocumentIndex, 'load_from_file', return_value=old_index):
            
            result = await doc_service.check_for_updates()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_for_updates_up_to_date(self, doc_service, sample_commit_response):
        """Test checking for updates when local is up to date."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_commit_response
        mock_response.raise_for_status.return_value = None
        
        # Create a mock local index with newer timestamp
        new_index = DocumentIndex(
            version="1.0",
            last_updated=datetime(2024, 2, 1, tzinfo=timezone.utc),
            chunks=[],
            embedding_model="test-model"
        )
        
        with patch.object(doc_service.client, 'get', return_value=mock_response), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(DocumentIndex, 'load_from_file', return_value=new_index):
            
            result = await doc_service.check_for_updates()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_cached_docs_no_index(self, doc_service):
        """Test getting cached docs when no index exists."""
        with patch.object(Path, 'exists', return_value=False):
            result = await doc_service.get_cached_docs()
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cached_docs_success(self, doc_service):
        """Test successfully getting cached docs."""
        sample_chunks = [
            DocumentChunk(
                id="test:1",
                title="Test Doc",
                content="Test content",
                source_url="https://github.com/test/test",
                section="General",
                file_path="/test/path",
                last_modified=datetime.now(timezone.utc)
            )
        ]
        
        mock_index = DocumentIndex(
            version="1.0",
            last_updated=datetime.now(timezone.utc),
            chunks=sample_chunks,
            embedding_model="test-model"
        )
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(DocumentIndex, 'load_from_file', return_value=mock_index):
            
            result = await doc_service.get_cached_docs()
            assert result == sample_chunks
    
    @pytest.mark.asyncio
    async def test_save_docs_to_cache(self, doc_service):
        """Test saving docs to cache."""
        sample_chunks = [
            DocumentChunk(
                id="test:1",
                title="Test Doc",
                content="Test content",
                source_url="https://github.com/test/test",
                section="General",
                file_path="/test/path",
                last_modified=datetime.now(timezone.utc)
            )
        ]
        
        with patch.object(DocumentIndex, 'save_to_file') as mock_save, \
             patch.object(doc_service.cache_manager, 'add_to_cache') as mock_add_cache:
            
            await doc_service.save_docs_to_cache(sample_chunks)
            
            mock_save.assert_called_once()
            mock_add_cache.assert_called_once_with(
                cache_key="documentation_index",
                file_path=doc_service.cache_dir / "index.json",
                metadata={
                    "repo": "test-owner/test-repo",
                    "branch": "main",
                    "chunk_count": 1
                }
            )
    
    @pytest.mark.asyncio
    async def test_is_cache_valid(self, doc_service):
        """Test checking if cache is valid."""
        with patch.object(doc_service.cache_manager, 'is_cache_valid', return_value=True) as mock_valid:
            result = await doc_service.is_cache_valid()
            
            assert result is True
            mock_valid.assert_called_once_with("documentation_index")
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self, doc_service):
        """Test invalidating cache."""
        with patch.object(doc_service.cache_manager, 'remove_from_cache', return_value=True) as mock_remove:
            result = await doc_service.invalidate_cache()
            
            assert result is True
            mock_remove.assert_called_once_with("documentation_index")
    
    @pytest.mark.asyncio
    async def test_cleanup_cache(self, doc_service):
        """Test cleaning up cache."""
        with patch.object(doc_service.cache_manager, 'cleanup_expired_items', return_value=2) as mock_expired, \
             patch.object(doc_service.cache_manager, 'cleanup_by_size', return_value=1) as mock_size:
            
            result = await doc_service.cleanup_cache()
            
            assert result == 3
            mock_expired.assert_called_once()
            mock_size.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cache_info(self, doc_service):
        """Test getting cache information."""
        mock_index = DocumentIndex(
            version="1.0",
            last_updated=datetime(2024, 1, 15, tzinfo=timezone.utc),
            chunks=[],
            embedding_model="test-model"
        )
        
        with patch.object(doc_service.cache_manager, 'get_cache_size_mb', return_value=1.5), \
             patch.object(doc_service, 'is_cache_valid', return_value=True), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(DocumentIndex, 'load_from_file', return_value=mock_index):
            
            result = await doc_service.get_cache_info()
            
            assert result["cache_size_mb"] == 1.5
            assert result["cache_valid"] is True
            assert result["index_exists"] is True
            assert result["chunk_count"] == 0
            assert result["version"] == "1.0"
            assert result["embedding_model"] == "test-model"
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, doc_service):
        """Test clearing all cache."""
        with patch.object(doc_service.cache_manager, 'clear_cache', return_value=5) as mock_clear:
            result = await doc_service.clear_cache()
            
            assert result == 5
            mock_clear.assert_called_once()
    
    def test_extract_title_from_content(self, doc_service, sample_markdown_content):
        """Test extracting title from markdown content."""
        result = doc_service._extract_title_from_content(sample_markdown_content, "test.md")
        assert result == "Test Document"
    
    def test_extract_title_from_content_no_h1(self, doc_service):
        """Test extracting title when no H1 heading exists."""
        content = "Some content without H1 heading"
        result = doc_service._extract_title_from_content(content, "my-test-file.md")
        assert result == "My Test File"
    
    def test_extract_section_from_path(self, doc_service):
        """Test extracting section from file path."""
        result = doc_service._extract_section_from_path("docs/api-reference/guide.md")
        assert result == "Docs"
    
    def test_extract_section_from_path_root(self, doc_service):
        """Test extracting section from root file path."""
        result = doc_service._extract_section_from_path("README.md")
        assert result == "General"


@pytest.mark.asyncio
async def test_documentation_service_integration():
    """Integration test for DocumentationService with mocked HTTP responses."""
    service = DocumentationService(
        cache_dir="test_integration_cache",
        github_repo="test/repo",
        max_retries=1,
        base_delay=0.01
    )
    
    # Mock all HTTP responses
    mock_contents = [{"name": "test.md", "path": "test.md", "type": "file"}]
    mock_content = "# Test\nContent here"
    mock_commit = {"commit": {"committer": {"date": "2024-01-15T10:30:00Z"}}}
    
    # Create an async mock for aiofiles.open
    async_mock_file = AsyncMock()
    async_mock_file.__aenter__ = AsyncMock(return_value=async_mock_file)
    async_mock_file.__aexit__ = AsyncMock(return_value=None)
    async_mock_file.write = AsyncMock()
    
    with patch.object(service, '_fetch_github_contents', return_value=mock_contents), \
         patch.object(service, '_fetch_file_content', return_value=mock_content), \
         patch.object(service, '_get_file_last_modified', return_value=datetime.now(timezone.utc)), \
         patch('aiofiles.open', return_value=async_mock_file), \
         patch('pathlib.Path.mkdir'):
        
        # Test the full workflow
        chunks = await service.fetch_latest_docs()
        assert len(chunks) == 1
        assert chunks[0].title == "Test"
        
        # Test caching
        await service.save_docs_to_cache(chunks)
        
    await service.close()