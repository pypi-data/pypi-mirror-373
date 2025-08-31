"""Search service for semantic search over documentation."""

import asyncio
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple

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

from ..models.documentation import DocumentIndex, SearchQuery, SearchResult
from .indexing_service import DocumentIndexingService
from ..utils.error_handler import ErrorHandler, handle_errors
from ..utils.errors import SearchError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class SearchService:
    """Service for performing semantic search over indexed documentation."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_dir: str = "data/indexes",
        max_snippet_length: int = 300
    ):
        """Initialize the search service.
        
        Args:
            model_name: Name of the sentence transformer model
            index_dir: Directory containing FAISS indexes
            max_snippet_length: Maximum length of result snippets
        """
        self.model_name = model_name
        self.index_dir = Path(index_dir)
        self.max_snippet_length = max_snippet_length
        
        # Initialize components
        self._model: Optional[SentenceTransformer] = None
        self._document_index: Optional[DocumentIndex] = None
        self._faiss_index: Optional[faiss.IndexFlatIP] = None
        self._indexing_service: Optional[DocumentIndexingService] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    @property
    def indexing_service(self) -> DocumentIndexingService:
        """Lazy load the indexing service."""
        if self._indexing_service is None:
            self._indexing_service = DocumentIndexingService(
                model_name=self.model_name,
                index_dir=str(self.index_dir)
            )
        return self._indexing_service
    
    @handle_errors("load_index", "search_service", reraise=False, default_return=False)
    async def load_index(self) -> bool:
        """Load the latest document and FAISS indexes.
        
        Returns:
            True if index was loaded successfully, False otherwise
        """
        try:
            document_index, faiss_index = self.indexing_service.load_latest_index()
            
            if document_index is None or faiss_index is None:
                logger.warning("No index found to load")
                return False
            
            self._document_index = document_index
            self._faiss_index = faiss_index
            
            logger.info(f"Loaded search index with {len(document_index.chunks)} chunks")
            return True
            
        except Exception as e:
            ErrorHandler.log_error(e, "load_index", "search_service")
            return False
    
    def _ensure_index_loaded(self) -> None:
        """Ensure that the search index is loaded."""
        if self._document_index is None or self._faiss_index is None:
            raise SearchError(
                message="Search index not loaded",
                index_status="not_loaded"
            )
    
    async def _create_query_embedding(self, query: str) -> np.ndarray:
        """Create embedding for search query.
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding as numpy array
        """
        loop = asyncio.get_event_loop()
        
        def encode_query():
            embedding = self.model.encode([query], convert_to_numpy=True)
            # Normalize for cosine similarity
            faiss.normalize_L2(embedding)
            return embedding[0]
        
        return await loop.run_in_executor(None, encode_query)
    
    def _extract_snippet(self, content: str, query: str) -> str:
        """Extract relevant snippet from content based on query.
        
        Args:
            content: Full content text
            query: Search query
            
        Returns:
            Relevant snippet with query context
        """
        # Clean content
        content = re.sub(r'\s+', ' ', content.strip())
        
        if len(content) <= self.max_snippet_length:
            return content
        
        # Try to find query terms in content for better snippet extraction
        query_terms = [term.lower().strip() for term in query.split() if len(term.strip()) > 2]
        
        best_position = 0
        best_score = 0
        
        # Look for positions with highest concentration of query terms
        for i in range(0, len(content) - self.max_snippet_length + 1, 50):
            snippet = content[i:i + self.max_snippet_length].lower()
            score = sum(1 for term in query_terms if term in snippet)
            
            if score > best_score:
                best_score = score
                best_position = i
        
        # Extract snippet and try to break at word boundaries
        start = best_position
        end = min(start + self.max_snippet_length, len(content))
        
        # Adjust start to word boundary if not at beginning
        if start > 0:
            space_before = content.rfind(' ', 0, start)
            if space_before > start - 50:  # Don't go too far back
                start = space_before + 1
        
        # Adjust end to word boundary if not at end
        if end < len(content):
            space_after = content.find(' ', end)
            if space_after != -1 and space_after < end + 50:  # Don't go too far forward
                end = space_after
        
        snippet = content[start:end].strip()
        
        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def _rank_results(
        self, 
        results: List[Tuple[int, float]], 
        query: str
    ) -> List[Tuple[int, float]]:
        """Apply additional ranking to search results.
        
        Args:
            results: List of (chunk_index, similarity_score) tuples
            query: Original search query
            
        Returns:
            Re-ranked results
        """
        if not results:
            return results
        
        # For now, we'll use the FAISS similarity scores directly
        # Future enhancements could include:
        # - Boosting results from certain sections (e.g., "Getting Started")
        # - Penalizing very short chunks
        # - Boosting results with exact query term matches
        
        query_terms = set(term.lower().strip() for term in query.split() if len(term.strip()) > 2)
        
        enhanced_results = []
        for chunk_idx, similarity_score in results:
            chunk = self._document_index.chunks[chunk_idx]
            
            # Calculate additional relevance factors
            content_lower = chunk.content.lower()
            
            # Boost for exact term matches
            exact_matches = sum(1 for term in query_terms if term in content_lower)
            exact_match_boost = min(exact_matches * 0.1, 0.3)  # Max 30% boost
            
            # Boost for title matches
            title_boost = 0.0
            if any(term in chunk.title.lower() for term in query_terms):
                title_boost = 0.2
            
            # Boost for section relevance (prioritize certain sections)
            section_boost = 0.0
            important_sections = ["getting started", "quickstart", "overview", "introduction"]
            if any(section in chunk.section.lower() for section in important_sections):
                section_boost = 0.1
            
            # Calculate final score
            final_score = similarity_score + exact_match_boost + title_boost + section_boost
            final_score = min(final_score, 1.0)  # Cap at 1.0
            
            enhanced_results.append((chunk_idx, final_score))
        
        # Sort by enhanced score
        enhanced_results.sort(key=lambda x: x[1], reverse=True)
        
        return enhanced_results
    
    @handle_errors("semantic_search", "search_service")
    async def semantic_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Perform semantic search over indexed documentation.
        
        Args:
            search_query: Search query with parameters
            
        Returns:
            List of search results ranked by relevance
        """
        self._ensure_index_loaded()
        
        logger.info(
            f"Performing semantic search for: '{search_query.query}'",
            extra={
                "extra_fields": {
                    "operation": "semantic_search",
                    "component": "search_service",
                    "query": search_query.query,
                    "limit": search_query.limit,
                    "min_score": search_query.min_score
                }
            }
        )
        
        try:
            # Create query embedding
            query_embedding = await self._create_query_embedding(search_query.query)
            
            # Perform FAISS search
            # Search for more results than requested to allow for filtering
            search_k = min(search_query.limit * 3, len(self._document_index.chunks))
            
            similarities, indices = self._faiss_index.search(
                query_embedding.reshape(1, -1).astype(np.float32),
                search_k
            )
            
            # Convert to list of (index, score) tuples
            raw_results = [
                (int(indices[0][i]), float(similarities[0][i]))
                for i in range(len(indices[0]))
                if similarities[0][i] >= search_query.min_score
            ]
            
            # Apply additional ranking
            ranked_results = self._rank_results(raw_results, search_query.query)
            
            # Convert to SearchResult objects
            search_results = []
            for chunk_idx, relevance_score in ranked_results[:search_query.limit]:
                chunk = self._document_index.chunks[chunk_idx]
                
                # Extract relevant snippet
                snippet = self._extract_snippet(chunk.content, search_query.query)
                
                result = SearchResult(
                    title=chunk.title,
                    snippet=snippet,
                    source_url=chunk.source_url,
                    relevance_score=relevance_score,
                    section=chunk.section
                )
                
                search_results.append(result)
            
            logger.info(
                f"Found {len(search_results)} results for query: '{search_query.query}'",
                extra={
                    "extra_fields": {
                        "operation": "semantic_search",
                        "component": "search_service",
                        "query": search_query.query,
                        "result_count": len(search_results)
                    }
                }
            )
            return search_results
            
        except Exception as e:
            raise SearchError(
                message=f"Semantic search failed: {e}",
                query=search_query.query,
                index_status="loaded" if self._document_index else "not_loaded"
            )
    
    async def get_similar_documents(
        self, 
        document_id: str, 
        limit: int = 5
    ) -> List[SearchResult]:
        """Find documents similar to a given document.
        
        Args:
            document_id: ID of the reference document
            limit: Maximum number of similar documents to return
            
        Returns:
            List of similar documents
        """
        self._ensure_index_loaded()
        
        # Find the reference document
        ref_chunk = None
        ref_index = None
        
        for i, chunk in enumerate(self._document_index.chunks):
            if chunk.id == document_id:
                ref_chunk = chunk
                ref_index = i
                break
        
        if ref_chunk is None:
            logger.warning(f"Document with ID '{document_id}' not found")
            return []
        
        if ref_chunk.embedding is None:
            logger.warning(f"Document '{document_id}' has no embedding")
            return []
        
        try:
            # Use the document's embedding to find similar documents
            ref_embedding = np.array([ref_chunk.embedding], dtype=np.float32)
            faiss.normalize_L2(ref_embedding)
            
            # Search for similar documents (exclude the reference document itself)
            search_k = min(limit + 5, len(self._document_index.chunks))
            similarities, indices = self._faiss_index.search(ref_embedding, search_k)
            
            # Filter out the reference document and convert to results
            similar_results = []
            for i in range(len(indices[0])):
                chunk_idx = int(indices[0][i])
                similarity_score = float(similarities[0][i])
                
                # Skip the reference document itself
                if chunk_idx == ref_index:
                    continue
                
                if len(similar_results) >= limit:
                    break
                
                chunk = self._document_index.chunks[chunk_idx]
                
                # Create a snippet (use first part of content)
                snippet = self._extract_snippet(chunk.content, ref_chunk.title)
                
                result = SearchResult(
                    title=chunk.title,
                    snippet=snippet,
                    source_url=chunk.source_url,
                    relevance_score=similarity_score,
                    section=chunk.section
                )
                
                similar_results.append(result)
            
            logger.info(f"Found {len(similar_results)} similar documents to '{document_id}'")
            return similar_results
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            raise
    
    def get_index_stats(self) -> dict:
        """Get statistics about the loaded index.
        
        Returns:
            Dictionary with index statistics
        """
        if self._document_index is None:
            return {"status": "no_index_loaded"}
        
        return {
            "status": "loaded",
            "version": self._document_index.version,
            "last_updated": self._document_index.last_updated.isoformat(),
            "total_chunks": len(self._document_index.chunks),
            "embedding_model": self._document_index.embedding_model,
            "unique_documents": len(set(chunk.title for chunk in self._document_index.chunks)),
            "unique_sections": len(set(chunk.section for chunk in self._document_index.chunks))
        }