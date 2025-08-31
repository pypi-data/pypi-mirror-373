"""Document indexing and embedding service."""

import asyncio
import hashlib
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    # Mock SentenceTransformer for development/testing
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
        
        def encode(self, texts, convert_to_numpy=True):
            # Return dummy embeddings for testing
            if isinstance(texts, str):
                texts = [texts]
            embeddings = np.random.rand(len(texts), 384).astype(np.float32)
            return embeddings if convert_to_numpy else embeddings.tolist()

from ..models.documentation import DocumentChunk, DocumentIndex
from ..utils.file_utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class DocumentIndexingService:
    """Service for creating and managing document embeddings and FAISS index."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_dir: Optional[str] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """Initialize the indexing service.
        
        Args:
            model_name: Name of the sentence transformer model
            index_dir: Directory to store FAISS indexes (defaults to user cache dir)
            chunk_size: Maximum size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.model_name = model_name
        
        # Use user cache directory if none provided
        if index_dir is None:
            import platformdirs
            index_dir = str(Path(platformdirs.user_cache_dir("strands-mcp-server")) / "indexes")
        
        self.index_dir = Path(index_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize sentence transformer model
        self._model: Optional[SentenceTransformer] = None
        self._faiss_index: Optional[faiss.IndexFlatIP] = None
        self._document_index: Optional[DocumentIndex] = None
        
        # Ensure index directory exists (sync version for __init__)
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def _chunk_text(self, text: str, title: str = "") -> List[str]:
        """Split text into overlapping chunks for better search granularity.
        
        Args:
            text: Text to chunk
            title: Document title to prepend to chunks
            
        Returns:
            List of text chunks
        """
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # If text is shorter than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [f"{title}\n\n{text}" if title else text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at word boundary
            if end < len(text):
                # Look for the last space within the chunk
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                # Prepend title to first chunk only
                if start == 0 and title:
                    chunk = f"{title}\n\n{chunk}"
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def _generate_chunk_id(self, content: str, source_url: str, section: str) -> str:
        """Generate a unique ID for a document chunk."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        url_hash = hashlib.md5(source_url.encode('utf-8')).hexdigest()[:8]
        return f"{url_hash}_{section}_{content_hash}"
    
    async def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        logger.info(f"Creating embeddings for {len(texts)} text chunks")
        
        # Run embedding generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def encode_texts():
            return self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
        
        embeddings = await loop.run_in_executor(None, encode_texts)
        
        return embeddings
    
    def _create_document_chunks(
        self, 
        content: str, 
        title: str, 
        source_url: str, 
        file_path: str,
        last_modified: datetime
    ) -> List[DocumentChunk]:
        """Create document chunks from content.
        
        Args:
            content: Document content
            title: Document title
            source_url: Source URL
            file_path: Local file path
            last_modified: Last modification time
            
        Returns:
            List of DocumentChunk objects
        """
        # Extract sections from markdown content
        sections = self._extract_sections(content)
        chunks = []
        
        for section_title, section_content in sections.items():
            # Chunk the section content
            text_chunks = self._chunk_text(section_content, section_title)
            
            for i, chunk_text in enumerate(text_chunks):
                chunk_id = self._generate_chunk_id(chunk_text, source_url, section_title)
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    title=title,
                    content=chunk_text,
                    source_url=source_url,
                    section=section_title,
                    file_path=file_path,
                    last_modified=last_modified
                )
                chunks.append(chunk)
        
        return chunks
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Dictionary mapping section titles to content
        """
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for markdown headers
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.lstrip('#').strip() or "Untitled"
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v.strip()}
    
    async def index_documents(
        self, 
        documents: List[Tuple[str, str, str, str, datetime]]
    ) -> DocumentIndex:
        """Index a list of documents.
        
        Args:
            documents: List of tuples (content, title, source_url, file_path, last_modified)
            
        Returns:
            DocumentIndex with embedded chunks
        """
        logger.info(f"Indexing {len(documents)} documents")
        
        all_chunks = []
        all_texts = []
        
        # Create chunks for all documents
        for content, title, source_url, file_path, last_modified in documents:
            chunks = self._create_document_chunks(
                content, title, source_url, file_path, last_modified
            )
            all_chunks.extend(chunks)
            all_texts.extend([chunk.content for chunk in chunks])
        
        # Generate embeddings for all chunks
        if all_texts:
            embeddings = await self.create_embeddings(all_texts)
            
            # Assign embeddings to chunks
            if len(embeddings) != len(all_chunks):
                raise ValueError(f"Mismatch between embeddings ({len(embeddings)}) and chunks ({len(all_chunks)})")
            
            for i, chunk in enumerate(all_chunks):
                chunk.embedding = embeddings[i].tolist()
        
        # Create document index with microsecond precision for version
        now = datetime.now()
        document_index = DocumentIndex(
            version=now.strftime("%Y%m%d_%H%M%S_%f"),
            last_updated=now,
            chunks=all_chunks,
            embedding_model=self.model_name
        )
        
        # Build FAISS index
        faiss_index = self.build_faiss_index(document_index)
        
        # Save both indexes to disk
        self.save_index(document_index, faiss_index)
        
        logger.info(f"Created and saved index with {len(all_chunks)} chunks")
        return document_index
    
    def build_faiss_index(self, document_index: DocumentIndex) -> faiss.IndexFlatIP:
        """Build FAISS index from document embeddings.
        
        Args:
            document_index: Document index with embeddings
            
        Returns:
            FAISS index
        """
        if not document_index.chunks:
            raise ValueError("No chunks to index")
        
        # Extract embeddings
        embeddings = []
        for chunk in document_index.chunks:
            if chunk.embedding is None:
                raise ValueError(f"Chunk {chunk.id} has no embedding")
            embeddings.append(chunk.embedding)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Create FAISS index
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(embeddings_array)
        
        logger.info(f"Built FAISS index with {index.ntotal} vectors, dimension {dimension}")
        return index
    
    def save_index(self, document_index: DocumentIndex, faiss_index: faiss.IndexFlatIP) -> None:
        """Save document index and FAISS index to disk.
        
        Args:
            document_index: Document index to save
            faiss_index: FAISS index to save
        """
        # Save document index as JSON
        index_file = self.index_dir / f"document_index_{document_index.version}.json"
        document_index.save_to_file(str(index_file))
        
        # Save FAISS index
        faiss_file = self.index_dir / f"faiss_index_{document_index.version}.index"
        faiss.write_index(faiss_index, str(faiss_file))
        
        # Create symlinks to latest
        latest_index_file = self.index_dir / "document_index_latest.json"
        latest_faiss_file = self.index_dir / "faiss_index_latest.index"
        
        # Remove existing symlinks
        for link_file in [latest_index_file, latest_faiss_file]:
            if link_file.exists():
                link_file.unlink()
        
        # Create new symlinks
        latest_index_file.symlink_to(index_file.name)
        latest_faiss_file.symlink_to(faiss_file.name)
        
        logger.info(f"Saved index to {index_file} and {faiss_file}")
    
    def load_latest_index(self) -> Tuple[Optional[DocumentIndex], Optional[faiss.IndexFlatIP]]:
        """Load the latest document and FAISS indexes.
        
        Returns:
            Tuple of (DocumentIndex, FAISS index) or (None, None) if not found
        """
        latest_index_file = self.index_dir / "document_index_latest.json"
        latest_faiss_file = self.index_dir / "faiss_index_latest.index"
        
        if not latest_index_file.exists() or not latest_faiss_file.exists():
            logger.info("No existing index found")
            return None, None
        
        try:
            # Load document index
            document_index = DocumentIndex.load_from_file(str(latest_index_file))
            
            # Load FAISS index
            faiss_index = faiss.read_index(str(latest_faiss_file))
            
            logger.info(f"Loaded index version {document_index.version} with {len(document_index.chunks)} chunks")
            return document_index, faiss_index
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return None, None
    
    async def update_index_incremental(
        self, 
        new_documents: List[Tuple[str, str, str, str, datetime]],
        existing_index: Optional[DocumentIndex] = None
    ) -> DocumentIndex:
        """Update index incrementally with new documents.
        
        Args:
            new_documents: List of new documents to add
            existing_index: Existing document index to update
            
        Returns:
            Updated document index
        """
        if existing_index is None:
            # No existing index, create new one
            return await self.index_documents(new_documents)
        
        logger.info(f"Updating index incrementally with {len(new_documents)} new documents")
        
        # Create chunks for new documents
        new_chunks = []
        new_texts = []
        
        for content, title, source_url, file_path, last_modified in new_documents:
            chunks = self._create_document_chunks(
                content, title, source_url, file_path, last_modified
            )
            new_chunks.extend(chunks)
            new_texts.extend([chunk.content for chunk in chunks])
        
        # Generate embeddings for new chunks
        if new_texts:
            embeddings = await self.create_embeddings(new_texts)
            
            # Assign embeddings to new chunks
            if len(embeddings) != len(new_chunks):
                raise ValueError(f"Mismatch between embeddings ({len(embeddings)}) and chunks ({len(new_chunks)})")
            
            for i, chunk in enumerate(new_chunks):
                chunk.embedding = embeddings[i].tolist()
        
        # Combine with existing chunks
        all_chunks = existing_index.chunks + new_chunks
        
        # Create updated document index with microsecond precision for version
        now = datetime.now()
        updated_index = DocumentIndex(
            version=now.strftime("%Y%m%d_%H%M%S_%f"),
            last_updated=now,
            chunks=all_chunks,
            embedding_model=self.model_name
        )
        
        logger.info(f"Updated index now has {len(all_chunks)} chunks")
        return updated_index