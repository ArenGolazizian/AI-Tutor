"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class MarkRequest(BaseModel):
    """Request model for the /mark endpoint."""
    question: str = Field(..., min_length=1, description="The question that was asked")
    student_answer: str = Field(..., min_length=1, description="The student's answer to evaluate")
    grade_level: Literal["elementary", "middle", "high", "college"] = Field(
        default="high",
        description="Student's current grade level for appropriate feedback"
    )
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Newton's Second Law?",
                "student_answer": "Newton's Second Law says that force equals mass times velocity.",
                "grade_level": "high",
                "top_k": 3
            }
        }

class ExplainRequest(BaseModel):
    """Request model for the /explain endpoint."""
    query: str = Field(..., min_length=1, description="The concept or question to explain")
    grade_level: Literal["elementary", "middle", "high", "college"] = Field(
        default="high",
        description="Student's current grade level for appropriate language"
    )
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do quadratic equations work?",
                "grade_level": "middle",
                "top_k": 3
            }
        }

class ExampleRequest(BaseModel):
    """Request model for the /example endpoint."""
    topic: str = Field(..., min_length=1, description="The topic to generate practice problems for")
    grade_level: Literal["elementary", "middle", "high", "college"] = Field(
        default="high",
        description="Student's current grade level for appropriate difficulty"
    )
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "solving linear equations",
                "grade_level": "high",
                "top_k": 3
            }
        }

class FlashcardsRequest(BaseModel):
    """Request model for the /flashcards endpoint."""
    topic: str = Field(..., min_length=1, description="The topic to create flashcards for")
    grade_level: Literal["elementary", "middle", "high", "college"] = Field(
        default="high",
        description="Student's current grade level for appropriate content"
    )
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Number of context chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "mitochondria and cell organelles",
                "grade_level": "high",
                "top_k": 5
            }
        }


class ModeResponse(BaseModel):
    """Standard response model for all educational mode endpoints."""
    response: str = Field(..., description="The LLM-generated response (feedback, explanation, problems, or flashcards)")
    context_used: int = Field(..., description="Number of context chunks retrieved and used")
    tokens_used: int = Field(..., description="Total tokens used by the LLM (prompt + completion)")
    grade_level: str = Field(..., description="The grade level used for this response")
    
    tenant_id: str = Field(..., description="The tenant (user) who made this request")
    daily_usage: int = Field(..., description="Total tokens used today by this tenant")
    daily_limit: int = Field(..., description="Daily token limit for this tenant (-1 = unlimited)")
    monthly_usage: int = Field(..., description="Total tokens used this month by this tenant")
    monthly_limit: int = Field(..., description="Monthly token limit for this tenant (-1 = unlimited)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "✓ Correct: The student correctly identified...\n✗ Needs Improvement: However, the formula should be F=ma, not F=mv...",
                "context_used": 3,
                "tokens_used": 881,
                "grade_level": "high",
                "tenant_id": "demo_user",
                "daily_usage": 5234,
                "daily_limit": 10000,
                "monthly_usage": 45678,
                "monthly_limit": 100000
            }
        }

class ErrorResponse(BaseModel):
    """Error response model for when something goes wrong."""
    error: str = Field(..., description="Error message describing what went wrong")
    detail: Optional[str] = Field(None, description="Additional details about the error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "LLM generation failed",
                "detail": "API rate limit exceeded. Please try again later."
            }
        }

class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = Field(..., description="Overall API status")
    components: dict = Field(..., description="Status of individual components (retriever, LLM, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "components": {
                    "ingestion": "ready",
                    "retriever": "ready",
                    "llm": "ready",
                    "chunks_loaded": 27
                }
            }
        }
