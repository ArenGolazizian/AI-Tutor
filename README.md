# AI Tutor - Multi-Tenant Educational Assistant

RAG-based educational platform that retrieves answers from uploaded PDFs to provide accurate, curriculum-based tutoring. Features quota management, four interaction modes, and administrative controls.

## Demo

### Student Interface
![Student App Demo](docs/demo/user_app.gif)

### Admin Dashboard
![Admin Dashboard Demo](docs/demo/admin_app.gif)

## Overview

AI Tutor retrieves relevant content from uploaded educational PDFs and uses RAG (Retrieval-Augmented Generation) to provide accurate, source-based answers. The system offers four interaction modes: concept explanation, answer verification, practice problem generation, and flashcard creation. Built with FastAPI, it implements multi-tenant architecture with configurable usage quotas and comprehensive analytics.

## Architecture

**Backend (FastAPI)**
- RESTful API with 4 educational endpoints
- Multi-tenant quota middleware with three-tier system
- SQLite-based usage tracking and admin management

**Retrieval System (RAG)**
- Retrieves relevant content from uploaded educational PDFs
- Hybrid retrieval combining BM25 (keyword) and dense embeddings (semantic)
- PDF ingestion pipeline with semantic chunking
- FAISS vector store for similarity search
- Ensures answers are grounded in curriculum materials

**LLM Integration**
- OpenRouter API (Meta Llama 3.3 8B default)
- Combines retrieved PDF content with AI reasoning
- Automatic token usage tracking
- Grade-level adapted responses

**Frontend (Streamlit)**
- Student interface with 4 interaction modes
- Admin dashboard for tenant management and analytics

## Features

### Student Interface
- **Explain Mode**: Retrieves relevant content from PDFs and provides grade-level adapted explanations
- **Check Mode**: Verifies student answers against curriculum materials with detailed feedback
- **Practice Mode**: Generates practice problems based on uploaded educational content
- **Flashcard Mode**: Creates study materials from PDF content

### Administrative
- **Tenant Management**: Create and monitor user accounts
- **Quota System**: Three-tier structure (Free: 10K/100K daily/monthly, Pro: 100K/1M, Enterprise: Unlimited)
- **Usage Analytics**: Real-time tracking with endpoint-level breakdown

### Key Benefits
- **Accurate Answers**: All responses grounded in uploaded PDF curriculum
- **Source-Based Learning**: Students learn from actual course materials
- **No Hallucinations**: RAG ensures answers come from verified educational content

## Technical Stack

**Backend**: FastAPI, Python 3.13+, SQLite, Uvicorn  
**AI/ML**: LangChain, OpenRouter, Sentence-Transformers, FAISS, Rank-BM25  
**Frontend**: Streamlit, Pandas  
**NLP**: PyMuPDF, spaCy, NLTK

## Installation

### Prerequisites
- Python 3.13+
- OpenRouter API key (free tier available at openrouter.ai)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/AI-Tutor.git
cd AI-Tutor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Generate demo data
python scripts/generate_demo_data.py
python scripts/setup_demo_tenants.py
```

## Usage

### Start Backend Server
```bash
uvicorn src.api.main:app --reload
```
Server: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### Start Student Interface
```bash
streamlit run streamlit_user_app.py
```
Interface: `http://localhost:8501`

### Start Admin Dashboard
```bash
streamlit run streamlit_admin_app.py
```
Dashboard: `http://localhost:8502`

## API Endpoints

### Educational Modes
```
POST /api/v1/mark        - Answer verification with feedback
POST /api/v1/explain     - Concept explanation
POST /api/v1/example     - Practice problem generation
POST /api/v1/flashcards  - Flashcard creation
```

### Administrative
```
GET  /admin/tenants                      - List all tenants
POST /admin/tenants                      - Create new tenant
GET  /admin/tenants/{tenant_id}/usage    - Get usage statistics
GET  /admin/quota-check/{tenant_id}      - Check quota availability
```

### System
```
GET  /health  - Health check endpoint
```

## Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional
DEFAULT_MODEL=meta-llama/llama-3.3-70b-instruct
```

### Quota Tiers

Modify tier limits in `src/core/database.py`:
```python
TIER_LIMITS = {
    "free": {"daily": 10000, "monthly": 100000},
    "pro": {"daily": 100000, "monthly": 1000000},
    "enterprise": {"daily": -1, "monthly": -1}  # Unlimited
}
```

## Project Structure

```
AI-Tutor/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # App initialization
│   │   ├── routes.py           # Educational endpoints
│   │   ├── admin.py            # Admin endpoints
│   │   ├── middleware.py       # Quota enforcement
│   │   └── models.py           # Pydantic schemas
│   └── core/                   # Core functionality
│       ├── llm_client.py       # LLM integration
│       ├── modes.py            # Educational modes
│       ├── prompts.py          # Prompt templates
│       ├── ingestion.py        # PDF processing
│       ├── hybrid_retriever.py # RAG retrieval
│       └── database.py         # Quota management
├── scripts/                    # Setup scripts
├── tests/                      # Test suite
├── streamlit_user_app.py       # Student interface
├── streamlit_admin_app.py      # Admin dashboard
└── requirements.txt            # Dependencies
```

## Testing

```bash
pytest                       # Run all tests
pytest tests/test_api.py     # Test API endpoints
pytest tests/test_quotas.py  # Test quota system
```

## Development

### Adding New Modes
1. Add prompt in `src/core/prompts.py`
2. Implement logic in `src/core/modes.py`
3. Create endpoint in `src/api/routes.py`
4. Update Streamlit UI

### Modifying Quotas
- Enforcement: `src/api/middleware.py`
- Tier limits: `src/core/database.py`

## Performance Notes

- Hybrid retrieval balances speed (BM25) with accuracy (embeddings)
- SQLite suitable for <1000 concurrent users; migrate to PostgreSQL for scale
- FAISS index loads into memory; consider disk-based for large datasets

## Security

- API keys in environment variables only
- Multi-tenant isolation at middleware level
- Input validation via Pydantic
- No authentication implemented (add OAuth/JWT for production)

## License

MIT License

## Contact

For questions or feedback, open an issue on GitHub.
