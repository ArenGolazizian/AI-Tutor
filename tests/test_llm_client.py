"""Test LLM client with OpenRouter."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.llm_client import LLMClient


def test_basic_generation():
    """Test basic LLM generation."""
    print("\n" + "="*80)
    print("TEST: Basic LLM Generation")
    print("="*80)
    
    client = LLMClient(model="meta-llama/llama-3.3-8b-instruct:free")
    print(f"Initialized LLM client with model: {client.model}\n")
    
    result = client.generate(
        system_prompt="You are a helpful math tutor. Keep answers concise and clear.",
        user_message="What is 25 multiplied by 4?",
        temperature=0.3
    )
    
    print(f"Question: What is 25 multiplied by 4?")
    
    if "error" in result:
        print(f"ERROR: {result['error']}\n")
    else:
        print(f"Response: {result['response']}")
        print(f"Tokens used: {result['tokens_used']}")
        print(f"Finish reason: {result['finish_reason']}\n")
    
    return result


def test_with_context():
    """Test LLM generation with retrieved context."""
    print("="*80)
    print("TEST: Generation with Context (RAG)")
    print("="*80)
    
    client = LLMClient()
    
    context = """
    Newton's Second Law quantifies the relationship between force, mass, and acceleration. 
    It states that the acceleration of an object depends on the mass of the object and 
    the amount of force applied. The mathematical formula is F = ma, where F is force, 
    m is mass, and a is acceleration.
    """
    
    result = client.generate(
        system_prompt="You are an educational AI tutor. Use the provided context to answer questions accurately.",
        user_message="Explain Newton's second law in simple terms for a 10th grader.",
        context=context,
        temperature=0.7
    )
    
    print(f"\nQuestion: Explain Newton's second law in simple terms")
    print(f"Context provided: {len(context)} characters")
    
    if "error" in result:
        print(f"\nERROR: {result['error']}\n")
    else:
        print(f"\nResponse:\n{result['response']}")
        print(f"\nTokens used: {result['tokens_used']}")
        print(f"Finish reason: {result['finish_reason']}\n")
    
    return result


def test_error_handling():
    """Test error handling with invalid model."""
    print("="*80)
    print("TEST: Error Handling")
    print("="*80)
    
    client = LLMClient()
    client.set_model("invalid-model-name")
    
    result = client.generate(
        system_prompt="Test",
        user_message="Test"
    )
    
    if "error" in result:
        print(f"Error handled gracefully: {result['error'][:100]}...")
    else:
        print("Expected error but got response")
    
    return result


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# OpenRouter LLM Client Tests")
    print("#"*80)
    
    try:
        result1 = test_basic_generation()
        if result1.get('response'):
            print("Test 1 PASSED\n")
        else:
            print(f"Test 1 FAILED: {result1.get('error', 'No response')}\n")
        
        result2 = test_with_context()
        if result2.get('response'):
            print("Test 2 PASSED\n")
        else:
            print(f"Test 2 FAILED: {result2.get('error', 'No response')}\n")
        
        result3 = test_error_handling()
        if "error" in result3:
            print("Test 3 PASSED\n")
        else:
            print("Test 3 FAILED: Expected error\n")
        
        print("="*80)
        print("All tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()
