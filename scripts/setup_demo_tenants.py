"""Setup script to create demo tenants in the quota database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import QuotaDatabase


def setup_demo_tenants():
    """Create 3 demo tenants: demo_user (free), pro_user (pro), enterprise_user (enterprise)."""
    print("\n" + "="*80)
    print("Setting up demo tenants...")
    print("="*80)
    
    db = QuotaDatabase(db_path="data/quotas.db")
    
    tenants = [
        {
            "tenant_id": "demo_user",
            "name": "Demo User (Free Tier)",
            "tier": "free",
            "notes": "Default test account with free tier limits"
        },
        {
            "tenant_id": "pro_user",
            "name": "Pro User",
            "tier": "pro",
            "notes": "Test account with pro tier limits"
        },
        {
            "tenant_id": "enterprise_user",
            "name": "Enterprise User",
            "tier": "enterprise",
            "notes": "Test account with unlimited access"
        }
    ]
    
    for tenant_data in tenants:
        print(f"\nCreating tenant: {tenant_data['tenant_id']}")
        print(f"  Name: {tenant_data['name']}")
        print(f"  Tier: {tenant_data['tier']}")
        
        success = db.add_tenant(**tenant_data)
        
        if success:
            tenant = db.get_tenant(tenant_data['tenant_id'])
            print(f"  ✅ Created successfully!")
            print(f"     Daily limit: {tenant['daily_token_limit']:,} tokens")
            print(f"     Monthly limit: {tenant['monthly_token_limit']:,} tokens")
        else:
            print(f"  ⚠️  Already exists (skipping)")
    
    print("\n" + "="*80)
    print("Summary of all tenants:")
    print("="*80)
    
    all_tenants = db.list_tenants()
    for tenant in all_tenants:
        print(f"\n{tenant['name']} ({tenant['tenant_id']})")
        print(f"  Tier: {tenant['tier']}")
        print(f"  Daily limit: {tenant['daily_token_limit']:,} tokens")
        print(f"  Monthly limit: {tenant['monthly_token_limit']:,} tokens")
        print(f"  Created: {tenant['created_at']}")
        print(f"  Active: {tenant['is_active']}")
    
    print("\n" + "="*80)
    print("✅ Demo tenants ready!")
    print("="*80)
    print("\nHow to use:")
    print("  1. Start the API server:")
    print("     uvicorn src.api.main:app --reload")
    print()
    print("  2. Make requests with X-Tenant-ID header:")
    print("     curl -H 'X-Tenant-ID: demo_user' http://localhost:8000/mark ...")
    print()
    print("  3. Or let it default to 'demo_user' if no header provided")
    print()
    print("  4. Check usage:")
    print("     http://localhost:8000/admin/tenants/demo_user/usage")
    print("="*80 + "\n")
    
    db.close()


if __name__ == "__main__":
    setup_demo_tenants()
