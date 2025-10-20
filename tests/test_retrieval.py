"""Tests for the retrieval pipeline (BM25, embeddings, hybrid)."""
import pytest
from src.core.ingestion import IngestionPipeline
from src.core.bm25_retriever import BM25Retriever
from src.core.embedding_retriever import EmbeddingRetriever
from src.core.hybrid_retriever import HybridRetriever


def test_bm25_retrieval():
    """Test BM25 keyword-based retrieval."""
    print("\n" + "="*60)
    print("TEST: BM25 Retrieval")
    print("="*60)
    
    pipeline = IngestionPipeline(chunk_size=512)
    chunks = pipeline.ingest_documents("data/demo", "data/demo/metadata.csv")
    
    print(f"Loaded {len(chunks)} chunks for retrieval")
    
    retriever = BM25Retriever(chunks)
    print(f"Built BM25 index")
    
    query1 = "linear equations slope"
    results1 = retriever.search(query1, top_k=3)
    
    print(f"\nQuery: '{query1}'")
    print(f"Top {len(results1)} results:")
    for i, (chunk, score) in enumerate(results1):
        print(f"\n  {i+1}. Score: {score:.2f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:100]}...")
    
    top_subject = results1[0][0]['metadata'].get('subject')
    assert top_subject == 'Mathematics', f"Expected Math content, got {top_subject}"
    
    query2 = "force mass acceleration Newton"
    results2 = retriever.search(query2, top_k=3)
    
    print(f"\nQuery: '{query2}'")
    print(f"Top {len(results2)} results:")
    for i, (chunk, score) in enumerate(results2):
        print(f"\n  {i+1}. Score: {score:.2f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:100]}...")
    
    top_subject = results2[0][0]['metadata'].get('subject')
    assert top_subject == 'Physics', f"Expected Physics content, got {top_subject}"
    
    query3 = "cell nucleus mitochondria"
    results3 = retriever.search(query3, top_k=3)
    
    print(f"\nQuery: '{query3}'")
    print(f"Top {len(results3)} results:")
    for i, (chunk, score) in enumerate(results3):
        print(f"\n  {i+1}. Score: {score:.2f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:100]}...")
    
    top_subject = results3[0][0]['metadata'].get('subject')
    assert top_subject == 'Biology', f"Expected Biology content, got {top_subject}"
    
    print("\n" + "="*60)
    print("All BM25 tests passed")
    print("="*60)


def test_bm25_threshold():
    """Test BM25 retrieval with score threshold."""
    print("\n" + "="*60)
    print("TEST: BM25 with Threshold")
    print("="*60)
    
    pipeline = IngestionPipeline(chunk_size=512)
    chunks = pipeline.ingest_documents("data/demo", "data/demo/metadata.csv")
    
    retriever = BM25Retriever(chunks)
    
    query = "quadratic equations parabola"
    results = retriever.search_with_threshold(query, threshold=5.0, top_k=10)
    
    print(f"Query: '{query}'")
    print(f"Threshold: 5.0")
    print(f"Results above threshold: {len(results)}")
    
    for chunk, score in results:
        print(f"  Score: {score:.2f} - {chunk['text'][:80]}...")
        assert score >= 5.0, "All scores should be above threshold"
    
    print("\nThreshold filtering works correctly")


def test_embedding_retrieval():
    """Test embedding-based semantic retrieval."""
    print("\n" + "="*60)
    print("TEST: Embedding-Based Semantic Retrieval")
    print("="*60)
    
    pipeline = IngestionPipeline(chunk_size=512)
    chunks = pipeline.ingest_documents("data/demo", "data/demo/metadata.csv")
    
    print(f"Loaded {len(chunks)} chunks for retrieval")
    
    retriever = EmbeddingRetriever(chunks, model_name='all-MiniLM-L6-v2')
    
    query1 = "straight line graphs and slopes"
    results1 = retriever.search(query1, top_k=3)
    
    print(f"\nQuery: '{query1}'")
    print(f"Top {len(results1)} results:")
    for i, (chunk, score) in enumerate(results1):
        print(f"\n  {i+1}. Similarity: {score:.3f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:400]}...")
    
    top_subject = results1[0][0]['metadata'].get('subject')
    print(f"\nTop result is from: {top_subject}")
    
    query2 = "what happens when you push something"
    results2 = retriever.search(query2, top_k=3)
    
    print(f"\nQuery: '{query2}'")
    print(f"Top {len(results2)} results:")
    for i, (chunk, score) in enumerate(results2):
        print(f"\n  {i+1}. Similarity: {score:.3f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:100]}...")
    
    query3 = "powerhouse of the cell energy production"
    results3 = retriever.search(query3, top_k=3)
    
    print(f"\nQuery: '{query3}'")
    print(f"Top {len(results3)} results:")
    for i, (chunk, score) in enumerate(results3):
        print(f"\n  {i+1}. Similarity: {score:.3f}")
        print(f"     Subject: {chunk['metadata'].get('subject', 'N/A')}")
        print(f"     Text: {chunk['text'][:100]}...")
    
    top_text = results3[0][0]['text'].lower()
    assert 'mitochondria' in top_text or 'powerhouse' in top_text, \
        "Should find mitochondria content for energy production query"
    
    print("\n" + "="*60)
    print("All embedding retrieval tests passed")
    print("="*60)


def test_hybrid_retrieval():
    """Test hybrid retrieval combining BM25 and embeddings."""
    print("\n" + "="*60)
    print("TEST: Hybrid Retrieval (BM25 + Embeddings)")
    print("="*60)
    
    pipeline = IngestionPipeline(chunk_size=512)
    chunks = pipeline.ingest_documents("data/demo", "data/demo/metadata.csv")
    
    print(f"Loaded {len(chunks)} chunks for retrieval\n")
    
    retriever = HybridRetriever(chunks, model_name='all-MiniLM-L6-v2')
    
    query = "Newton force acceleration"
    
    print(f"\nQuery: '{query}'")
    print("\nComparing retrieval methods:\n")
    
    bm25_results = retriever.search_bm25_only(query, top_k=3)
    embedding_results = retriever.search_embedding_only(query, top_k=3)
    hybrid_results = retriever.search(query, top_k=3, alpha=0.5)
    
    print("BM25 (keyword) results:")
    for i, (chunk, score) in enumerate(bm25_results, 1):
        print(f"  {i}. Score: {score:.2f} - {chunk['text'][:80]}...")
    
    print("\nEmbedding (semantic) results:")
    for i, (chunk, score) in enumerate(embedding_results, 1):
        print(f"  {i}. Score: {score:.3f} - {chunk['text'][:80]}...")
    
    print("\nHybrid (combined) results:")
    for i, (chunk, score) in enumerate(hybrid_results, 1):
        print(f"  {i}. Score: {score:.4f} - {chunk['text'][:80]}...")
    
    assert len(hybrid_results) > 0, "Hybrid search should return results"
    assert len(hybrid_results) <= 3, "Should not exceed top_k"
    
    print("\n\nTesting different alpha values:")
    print("(alpha=0.0 means all BM25, alpha=1.0 means all embeddings)\n")
    
    for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
        results = retriever.search(query, top_k=1, alpha=alpha)
        top_chunk, top_score = results[0]
        print(f"  alpha={alpha}: Score={top_score:.4f} - {top_chunk['text'][:60]}...")
    
    print("\n" + "="*60)
    print("Hybrid retrieval test passed")
    print("="*60)
