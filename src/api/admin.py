"""Admin endpoints for tenant and quota management."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Literal
from src.core.database import QuotaDatabase

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

_quota_db: Optional[QuotaDatabase] = None


def set_quota_db(db: QuotaDatabase):
    """Initialize the global database instance."""
    global _quota_db
    _quota_db = db


def get_quota_db() -> QuotaDatabase:
    """Get the database instance."""
    if _quota_db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    return _quota_db


class CreateTenantRequest(BaseModel):
    """Request model for creating a new tenant."""
    tenant_id: str = Field(..., min_length=1, description="Unique tenant identifier")
    name: str = Field(..., min_length=1, description="Display name")
    tier: Literal["free", "pro", "enterprise"] = Field(default="free", description="Quota tier")
    notes: Optional[str] = Field(None, description="Optional notes about the tenant")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "user_123",
                "name": "John Doe",
                "tier": "pro",
                "notes": "Beta tester"
            }
        }


class TenantResponse(BaseModel):
    """Response model for tenant information."""
    tenant_id: str
    name: str
    tier: str
    daily_token_limit: int
    monthly_token_limit: int
    created_at: str
    is_active: bool


@admin_router.post(
    "/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Tenant",
    description="Create a new tenant (user/organization) with quota limits."
)
async def create_tenant(request: CreateTenantRequest):
    """Create a new tenant with tier-based token limits."""
    db = get_quota_db()
    
    success = db.add_tenant(
        tenant_id=request.tenant_id,
        name=request.name,
        tier=request.tier,
        notes=request.notes
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant '{request.tenant_id}' already exists"
        )
    
    tenant = db.get_tenant(request.tenant_id)
    return TenantResponse(**tenant)


@admin_router.get(
    "/tenants",
    summary="List Tenants",
    description="Get a list of all tenants."
)
async def list_tenants():
    """List all tenants in the system."""
    db = get_quota_db()
    tenants = db.list_tenants()
    return {"tenants": tenants, "count": len(tenants)}


@admin_router.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
    summary="Get Tenant",
    description="Get detailed information about a specific tenant."
)
async def get_tenant(tenant_id: str):
    """Get tenant details."""
    db = get_quota_db()
    tenant = db.get_tenant(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found"
        )
    
    return TenantResponse(**tenant)


@admin_router.get(
    "/tenants/{tenant_id}/usage",
    summary="Get Tenant Usage",
    description="Get detailed usage statistics for a tenant."
)
async def get_tenant_usage(tenant_id: str):
    """Get comprehensive usage statistics for a tenant."""
    db = get_quota_db()
    stats = db.get_usage_stats(tenant_id)
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"]
        )
    
    return stats


@admin_router.post(
    "/tenants/{tenant_id}/reset",
    summary="Reset Tenant Usage",
    description="Reset all usage for a tenant (useful for testing)."
)
async def reset_tenant_usage(tenant_id: str):
    """Reset all usage records for a tenant. Warning: Permanently deletes history!"""
    db = get_quota_db()
    
    tenant = db.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found"
        )
    
    db.reset_usage(tenant_id)
    
    return {
        "success": True,
        "message": f"Usage reset for tenant '{tenant_id}'",
        "tenant_id": tenant_id
    }


@admin_router.get(
    "/quota-check/{tenant_id}",
    summary="Check Quota",
    description="Check if a tenant has quota available (without processing a request)."
)
async def check_quota(tenant_id: str):
    """Check quota status for a tenant."""
    db = get_quota_db()
    can_proceed, usage_info = db.check_quota(tenant_id)
    
    return {
        "can_proceed": can_proceed,
        **usage_info
    }
