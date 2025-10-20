"""Hybrid retriever combining BM25 and embedding-based search with RRF."""
from typing import List, Dict, Tuple
from src.core.bm25_retriever import BM25Retriever
from src.core.embedding_retriever import EmbeddingRetriever


class HybridRetriever:
    """Hybrid retriever combining keyword (BM25) and semantic (embeddings) search using RRF."""
    
    def __init__(
        self,
        chunks: List[Dict[str, any]],
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        """Initialize hybrid retriever with both BM25 and embedding indices."""
        self.chunks = chunks
        
        print("Initializing BM25 retriever...")
        self.bm25 = BM25Retriever(chunks)
        
        print("Initializing embedding retriever...")
        self.embedding = EmbeddingRetriever(chunks, model_name=model_name)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5,
        bm25_k: int = 20,
        embedding_k: int = 20
    ) -> List[Tuple[Dict[str, any], float]]:
        """Hybrid search using Reciprocal Rank Fusion (RRF)."""
        bm25_results = self.bm25.search(query, top_k=bm25_k)
        embedding_results = self.embedding.search(query, top_k=embedding_k)
        
        rrf_scores = {}
        k_constant = 60
        
        for rank, (chunk, score) in enumerate(bm25_results, start=1):
            chunk_id = id(chunk)
            rrf_score = 1.0 / (k_constant + rank)
            rrf_scores[chunk_id] = {
                'chunk': chunk,
                'bm25_rrf': rrf_score,
                'embedding_rrf': 0.0
            }
        
        for rank, (chunk, score) in enumerate(embedding_results, start=1):
            chunk_id = id(chunk)
            rrf_score = 1.0 / (k_constant + rank)
            
            if chunk_id in rrf_scores:
                rrf_scores[chunk_id]['embedding_rrf'] = rrf_score
            else:
                rrf_scores[chunk_id] = {
                    'chunk': chunk,
                    'bm25_rrf': 0.0,
                    'embedding_rrf': rrf_score
                }
        
        hybrid_results = []
        for chunk_id, data in rrf_scores.items():
            hybrid_score = (
                alpha * data['embedding_rrf'] +
                (1 - alpha) * data['bm25_rrf']
            )
            hybrid_results.append((data['chunk'], hybrid_score))
        
        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        
        return hybrid_results[:top_k]
    
    def search_bm25_only(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, any], float]]:
        """Search using only BM25 (keyword search)."""
        return self.bm25.search(query, top_k=top_k)
    
    def search_embedding_only(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, any], float]]:
        """Search using only embeddings (semantic search)."""
        return self.embedding.search(query, top_k=top_k)
