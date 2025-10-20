"""FastAPI application setup and initialization."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.api.routes import router, set_modes, set_quota_db
from src.api.admin import admin_router, set_quota_db as set_admin_quota_db
from src.api.middleware import QuotaMiddleware
from src.core.ingestion import IngestionPipeline
from src.core.hybrid_retriever import HybridRetriever
from src.core.llm_client import LLMClient
from src.core.modes import EducationalModes
from src.core.database import QuotaDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup, cleanup on shutdown."""
    logger.info("Starting AI-Tutor API server...")
    
    try:
        logger.info("Initializing quota database...")
        db = QuotaDatabase(db_path="data/quotas.db")
        app.state.quota_db = db
        set_quota_db(db)
        set_admin_quota_db(db)
        logger.info("Database ready")
        
        logger.info("Ingesting documents...")
        pipeline = IngestionPipeline(chunk_size=512)
        chunks = pipeline.ingest_documents('data/demo', 'data/demo/metadata.csv')
        logger.info(f"Loaded {len(chunks)} chunks")
        
        logger.info("Initializing hybrid retriever...")
        retriever = HybridRetriever(chunks, model_name='all-MiniLM-L6-v2')
        logger.info("Retriever ready")
        
        logger.info("Initializing LLM client...")
        llm = LLMClient()
        logger.info(f"LLM ready (model: {llm.model})")
        
        logger.info("Initializing educational modes...")
        modes = EducationalModes(retriever, llm, default_grade_level="high")
        set_modes(modes)
        logger.info("All 4 modes ready")
        
        logger.info("=" * 80)
        logger.info("AI-Tutor API is ready!")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("=" * 80)
        
        yield
        
        logger.info("Shutting down AI-Tutor API...")
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise


app = FastAPI(
    title="AI-Tutor API",
    description="""
    Production-ready RAG-based educational AI system with 4 interaction modes.
    
    ## Features
    - Mark Mode: Get feedback on student answers
    - Explain Mode: Simplify complex concepts
    - Example Mode: Generate practice problems
    - Flashcards Mode: Create study materials
    
    ## Technology Stack
    - Retrieval: Hybrid search (BM25 + semantic embeddings) with RRF fusion
    - LLM: OpenRouter API with Llama 3.3-8b-instruct
    - Embeddings: all-MiniLM-L6-v2
    - Backend: FastAPI with Pydantic validation
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(QuotaMiddleware)

app.include_router(admin_router)
app.include_router(router, prefix="/api/v1")
app.include_router(router)


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI-Tutor API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "interactive": "/docs",
            "alternative": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "mark": "/mark",
            "explain": "/explain",
            "example": "/example",
            "flashcards": "/flashcards"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
