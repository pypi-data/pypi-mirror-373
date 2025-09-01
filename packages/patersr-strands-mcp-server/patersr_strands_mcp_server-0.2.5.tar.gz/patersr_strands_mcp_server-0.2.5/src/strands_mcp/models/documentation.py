"""Data models for documentation and search functionality."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import json


class DocumentChunk(BaseModel):
    """Represents an indexed content piece from documentation."""
    
    id: str = Field(..., description="Unique identifier for the document chunk")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Text content of the chunk")
    source_url: str = Field(..., description="GitHub source URL")
    section: str = Field(..., description="Document section name")
    file_path: str = Field(..., description="Local file path")
    last_modified: datetime = Field(..., description="Last modification timestamp")
    embedding: Optional[List[float]] = Field(None, description="Vector representation")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v
    
    @field_validator('source_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Source URL must be a valid HTTP/HTTPS URL')
        return v
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None and len(v) == 0:
            raise ValueError('Embedding cannot be an empty list')
        return v
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source_url': self.source_url,
            'section': self.section,
            'file_path': self.file_path,
            'last_modified': self.last_modified.isoformat(),
            'embedding': self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentChunk':
        """Create instance from dictionary."""
        if 'last_modified' in data and isinstance(data['last_modified'], str):
            data['last_modified'] = datetime.fromisoformat(data['last_modified'])
        return cls(**data)


class DocumentIndex(BaseModel):
    """Represents the complete document index with metadata."""
    
    version: str = Field(..., description="Index version identifier")
    last_updated: datetime = Field(..., description="Last update timestamp")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="List of document chunks")
    embedding_model: str = Field(..., description="Name of the embedding model used")
    
    @field_validator('version')
    @classmethod
    def version_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Version cannot be empty')
        return v
    
    @field_validator('embedding_model')
    @classmethod
    def embedding_model_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Embedding model cannot be empty')
        return v
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'version': self.version,
            'last_updated': self.last_updated.isoformat(),
            'chunks': [chunk.to_dict() for chunk in self.chunks],
            'embedding_model': self.embedding_model
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentIndex':
        """Create instance from dictionary."""
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        if 'chunks' in data:
            data['chunks'] = [DocumentChunk.from_dict(chunk) for chunk in data['chunks']]
        return cls(**data)
    
    def save_to_file(self, file_path: str) -> None:
        """Save index to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'DocumentIndex':
        """Load index from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class SearchQuery(BaseModel):
    """Represents a search query with validation."""
    
    query: str = Field(..., max_length=1000, description="Search query string")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    min_score: float = Field(0.5, ge=0.0, le=1.0, description="Minimum relevance score")
    
    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class SearchResult(BaseModel):
    """Represents a search result with metadata."""
    
    title: str = Field(..., description="Document title")
    snippet: str = Field(..., description="Relevant content excerpt")
    source_url: str = Field(..., description="Link to full document")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    section: str = Field(..., description="Document section")
    
    @field_validator('snippet')
    @classmethod
    def truncate_snippet(cls, v: str) -> str:
        """Truncate snippet if too long."""
        max_length = 500
        if len(v) > max_length:
            return v[:max_length-3] + "..."
        return v
    
    @field_validator('source_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Source URL must be a valid HTTP/HTTPS URL')
        return v