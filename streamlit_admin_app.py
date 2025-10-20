"""
AI Tutor - Admin Dashboard
A Streamlit app for managing users and monitoring system usage.
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Tutor Admin",
    page_icon="⚙",
    layout="wide"
)

# Title
st.title("AI Tutor Admin Dashboard")
st.markdown("Manage tenants and monitor system usage")

# Sidebar
st.sidebar.title("Admin Controls")
st.sidebar.markdown("---")

# Check API connection
try:
    health_response = requests.get(f"{API_BASE_URL}/health")
    if health_response.status_code == 200:
        st.sidebar.success("API Connected")
    else:
        st.sidebar.error("API Error")
except:
    st.sidebar.error("API Offline")
    st.error("Cannot connect to API server. Please start it first:")
    st.code("uvicorn src.api.main:app --reload")
    st.stop()

st.sidebar.markdown(f"**Server:** {API_BASE_URL}")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation:",
    ["Dashboard", "Manage Tenants", "Usage Analytics"]
)

# PAGE 1: Dashboard
if page == "Dashboard":
    st.header("System Overview")
    
    # Get all tenants
    try:
        tenants_response = requests.get(f"{API_BASE_URL}/admin/tenants")
        if tenants_response.status_code == 200:
            tenants_json = tenants_response.json()
            # API returns {"tenants": [...], "count": N}
            tenants = tenants_json.get("tenants", [])
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            
            active_tenants = sum(1 for t in tenants if t.get("is_active", True))
            col1.metric("Total Tenants", len(tenants))
            col2.metric("Active Tenants", active_tenants)
            col3.metric("Inactive Tenants", len(tenants) - active_tenants)
            
            st.markdown("---")
            
            # Tenants table
            st.subheader("All Tenants")
            
            # Get usage for each tenant
            tenant_data = []
            for tenant in tenants:
                tenant_id = tenant.get("tenant_id")
                tier = tenant.get("tier", "unknown")
                is_active = tenant.get("is_active", True)
                
                usage_response = requests.get(f"{API_BASE_URL}/admin/tenants/{tenant_id}/usage")
                
                if usage_response.status_code == 200:
                    usage_data = usage_response.json()
                    # Parse correct structure: usage.today and limits.daily
                    daily_usage = usage_data.get("usage", {}).get("today", 0)
                    daily_limit = usage_data.get("limits", {}).get("daily", 1)
                    
                    if daily_limit == -1:
                        usage_pct_str = "Unlimited"
                    else:
                        usage_pct = (daily_usage / max(daily_limit, 1) * 100) if daily_limit > 0 else 0
                        usage_pct_str = f"{usage_pct:.1f}%"
                    
                    tenant_data.append({
                        "Tenant ID": tenant_id,
                        "Name": tenant.get("name", tenant_id),
                        "Tier": tier,
                        "Daily Usage": f"{daily_usage:,}",
                        "Daily Limit": f"{daily_limit:,}" if daily_limit != -1 else "Unlimited",
                        "Usage %": usage_pct_str,
                        "Status": "Active" if is_active else "Inactive"
                    })
            
            if tenant_data:
                df = pd.DataFrame(tenant_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No tenants found")
                
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# PAGE 2: Manage Tenants
elif page == "Manage Tenants":
    st.header("Tenant Management")
    
    tab1, tab2 = st.tabs(["View Tenants", "Create Tenant"])
    
    # Tab 1: View Tenants
    with tab1:
        st.subheader("Current Tenants")
        
        try:
            tenants_response = requests.get(f"{API_BASE_URL}/admin/tenants")
            if tenants_response.status_code == 200:
                tenants_json = tenants_response.json()
                tenants = tenants_json.get("tenants", [])
                
                for tenant in tenants:
                    tenant_id = tenant.get("tenant_id")
                    tenant_name = tenant.get("name", tenant_id)
                    tier = tenant.get("tier", "unknown")
                    
                    with st.expander(f"{tenant_name} - {tier.upper()}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Tenant ID:** `{tenant_id}`")
                            st.markdown(f"**Name:** {tenant_name}")
                            st.markdown(f"**Tier:** {tier}")
                            st.markdown(f"**Status:** {'Active' if tenant.get('is_active', True) else 'Inactive'}")
                        
                        with col2:
                            daily_limit = tenant.get('daily_token_limit', 0)
                            monthly_limit = tenant.get('monthly_token_limit', 0)
                            st.markdown(f"**Daily Limit:** {daily_limit:,} tokens" if daily_limit != -1 else "**Daily Limit:** Unlimited")
                            st.markdown(f"**Monthly Limit:** {monthly_limit:,} tokens" if monthly_limit != -1 else "**Monthly Limit:** Unlimited")
                            st.markdown(f"**Created:** {tenant.get('created_at', 'Unknown')}")
                        
                        # Get usage
                        usage_response = requests.get(f"{API_BASE_URL}/admin/tenants/{tenant_id}/usage")
                        if usage_response.status_code == 200:
                            usage_data = usage_response.json()
                            
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            
                            # Parse correct structure
                            daily_usage = usage_data.get("usage", {}).get("today", 0)
                            daily_limit = usage_data.get("limits", {}).get("daily", 0)
                            monthly_usage = usage_data.get("usage", {}).get("this_month", 0)
                            monthly_limit = usage_data.get("limits", {}).get("monthly", 0)
                            
                            with col1:
                                st.markdown("**Current Usage:**")
                                st.markdown(f"- Daily: {daily_usage:,} / {daily_limit:,}" if daily_limit != -1 else f"- Daily: {daily_usage:,} (Unlimited)")
                                st.markdown(f"- Monthly: {monthly_usage:,} / {monthly_limit:,}" if monthly_limit != -1 else f"- Monthly: {monthly_usage:,} (Unlimited)")
                            
                            with col2:
                                if daily_limit != -1:
                                    daily_pct = (daily_usage / max(daily_limit, 1)) * 100
                                    st.progress(min(daily_pct / 100, 1.0))
                                    st.caption(f"Daily usage: {daily_pct:.1f}%")
                                else:
                                    st.caption("Unlimited usage")
        
        except Exception as e:
            st.error(f"Error loading tenants: {str(e)}")
    
    # Tab 2: Create Tenant
    with tab2:
        st.subheader("Create New Tenant")
        
        with st.form("create_tenant_form"):
            new_tenant_id = st.text_input("Tenant ID:", placeholder="e.g., user_123")
            new_name = st.text_input("Name:", placeholder="e.g., John Doe")
            
            new_tier = st.selectbox(
                "Tier:",
                ["free", "pro", "enterprise"]
            )
            
            new_notes = st.text_area("Notes (optional):", placeholder="Any additional information...")
            
            submitted = st.form_submit_button("Create Tenant", type="primary")
            
            if submitted:
                if not new_tenant_id:
                    st.error("Tenant ID is required!")
                elif not new_name:
                    st.error("Name is required!")
                else:
                    try:
                        payload = {
                            "tenant_id": new_tenant_id,
                            "name": new_name,
                            "tier": new_tier
                        }
                        
                        if new_notes:
                            payload["notes"] = new_notes
                        
                        response = requests.post(
                            f"{API_BASE_URL}/admin/tenants",
                            json=payload
                        )
                        
                        if response.status_code == 201 or response.status_code == 200:
                            created_tenant = response.json()
                            st.success(f"Tenant '{new_name}' (ID: {new_tenant_id}) created successfully!")
                            st.info(f"Tier: {new_tier.upper()} | Created: {created_tenant.get('created_at', 'now')}")
                            st.balloons()
                        elif response.status_code == 400:
                            error_data = response.json()
                            st.error(f"Error: {error_data.get('detail', 'Bad request')}")
                        else:
                            st.error(f"Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error creating tenant: {str(e)}")
    
    # Removed Tab 3: Edit Tenant

# PAGE 3: Usage Analytics
elif page == "Usage Analytics":
    st.header("Usage Analytics")
    
    # Tenant selector
    try:
        tenants_response = requests.get(f"{API_BASE_URL}/admin/tenants")
        if tenants_response.status_code == 200:
            tenants_json = tenants_response.json()
            tenants = tenants_json.get("tenants", [])
            tenant_ids = [t.get("tenant_id") for t in tenants]
            
            selected_tenant = st.selectbox("Select Tenant:", tenant_ids)
            
            # Get detailed usage
            usage_response = requests.get(f"{API_BASE_URL}/admin/tenants/{selected_tenant}/usage")
            
            if usage_response.status_code == 200:
                usage_data = usage_response.json()
                
                # Parse correct structure
                daily_usage = usage_data.get("usage", {}).get("today", 0)
                daily_limit = usage_data.get("limits", {}).get("daily", 0)
                monthly_usage = usage_data.get("usage", {}).get("this_month", 0)
                monthly_limit = usage_data.get("limits", {}).get("monthly", 0)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Daily Usage", f"{daily_usage:,}")
                col2.metric("Daily Limit", f"{daily_limit:,}" if daily_limit != -1 else "Unlimited")
                col3.metric("Monthly Usage", f"{monthly_usage:,}")
                col4.metric("Monthly Limit", f"{monthly_limit:,}" if monthly_limit != -1 else "Unlimited")
                
                # Progress bars
                st.markdown("---")
                st.subheader("Quota Usage")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Daily Quota:**")
                    if daily_limit != -1:
                        daily_pct = (daily_usage / max(daily_limit, 1)) * 100
                        st.progress(min(daily_pct / 100, 1.0))
                        st.caption(f"{daily_pct:.1f}% used")
                    else:
                        st.caption("Unlimited")
                
                with col2:
                    st.markdown("**Monthly Quota:**")
                    if monthly_limit != -1:
                        monthly_pct = (monthly_usage / max(monthly_limit, 1)) * 100
                        st.progress(min(monthly_pct / 100, 1.0))
                        st.caption(f"{monthly_pct:.1f}% used")
                    else:
                        st.caption("Unlimited")
                
                # Recent activity
                st.markdown("---")
                st.subheader("Recent Activity")
                
                # Check if by_endpoint data exists
                if "by_endpoint" in usage_data and usage_data["by_endpoint"]:
                    st.markdown("**Activity by Endpoint:**")
                    for endpoint_data in usage_data["by_endpoint"]:
                        st.markdown(f"- **{endpoint_data.get('endpoint', 'unknown')}**: {endpoint_data.get('request_count', 0)} requests, {endpoint_data.get('total_tokens', 0):,} tokens")
                else:
                    st.info("No activity recorded yet")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Admin Dashboard | AI Tutor System")
