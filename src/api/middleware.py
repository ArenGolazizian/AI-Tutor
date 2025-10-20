"""FastAPI middleware for quota enforcement."""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class QuotaMiddleware(BaseHTTPMiddleware):
    """Middleware that checks tenant quotas before processing requests."""
    
    def __init__(self, app):
        super().__init__(app)
        
        self.exempt_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/admin"
        ]
        self.exempt_exact_paths = ["/"]
    
    async def dispatch(self, request: Request, call_next):
        """Process each request through the quota system."""
        logger.info(f"Middleware processing: {request.method} {request.url.path}")
        
        if request.url.path in self.exempt_exact_paths:
            logger.info(f"Skipping quota check - exact match for path: {request.url.path}")
            return await call_next(request)
        
        for exempt_path in self.exempt_paths:
            if request.url.path.startswith(exempt_path):
                logger.info(f"Skipping quota check - path '{request.url.path}' starts with exempt '{exempt_path}'")
                return await call_next(request)
        
        logger.info(f"Path {request.url.path} is NOT exempt, checking quota...")
        
        try:
            quota_db = request.app.state.quota_db
            logger.info("Got quota_db from app.state")
        except Exception as e:
            logger.error(f"Failed to get quota_db: {e}")
            return await call_next(request)
        
        tenant_id = request.headers.get("X-Tenant-ID")
        
        if not tenant_id:
            tenant_id = "demo_user"
            logger.warning("No X-Tenant-ID header found, using 'demo_user'")
        
        can_proceed, usage_info = quota_db.check_quota(tenant_id)
        
        logger.info(f"Quota check for {tenant_id}: can_proceed={can_proceed}, daily={usage_info.get('daily_usage')}/{usage_info.get('daily_limit')}")
        
        if not can_proceed:
            logger.warning(f"Quota exceeded for {tenant_id}: {usage_info.get('reason')}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Token quota exceeded",
                    "detail": usage_info.get("reason"),
                    "usage": {
                        "daily_usage": usage_info["daily_usage"],
                        "daily_limit": usage_info["daily_limit"],
                        "monthly_usage": usage_info["monthly_usage"],
                        "monthly_limit": usage_info["monthly_limit"]
                    },
                    "suggestion": "Upgrade to a higher tier or wait for quota reset"
                }
            )
        
        request.state.tenant_id = tenant_id
        request.state.usage_info = usage_info
        
        response = await call_next(request)
        
        return response
