"""API route handlers for the 4 educational modes."""
from fastapi import APIRouter, HTTPException, status, Request
from src.api.models import (
    MarkRequest, ExplainRequest, ExampleRequest, FlashcardsRequest,
    ModeResponse, ErrorResponse, HealthResponse
)
from src.core.modes import EducationalModes
from src.core.database import QuotaDatabase
from typing import Optional

router = APIRouter()

_modes: Optional[EducationalModes] = None
_quota_db: Optional[QuotaDatabase] = None


def set_modes(modes: EducationalModes):
    """Initialize the global modes instance."""
    global _modes
    _modes = modes


def set_quota_db(db: QuotaDatabase):
    """Initialize the global database instance."""
    global _quota_db
    _quota_db = db


def get_modes() -> EducationalModes:
    """Get the initialized modes instance."""
    if _modes is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Educational modes not initialized. Please check server startup logs."
        )
    return _modes


def get_quota_db() -> QuotaDatabase:
    """Get the database instance."""
    if _quota_db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized. Please check server startup logs."
        )
    return _quota_db


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and all components are initialized.",
    tags=["System"]
)
async def health_check():
    """Health check endpoint."""
    try:
        modes = get_modes()
        return HealthResponse(
            status="healthy",
            components={
                "ingestion": "ready",
                "retriever": "ready",
                "llm": "ready",
                "chunks_loaded": len(modes.retriever.chunks)
            }
        )
    except HTTPException:
        return HealthResponse(
            status="unhealthy",
            components={
                "ingestion": "not initialized",
                "retriever": "not initialized",
                "llm": "not initialized",
                "chunks_loaded": 0
            }
        )


@router.post(
    "/mark",
    response_model=ModeResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Mark Student Answer",
    description="Evaluate a student's answer and provide detailed feedback with corrections.",
    tags=["Educational Modes"]
)
async def mark_answer(request: MarkRequest, http_request: Request):
    """Provide feedback on student answers."""
    try:
        modes = get_modes()
        db = get_quota_db()
        
        tenant_id = getattr(http_request.state, "tenant_id", "demo_user")
        
        result = modes.mark(
            student_answer=request.student_answer,
            question=request.question,
            grade_level=request.grade_level,
            top_k=request.top_k
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        db.record_usage(tenant_id, "/mark", result["tokens_used"])
        _, updated_usage = db.check_quota(tenant_id)
        
        return ModeResponse(
            response=result["response"],
            context_used=result["context_used"],
            tokens_used=result["tokens_used"],
            grade_level=request.grade_level,
            tenant_id=tenant_id,
            daily_usage=updated_usage["daily_usage"],
            daily_limit=updated_usage["daily_limit"],
            monthly_usage=updated_usage["monthly_usage"],
            monthly_limit=updated_usage["monthly_limit"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )


@router.post(
    "/explain",
    response_model=ModeResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Explain Concept",
    description="Provide a step-by-step explanation of a concept at the appropriate grade level.",
    tags=["Educational Modes"]
)
async def explain_concept(request: ExplainRequest, http_request: Request):
    """Provide step-by-step explanations of concepts."""
    try:
        modes = get_modes()
        db = get_quota_db()
        
        tenant_id = getattr(http_request.state, "tenant_id", "demo_user")
        
        result = modes.explain(
            query=request.query,
            grade_level=request.grade_level,
            top_k=request.top_k
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        db.record_usage(tenant_id, "/explain", result["tokens_used"])
        _, updated_usage = db.check_quota(tenant_id)
        
        return ModeResponse(
            response=result["response"],
            context_used=result["context_used"],
            tokens_used=result["tokens_used"],
            grade_level=request.grade_level,
            tenant_id=tenant_id,
            daily_usage=updated_usage["daily_usage"],
            daily_limit=updated_usage["daily_limit"],
            monthly_usage=updated_usage["monthly_usage"],
            monthly_limit=updated_usage["monthly_limit"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.post(
    "/example",
    response_model=ModeResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Generate Practice Problems",
    description="Create practice problems on a topic with 3 difficulty levels (Easy → Medium → Challenge).",
    tags=["Educational Modes"]
)
async def generate_examples(request: ExampleRequest, http_request: Request):
    """Generate practice problems with solutions."""
    try:
        modes = get_modes()
        db = get_quota_db()
        
        tenant_id = getattr(http_request.state, "tenant_id", "demo_user")
        
        result = modes.example(
            topic=request.topic,
            grade_level=request.grade_level,
            top_k=request.top_k
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        db.record_usage(tenant_id, "/example", result["tokens_used"])
        _, updated_usage = db.check_quota(tenant_id)
        
        return ModeResponse(
            response=result["response"],
            context_used=result["context_used"],
            tokens_used=result["tokens_used"],
            grade_level=request.grade_level,
            tenant_id=tenant_id,
            daily_usage=updated_usage["daily_usage"],
            daily_limit=updated_usage["daily_limit"],
            monthly_usage=updated_usage["monthly_usage"],
            monthly_limit=updated_usage["monthly_limit"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate examples: {str(e)}"
        )


@router.post(
    "/flashcards",
    response_model=ModeResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Generate Flashcards",
    description="Create study flashcards (5-8 Q&A pairs) for a topic.",
    tags=["Educational Modes"]
)
async def generate_flashcards(request: FlashcardsRequest, http_request: Request):
    """Create study flashcards for a topic."""
    try:
        modes = get_modes()
        db = get_quota_db()
        
        tenant_id = getattr(http_request.state, "tenant_id", "demo_user")
        
        result = modes.flashcards(
            topic=request.topic,
            grade_level=request.grade_level,
            top_k=request.top_k
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        db.record_usage(tenant_id, "/flashcards", result["tokens_used"])
        _, updated_usage = db.check_quota(tenant_id)
        
        return ModeResponse(
            response=result["response"],
            context_used=result["context_used"],
            tokens_used=result["tokens_used"],
            grade_level=request.grade_level,
            tenant_id=tenant_id,
            daily_usage=updated_usage["daily_usage"],
            daily_limit=updated_usage["daily_limit"],
            monthly_usage=updated_usage["monthly_usage"],
            monthly_limit=updated_usage["monthly_limit"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )
