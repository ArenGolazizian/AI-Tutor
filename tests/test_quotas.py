"""Test script to demonstrate the quota system."""
import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_1_check_quota():
    """Test 1: Check quota for demo_user."""
    print_section("TEST 1: Check Quota Status")
    
    response = requests.get(f"{BASE_URL}/admin/quota-check/demo_user")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuota check successful!")
        print(f"\nQuota Status:")
        print(f"   Tenant ID: {data['tenant_id']}")
        print(f"   Tier: {data['tier']}")
        print(f"   Can proceed: {data['can_proceed']}")
        print(f"\nDaily Usage:")
        print(f"   Used: {data['daily_usage']:,} tokens")
        print(f"   Limit: {data['daily_limit']:,} tokens")
        print(f"   Remaining: {data['daily_limit'] - data['daily_usage']:,} tokens")
        print(f"\nMonthly Usage:")
        print(f"   Used: {data['monthly_usage']:,} tokens")
        print(f"   Limit: {data['monthly_limit']:,} tokens")
        print(f"   Remaining: {data['monthly_limit'] - data['monthly_usage']:,} tokens")
    else:
        print(f"Failed: {response.text}")


def test_2_normal_request():
    """Test 2: Make a normal request (should succeed)."""
    print_section("TEST 2: Normal Request (Under Quota)")
    
    payload = {
        "query": "What is photosynthesis?",
        "grade_level": "middle",
        "top_k": 3
    }
    
    headers = {
        "X-Tenant-ID": "demo_user",
        "Content-Type": "application/json"
    }
    
    print("\nSending request to /explain endpoint...")
    print(f"   Tenant: demo_user")
    print(f"   Query: {payload['query']}")
    
    response = requests.post(f"{BASE_URL}/explain", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nRequest successful!")
        print(f"\nResponse Metadata:")
        print(f"   Tokens used: {data['tokens_used']}")
        print(f"   Context chunks: {data['context_used']}")
        print(f"   Daily usage: {data['daily_usage']:,} / {data['daily_limit']:,} tokens")
        print(f"   Monthly usage: {data['monthly_usage']:,} / {data['monthly_limit']:,} tokens")
        print(f"\nResponse preview (first 300 chars):")
        print(f"   {data['response'][:300]}...")
    else:
        print(f"Failed: {response.status_code}")
        print(f"   {response.text}")


def test_3_view_usage_stats():
    """Test 3: View detailed usage statistics."""
    print_section("TEST 3: View Usage Statistics")
    
    response = requests.get(f"{BASE_URL}/admin/tenants/demo_user/usage")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nUsage stats retrieved!")
        print(f"\nTenant: {data['name']} ({data['tenant_id']})")
        print(f"   Tier: {data['tier']}")
        print(f"\nUsage by Time Period:")
        print(f"   Today: {data['usage']['today']:,} tokens")
        print(f"   This week: {data['usage']['this_week']:,} tokens")
        print(f"   This month: {data['usage']['this_month']:,} tokens")
        print(f"   All time: {data['usage']['all_time']:,} tokens")
        
        if data['by_endpoint']:
            print(f"\nUsage by Endpoint:")
            for endpoint_data in data['by_endpoint']:
                print(f"   {endpoint_data['endpoint']}: {endpoint_data['total_tokens']:,} tokens ({endpoint_data['request_count']} requests)")
        else:
            print(f"\nNo usage history yet")
    else:
        print(f"Failed: {response.text}")


def test_4_list_all_tenants():
    """Test 4: List all tenants."""
    print_section("TEST 4: List All Tenants")
    
    response = requests.get(f"{BASE_URL}/admin/tenants")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFound {data['count']} tenants:")
        for tenant in data['tenants']:
            print(f"\n   {tenant['name']} ({tenant['tenant_id']})")
            print(f"      Tier: {tenant['tier']}")
            print(f"      Daily limit: {tenant['daily_token_limit']:,} tokens")
            print(f"      Monthly limit: {tenant['monthly_token_limit']:,} tokens")
            print(f"      Active: {tenant['is_active']}")
    else:
        print(f"Failed: {response.text}")


def test_5_create_new_tenant():
    """Test 5: Create a new tenant."""
    print_section("TEST 5: Create New Tenant")
    
    payload = {
        "tenant_id": "test_user_" + str(int(time.time())),
        "name": "Test User Created via API",
        "tier": "pro",
        "notes": "Created by test script"
    }
    
    print(f"\nCreating tenant: {payload['tenant_id']}")
    
    response = requests.post(f"{BASE_URL}/admin/tenants", json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print(f"\nTenant created successfully!")
        print(f"   ID: {data['tenant_id']}")
        print(f"   Name: {data['name']}")
        print(f"   Tier: {data['tier']}")
        print(f"   Daily limit: {data['daily_token_limit']:,} tokens")
        print(f"   Monthly limit: {data['monthly_token_limit']:,} tokens")
    elif response.status_code == 409:
        print(f"Tenant already exists (this is expected if you've run this test before)")
    else:
        print(f"Failed: {response.status_code}")
        print(f"   {response.text}")


def test_6_unlimited_tier():
    """Test 6: Test enterprise tier (unlimited)."""
    print_section("TEST 6: Enterprise Tier (Unlimited)")
    
    response = requests.get(f"{BASE_URL}/admin/quota-check/enterprise_user")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nEnterprise tier quota check:")
        print(f"   Tier: {data['tier']}")
        print(f"   Daily limit: {'Unlimited' if data['daily_limit'] == -1 else data['daily_limit']}")
        print(f"   Monthly limit: {'Unlimited' if data['monthly_limit'] == -1 else data['monthly_limit']}")
        print(f"   Can proceed: {data['can_proceed']} (should always be True)")
    else:
        print(f"Failed: {response.text}")


def main():
    """Run all quota tests."""
    print("\n" + "#"*80)
    print("# AI-Tutor Quota System Test Suite")
    print("#"*80)
    print("\nMake sure:")
    print("   1. The server is running: uvicorn src.api.main:app --reload")
    print("   2. Demo tenants are set up: python scripts/setup_demo_tenants.py")
    
    print("\nWaiting 2 seconds before starting tests...")
    time.sleep(2)
    
    try:
        test_1_check_quota()
        test_2_normal_request()
        test_3_view_usage_stats()
        test_4_list_all_tenants()
        test_5_create_new_tenant()
        test_6_unlimited_tier()
        
        print("\n" + "="*80)
        print("All quota tests completed!")
        print("="*80)
        print("\nNext steps:")
        print("   1. Try making requests with different tenant IDs")
        print("   2. Test quota exceeded by making many requests")
        print("   3. View usage in admin panel: http://localhost:8000/admin/tenants")
        print("   4. Reset usage for testing: POST /admin/tenants/{tenant_id}/reset")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n\n" + "="*80)
        print("ERROR: Could not connect to the API server!")
        print("="*80)
        print("\nPlease start the server first with:")
        print("   uvicorn src.api.main:app --reload")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
