"""Tests for the 4 educational interaction modes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ingestion import IngestionPipeline
from src.core.hybrid_retriever import HybridRetriever
from src.core.llm_client import LLMClient
from src.core.modes import EducationalModes


def setup_system():
    """Set up the complete system with ingestion, retrieval, and LLM."""
    print("="*80)
    print("Setting up AI-Tutor system...")
    print("="*80)
    
    print("\n1. Ingesting documents...")
    pipeline = IngestionPipeline(chunk_size=512)
    chunks = pipeline.ingest_documents('data/demo', 'data/demo/metadata.csv')
    print(f"   Loaded {len(chunks)} chunks\n")
    
    print("2. Initializing retrieval system...")
    retriever = HybridRetriever(chunks, model_name='all-MiniLM-L6-v2')
    print("   Hybrid retriever ready\n")
    
    print("3. Initializing LLM client...")
    llm = LLMClient()
    print(f"   Using model: {llm.model}\n")
    
    print("4. Initializing educational modes...")
    modes = EducationalModes(retriever, llm, default_grade_level="high")
    print("   All 4 modes ready\n")
    
    return modes


def test_mark_mode(modes):
    """Test the Mark mode (feedback on student answers)."""
    print("\n" + "="*80)
    print("TEST 1: MARK MODE (Feedback & Corrections)")
    print("="*80)
    
    question = "What is Newton's Second Law?"
    student_answer = "Newton's Second Law says that force equals mass times velocity."
    
    print(f"\nQuestion: {question}")
    print(f"Student Answer: {student_answer}")
    print("\nGenerating feedback...\n")
    
    result = modes.mark(
        student_answer=student_answer,
        question=question,
        grade_level="high"
    )
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return False
    
    print("FEEDBACK:")
    print("-" * 80)
    print(result["response"])
    print("-" * 80)
    print(f"\nContext chunks used: {result['context_used']}")
    print(f"Tokens used: {result['tokens_used']}")
    
    return True


def test_explain_mode(modes):
    """Test the Explain mode (simplify concepts)."""
    print("\n" + "="*80)
    print("TEST 2: EXPLAIN MODE (Simplify Concepts)")
    print("="*80)
    
    query = "How do quadratic equations work?"
    
    print(f"\nStudent asks: {query}")
    print("\nGenerating explanation...\n")
    
    result = modes.explain(
        query=query,
        grade_level="middle"
    )
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return False
    
    print("EXPLANATION:")
    print("-" * 80)
    print(result["response"])
    print("-" * 80)
    print(f"\nContext chunks used: {result['context_used']}")
    print(f"Tokens used: {result['tokens_used']}")
    
    return True


def test_example_mode(modes):
    """Test the Example mode (generate practice problems)."""
    print("\n" + "="*80)
    print("TEST 3: EXAMPLE MODE (Practice Problems)")
    print("="*80)
    
    topic = "solving linear equations"
    
    print(f"\nTopic: {topic}")
    print("\nGenerating practice problems...\n")
    
    result = modes.example(
        topic=topic,
        grade_level="high"
    )
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return False
    
    print("PRACTICE PROBLEMS:")
    print("-" * 80)
    print(result["response"])
    print("-" * 80)
    print(f"\nContext chunks used: {result['context_used']}")
    print(f"Tokens used: {result['tokens_used']}")
    
    return True


def test_flashcards_mode(modes):
    """Test the Flashcards mode (study materials)."""
    print("\n" + "="*80)
    print("TEST 4: FLASHCARDS MODE (Study Materials)")
    print("="*80)
    
    topic = "mitochondria and cell organelles"
    
    print(f"\nTopic: {topic}")
    print("\nGenerating flashcards...\n")
    
    result = modes.flashcards(
        topic=topic,
        grade_level="high"
    )
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return False
    
    print("FLASHCARDS:")
    print("-" * 80)
    print(result["response"])
    print("-" * 80)
    print(f"\nContext chunks used: {result['context_used']}")
    print(f"Tokens used: {result['tokens_used']}")
    
    return True


def main():
    """Run all mode tests."""
    print("\n" + "#"*80)
    print("# AI-Tutor Educational Modes Test Suite")
    print("#"*80)
    
    try:
        modes = setup_system()
        
        results = {
            "Mark Mode": test_mark_mode(modes),
            "Explain Mode": test_explain_mode(modes),
            "Example Mode": test_example_mode(modes),
            "Flashcards Mode": test_flashcards_mode(modes)
        }
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        for mode, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{mode}: {status}")
        
        all_passed = all(results.values())
        print("\n" + "="*80)
        if all_passed:
            print("ALL TESTS PASSED!")
        else:
            print("SOME TESTS FAILED")
        print("="*80)
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
