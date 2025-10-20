"""Test script for the FastAPI endpoints."""
import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_response(endpoint_name, response):
    """Pretty print the API response."""
    print("\n" + "="*80)
    print(f"Testing: {endpoint_name}")
    print("="*80)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSUCCESS!")
        print(f"\nResponse Preview (first 500 chars):")
        print("-" * 80)
        print(data["response"][:500] + "..." if len(data["response"]) > 500 else data["response"])
        print("-" * 80)
        print(f"\nMetadata:")
        print(f"   • Context chunks used: {data['context_used']}")
        print(f"   • Tokens used: {data['tokens_used']}")
        print(f"   • Grade level: {data['grade_level']}")
    else:
        print(f"\nFAILED!")
        print(f"Error: {response.text}")


def test_health():
    """Test the health check endpoint."""
    print("\n" + "="*80)
    print("Testing: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAPI is {data['status']}!")
        print(f"\nComponents:")
        for component, status in data['components'].items():
            print(f"   • {component}: {status}")
    else:
        print(f"\nHealth check failed!")
        print(f"Error: {response.text}")


def test_mark_endpoint():
    """Test the /mark endpoint."""
    payload = {
        "question": "What is Newton's Second Law?",
        "student_answer": "Newton's Second Law says that force equals mass times velocity.",
        "grade_level": "high",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/mark", json=payload)
    print_response("POST /mark", response)


def test_explain_endpoint():
    """Test the /explain endpoint."""
    payload = {
        "query": "How do quadratic equations work?",
        "grade_level": "middle",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/explain", json=payload)
    print_response("POST /explain", response)


def test_example_endpoint():
    """Test the /example endpoint."""
    payload = {
        "topic": "solving linear equations",
        "grade_level": "high",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/example", json=payload)
    print_response("POST /example", response)


def test_flashcards_endpoint():
    """Test the /flashcards endpoint."""
    payload = {
        "topic": "mitochondria and cell organelles",
        "grade_level": "high",
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/flashcards", json=payload)
    print_response("POST /flashcards", response)


def main():
    """Run all API tests."""
    print("\n" + "#"*80)
    print("# AI-Tutor API Test Suite")
    print("#"*80)
    print("\nMake sure the server is running first!")
    print("   Start it with: uvicorn src.api.main:app --reload")
    print("\nWaiting 2 seconds before starting tests...")
    time.sleep(2)
    
    try:
        test_health()
        
        print("\n\n" + "#"*80)
        print("# Testing Educational Mode Endpoints")
        print("#"*80)
        
        test_mark_endpoint()
        test_explain_endpoint()
        test_example_endpoint()
        test_flashcards_endpoint()
        
        print("\n\n" + "="*80)
        print("All API tests completed!")
        print("="*80)
        print("\nNext steps:")
        print("   1. Check the interactive docs at: http://localhost:8000/docs")
        print("   2. Try the endpoints yourself in the Swagger UI")
        print("   3. Build a frontend to use these endpoints!")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n\n" + "="*80)
        print("ERROR: Could not connect to the API server!")
        print("="*80)
        print("\nPlease start the server first with:")
        print("   uvicorn src.api.main:app --reload")
        print("\nOr:")
        print("   python src/api/main.py")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
