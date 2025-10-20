"""BM25 Retriever for keyword-based sparse retrieval."""
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple
import re


class BM25Retriever:
    """BM25-based retriever for keyword search."""
    
    def __init__(self, chunks: List[Dict[str, any]]):
        """Initialize BM25 retriever with document chunks."""
        self.chunks = chunks
        
        self.tokenized_chunks = [self._tokenize(chunk['text']) for chunk in chunks]
        
        self.bm25 = BM25Okapi(self.tokenized_chunks)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase, remove punctuation, split on whitespace."""
        text = text.lower()
        
        tokens = re.findall(r'\b\w+\b', text)
        
        return tokens
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, any], float]]:
        """Search for relevant chunks using BM25."""
        query_tokens = self._tokenize(query)
        
        scores = self.bm25.get_scores(query_tokens)
        
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = [(self.chunks[i], float(scores[i])) for i in top_indices]
        
        return results
    
    def search_with_threshold(
        self, 
        query: str, 
        threshold: float = 0.0,
        top_k: int = 10
    ) -> List[Tuple[Dict[str, any], float]]:
        """Search with a minimum score threshold."""
        results = self.search(query, top_k=top_k)
        
        filtered = [(chunk, score) for chunk, score in results if score >= threshold]
        
        return filtered
