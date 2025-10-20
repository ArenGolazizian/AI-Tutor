"""Embedding-based retriever using sentence transformers and FAISS."""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Tuple


class EmbeddingRetriever:
    """
    Semantic retriever using sentence embeddings and FAISS vector search.
    
    Uses sentence-transformers to create dense embeddings of text chunks,
    then uses FAISS for efficient similarity search. This captures semantic
    meaning beyond exact keyword matches.
    
    Example:
        >>> chunks = [{"text": "Algebra is math"}, {"text": "Physics is science"}]
        >>> retriever = EmbeddingRetriever(chunks, model_name='all-MiniLM-L6-v2')
        >>> results = retriever.search("mathematical concepts", top_k=5)
    """
    
    def __init__(
        self, 
        chunks: List[Dict[str, any]],
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        """
        Initialize embedding retriever.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            model_name: Sentence-transformer model name
                       'all-MiniLM-L6-v2' is fast and works well for general text (default)
                       'all-mpnet-base-v2' is more accurate but slower
        """
        self.chunks = chunks
        self.model_name = model_name
        
        # Load sentence transformer model
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Generate embeddings for all chunks
        print(f"Generating embeddings for {len(chunks)} chunks...")
        texts = [chunk['text'] for chunk in chunks]
        self.embeddings = self.model.encode(
            texts, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Build FAISS index
        print("Building FAISS index...")
        dimension = self.embeddings.shape[1]
        
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        # Add to index
        self.index.add(self.embeddings)
        
        print(f"✓ FAISS index ready with {self.index.ntotal} vectors")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, any], float]]:
        """
        Search for semantically similar chunks.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by relevance
            Scores are cosine similarities in range [-1, 1], higher is better
            
        Example:
            >>> results = retriever.search("how do cells work", top_k=3)
            >>> for chunk, score in results:
            ...     print(f"Score: {score:.3f} - {chunk['text'][:50]}")
        """
        # Encode query
        query_embedding = self.model.encode(
            [query], 
            convert_to_numpy=True
        )
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Build results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            results.append((self.chunks[idx], float(score)))
        
        return results
    
    def search_with_threshold(
        self, 
        query: str, 
        threshold: float = 0.5,
        top_k: int = 10
    ) -> List[Tuple[Dict[str, any], float]]:
        """
        Search with a minimum similarity threshold.
        
        Args:
            query: Search query
            threshold: Minimum cosine similarity (0.0 to 1.0)
            top_k: Maximum results to consider
            
        Returns:
            List of (chunk, score) tuples above threshold
        """
        results = self.search(query, top_k=top_k)
        
        # Filter by threshold
        filtered = [(chunk, score) for chunk, score in results if score >= threshold]
        
        return filtered
    
    def save_index(self, index_path: str):
        """Save FAISS index to disk."""
        faiss.write_index(self.index, index_path)
        print(f"Saved FAISS index to {index_path}")
    
    def load_index(self, index_path: str):
        """Load FAISS index from disk."""
        self.index = faiss.read_index(index_path)
        print(f"Loaded FAISS index from {index_path}")
