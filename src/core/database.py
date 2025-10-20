"""SQLite database manager for multi-tenant quota tracking."""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class QuotaDatabase:
    """Database manager for tracking token usage and enforcing quotas."""
    
    TIER_LIMITS = {
        "free": {
            "daily_token_limit": 10_000,
            "monthly_token_limit": 100_000,
        },
        "pro": {
            "daily_token_limit": 100_000,
            "monthly_token_limit": 1_000_000,
        },
        "enterprise": {
            "daily_token_limit": -1,
            "monthly_token_limit": -1,
        }
    }
    
    def __init__(self, db_path: str = "data/quotas.db"):
        """Initialize database connection."""
        self.db_path = db_path
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.create_tables()
        
        logger.info(f"Database initialized at {db_path}")
    
    def create_tables(self):
        """Create the database schema (tenants + usage tables)."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tier TEXT NOT NULL CHECK(tier IN ('free', 'pro', 'enterprise')),
                daily_token_limit INTEGER NOT NULL,
                monthly_token_limit INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                tokens_used INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_tenant_timestamp 
            ON usage(tenant_id, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_timestamp 
            ON usage(timestamp)
        """)
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def add_tenant(
        self, 
        tenant_id: str, 
        name: str, 
        tier: str = "free",
        notes: Optional[str] = None
    ) -> bool:
        """Add a new tenant (user/organization)."""
        if tier not in self.TIER_LIMITS:
            raise ValueError(f"Invalid tier: {tier}. Must be one of {list(self.TIER_LIMITS.keys())}")
        
        limits = self.TIER_LIMITS[tier]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO tenants (tenant_id, name, tier, daily_token_limit, monthly_token_limit, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tenant_id,
                name,
                tier,
                limits["daily_token_limit"],
                limits["monthly_token_limit"],
                notes
            ))
            self.conn.commit()
            logger.info(f"Created tenant: {tenant_id} ({name}) - {tier} tier")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Tenant {tenant_id} already exists")
            return False
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        """Get tenant information."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tenants WHERE tenant_id = ?", (tenant_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def check_quota(self, tenant_id: str) -> Tuple[bool, Dict]:
        """Check if tenant has quota available before processing a request."""
        tenant = self.get_tenant(tenant_id)
        
        if not tenant:
            return False, {"error": f"Tenant {tenant_id} not found"}
        
        if not tenant["is_active"]:
            return False, {"error": f"Tenant {tenant_id} is inactive"}
        
        daily_usage = self._get_usage_in_period(tenant_id, days=1)
        monthly_usage = self._get_usage_in_period(tenant_id, days=30)
        
        daily_limit = tenant["daily_token_limit"]
        monthly_limit = tenant["monthly_token_limit"]
        
        can_proceed = True
        reason = None
        
        if daily_limit != -1 and daily_usage >= daily_limit:
            can_proceed = False
            reason = f"Daily quota exceeded: {daily_usage:,} / {daily_limit:,} tokens"
        elif monthly_limit != -1 and monthly_usage >= monthly_limit:
            can_proceed = False
            reason = f"Monthly quota exceeded: {monthly_usage:,} / {monthly_limit:,} tokens"
        
        usage_info = {
            "tenant_id": tenant_id,
            "tier": tenant["tier"],
            "daily_usage": daily_usage,
            "daily_limit": daily_limit,
            "monthly_usage": monthly_usage,
            "monthly_limit": monthly_limit,
            "can_proceed": can_proceed,
            "reason": reason
        }
        
        return can_proceed, usage_info
    
    def record_usage(self, tenant_id: str, endpoint: str, tokens_used: int):
        """Record token usage for a tenant."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO usage (tenant_id, endpoint, tokens_used)
            VALUES (?, ?, ?)
        """, (tenant_id, endpoint, tokens_used))
        self.conn.commit()
        
        logger.info(f"Recorded usage: {tenant_id} used {tokens_used} tokens on {endpoint}")
    
    def get_usage_stats(self, tenant_id: str) -> Dict:
        """Get detailed usage statistics for a tenant."""
        tenant = self.get_tenant(tenant_id)
        
        if not tenant:
            return {"error": f"Tenant {tenant_id} not found"}
        
        today = self._get_usage_in_period(tenant_id, days=1)
        this_week = self._get_usage_in_period(tenant_id, days=7)
        this_month = self._get_usage_in_period(tenant_id, days=30)
        all_time = self._get_usage_in_period(tenant_id, days=None)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT endpoint, 
                   COUNT(*) as request_count,
                   SUM(tokens_used) as total_tokens
            FROM usage
            WHERE tenant_id = ?
            GROUP BY endpoint
            ORDER BY total_tokens DESC
        """, (tenant_id,))
        
        by_endpoint = [dict(row) for row in cursor.fetchall()]
        
        return {
            "tenant_id": tenant_id,
            "name": tenant["name"],
            "tier": tenant["tier"],
            "limits": {
                "daily": tenant["daily_token_limit"],
                "monthly": tenant["monthly_token_limit"]
            },
            "usage": {
                "today": today,
                "this_week": this_week,
                "this_month": this_month,
                "all_time": all_time
            },
            "by_endpoint": by_endpoint
        }
    
    def _get_usage_in_period(self, tenant_id: str, days: Optional[int]) -> int:
        """Get total token usage for a tenant in a time period."""
        cursor = self.conn.cursor()
        
        if days is None:
            cursor.execute("""
                SELECT COALESCE(SUM(tokens_used), 0) as total
                FROM usage
                WHERE tenant_id = ?
            """, (tenant_id,))
        else:
            cutoff = datetime.now() - timedelta(days=days)
            cursor.execute("""
                SELECT COALESCE(SUM(tokens_used), 0) as total
                FROM usage
                WHERE tenant_id = ? AND timestamp >= ?
            """, (tenant_id, cutoff))
        
        result = cursor.fetchone()
        return result["total"]
    
    def reset_usage(self, tenant_id: str):
        """Reset all usage for a tenant (useful for testing)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usage WHERE tenant_id = ?", (tenant_id,))
        self.conn.commit()
        logger.info(f"Reset usage for tenant: {tenant_id}")
    
    def list_tenants(self) -> list:
        """List all tenants."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tenants ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Database connection closed")
