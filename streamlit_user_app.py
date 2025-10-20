"""
AI Tutor - User Interface
A simple Streamlit app for students to interact with the AI tutor.
"""
import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Tutor",
    page_icon="🎓",
    layout="wide"
)

# Sidebar for user selection
st.sidebar.title("AI Tutor")
st.sidebar.markdown("---")

# Get all available tenants from API
available_tenants = []
tenant_names = {}  # Map tenant_id to display name
try:
    tenants_response = requests.get(f"{API_BASE_URL}/admin/tenants")
    if tenants_response.status_code == 200:
        tenants_json = tenants_response.json()
        # API returns {"tenants": [...], "count": N}
        tenants_data = tenants_json.get("tenants", [])
        available_tenants = [t["tenant_id"] for t in tenants_data]
        # Create display names
        for t in tenants_data:
            tenant_id = t["tenant_id"]
            name = t.get("name", tenant_id)
            tier = t.get("tier", "unknown")
            tenant_names[tenant_id] = f"{name} ({tier.upper()})"
except:
    # Fallback to default tenants if API call fails
    available_tenants = ["demo_user", "pro_user", "enterprise_user"]
    tenant_names = {
        "demo_user": "Demo User (FREE)",
        "pro_user": "Pro User (PRO)",
        "enterprise_user": "Enterprise User (ENTERPRISE)"
    }

# Tenant selection with display names
if available_tenants:
    # Show friendly names in dropdown
    display_names = [tenant_names.get(t, t) for t in available_tenants]
    selected_index = st.sidebar.selectbox(
        "Select Your Account:",
        range(len(available_tenants)),
        format_func=lambda i: display_names[i],
        help="Choose which account to use"
    )
    tenant_id = available_tenants[selected_index]
else:
    tenant_id = "demo_user"

# Display account info
tenant_info = {
    "demo_user": {"tier": "Free", "daily_limit": "10,000 tokens", "label": "[Free]"},
    "pro_user": {"tier": "Pro", "daily_limit": "100,000 tokens", "label": "[Pro]"},
    "enterprise_user": {"tier": "Enterprise", "daily_limit": "Unlimited", "label": "[Enterprise]"}
}

# Get tenant details from API
try:
    tenants_response = requests.get(f"{API_BASE_URL}/admin/tenants")
    if tenants_response.status_code == 200:
        tenants_json = tenants_response.json()
        tenants_data = tenants_json.get("tenants", [])
        for t in tenants_data:
            if t["tenant_id"] == tenant_id:
                daily_limit = t.get('daily_token_limit', 0)
                if daily_limit == -1:
                    limit_str = "Unlimited"
                else:
                    limit_str = f"{daily_limit:,} tokens"
                
                tenant_info[tenant_id] = {
                    "tier": t.get("tier", "unknown").title(),
                    "daily_limit": limit_str,
                    "label": f"[{t.get('tier', 'unknown').upper()}]"
                }
                break
except:
    pass

info = tenant_info.get(tenant_id, {"tier": "Unknown", "daily_limit": "Unknown", "label": "[Unknown]"})
st.sidebar.markdown(f"### {info['label']} {info['tier']} Account")
st.sidebar.markdown(f"**Daily Limit:** {info['daily_limit']}")

# Get current usage
try:
    usage_response = requests.get(f"{API_BASE_URL}/admin/tenants/{tenant_id}/usage")
    if usage_response.status_code == 200:
        usage_data = usage_response.json()
        # Parse the correct structure: usage.today and limits.daily
        daily_usage = usage_data.get("usage", {}).get("today", 0)
        daily_limit = usage_data.get("limits", {}).get("daily", 10000)
        
        # Progress bar
        if daily_limit == -1 or daily_limit == 0:  # Unlimited
            st.sidebar.markdown(f"**Today:** {daily_usage:,} tokens (Unlimited)")
        else:
            progress = min(daily_usage / daily_limit, 1.0) if daily_limit > 0 else 0
            st.sidebar.progress(progress)
            st.sidebar.markdown(f"**Today:** {daily_usage:,} / {daily_limit:,} tokens")
            
            if progress >= 0.9 and progress < 1.0:
                st.sidebar.warning("Warning: Nearing quota limit!")
            elif progress >= 1.0:
                st.sidebar.error("Quota exceeded!")
except Exception as e:
    st.sidebar.info("Start the API server first")

st.sidebar.markdown("---")
st.sidebar.markdown("**Server:** http://localhost:8000")

# Main content
st.title("AI Tutor Assistant")
st.markdown("Get help with your studies using AI-powered tutoring!")

# Tabs for different modes
tab1, tab2, tab3, tab4 = st.tabs(["Explain", "Mark Answer", "Examples", "Flashcards"])

# Tab 1: Explain Mode
with tab1:
    st.header("Explain a Concept")
    st.markdown("Ask the AI to explain any topic!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        explain_query = st.text_area(
            "What would you like to learn about?",
            placeholder="E.g., What is photosynthesis?",
            height=100,
            key="explain_query"
        )
    
    with col2:
        explain_grade = st.selectbox(
            "Grade Level:",
            ["elementary", "middle", "high", "college"],
            index=2,
            key="explain_grade"
        )
    
    if st.button("Explain", type="primary", key="explain_btn"):
        if not explain_query:
            st.warning("Please enter a question!")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/explain",
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": tenant_id
                        },
                        json={
                            "query": explain_query,
                            "grade_level": explain_grade
                        },
                        timeout=60  # 60 second timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Here's your explanation!")
                        st.markdown(f"### Answer:")
                        st.markdown(data["response"])
                        
                        # Show token usage
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Tokens Used", data.get("tokens_used", 0))
                        col2.metric("Daily Usage", f"{data.get('daily_usage', 0):,}")
                        col3.metric("Daily Limit", f"{data.get('daily_limit', 0):,}")
                        
                    elif response.status_code == 429:
                        st.error("Quota Exceeded!")
                        st.warning("You've reached your daily token limit. Try again tomorrow or upgrade your account.")
                    else:
                        st.error(f"Error: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out. The server took too long to respond.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server. Make sure it's running!")
                    st.code("uvicorn src.api.main:app --reload")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Tab 2: Mark Answer Mode
with tab2:
    st.header("Check My Answer")
    st.markdown("Submit your answer to get feedback!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        mark_question = st.text_input(
            "Question:",
            placeholder="E.g., What is photosynthesis?",
            key="mark_question"
        )
        
        mark_answer = st.text_area(
            "Your Answer:",
            placeholder="Type your answer here...",
            height=150,
            key="mark_answer"
        )
    
    with col2:
        mark_grade = st.selectbox(
            "Grade Level:",
            ["elementary", "middle", "high", "college"],
            index=2,
            key="mark_grade"
        )
    
    if st.button("Check Answer", type="primary", key="mark_btn"):
        if not mark_question or not mark_answer:
            st.warning("Please fill in both question and answer!")
        else:
            with st.spinner("Evaluating your answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/mark",
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": tenant_id
                        },
                        json={
                            "question": mark_question,
                            "student_answer": mark_answer,
                            "grade_level": mark_grade
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Feedback received!")
                        st.markdown(f"### Evaluation:")
                        st.markdown(data["response"])
                        
                        # Show token usage
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Tokens Used", data.get("tokens_used", 0))
                        col2.metric("Daily Usage", f"{data.get('daily_usage', 0):,}")
                        col3.metric("Daily Limit", f"{data.get('daily_limit', 0):,}")
                        
                    elif response.status_code == 429:
                        st.error("Quota Exceeded!")
                    else:
                        st.error(f"Error: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Tab 3: Examples Mode
with tab3:
    st.header("Practice Problems")
    st.markdown("Get practice problems to test your understanding!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        example_topic = st.text_input(
            "Topic:",
            placeholder="E.g., Quadratic equations",
            key="example_topic"
        )
    
    with col2:
        example_grade = st.selectbox(
            "Grade Level:",
            ["elementary", "middle", "high", "college"],
            index=2,
            key="example_grade"
        )
    
    if st.button("Generate Problems", type="primary", key="example_btn"):
        if not example_topic:
            st.warning("Please enter a topic!")
        else:
            with st.spinner("Creating practice problems..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/example",
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": tenant_id
                        },
                        json={
                            "topic": example_topic,
                            "grade_level": example_grade
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Practice problems ready!")
                        st.markdown(f"### Problems:")
                        st.markdown(data["response"])
                        
                        # Show token usage
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Tokens Used", data.get("tokens_used", 0))
                        col2.metric("Daily Usage", f"{data.get('daily_usage', 0):,}")
                        col3.metric("Daily Limit", f"{data.get('daily_limit', 0):,}")
                        
                    elif response.status_code == 429:
                        st.error("Quota Exceeded!")
                    else:
                        st.error(f"Error: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Tab 4: Flashcards Mode
with tab4:
    st.header("Study Flashcards")
    st.markdown("Generate flashcards for efficient studying!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        flashcard_topic = st.text_input(
            "Topic:",
            placeholder="E.g., Cell biology",
            key="flashcard_topic"
        )
    
    with col2:
        flashcard_grade = st.selectbox(
            "Grade Level:",
            ["elementary", "middle", "high", "college"],
            index=2,
            key="flashcard_grade"
        )
    
    if st.button("Create Flashcards", type="primary", key="flashcard_btn"):
        if not flashcard_topic:
            st.warning("Please enter a topic!")
        else:
            with st.spinner("Creating flashcards..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/flashcards",
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": tenant_id
                        },
                        json={
                            "topic": flashcard_topic,
                            "grade_level": flashcard_grade
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Flashcards created!")
                        st.markdown(f"### Flashcards:")
                        st.markdown(data["response"])
                        
                        # Show token usage
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Tokens Used", data.get("tokens_used", 0))
                        col2.metric("Daily Usage", f"{data.get('daily_usage', 0):,}")
                        col3.metric("Daily Limit", f"{data.get('daily_limit', 0):,}")
                        
                    elif response.status_code == 429:
                        st.error("Quota Exceeded!")
                    else:
                        st.error(f"Error: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Tip: Upgrade to Pro or Enterprise for higher token limits!")
