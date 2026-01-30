"""Quiz schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class QuizQuestionCreate(BaseModel):
    """Schema for creating a quiz question."""

    quiz_id: str = Field(..., description="ID of the parent quiz")
    question: str = Field(..., description="The question text")
    question_type: str = Field(
        ..., description="Type of question (multiple_choice, true_false, short_answer)"
    )
    options: Optional[list[str]] = Field(None, description="Options for multiple choice questions")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of the answer")
    difficulty: str = Field("medium", description="Difficulty level (easy, medium, hard)")


class QuizQuestion(BaseModel):
    """Schema for a quiz question."""

    id: str = Field(..., description="Unique identifier")
    quiz_id: str = Field(..., description="ID of the parent quiz")
    question: str = Field(..., description="The question text")
    question_type: str = Field(..., description="Type of question")
    options: Optional[list[str]] = Field(None, description="Options for multiple choice")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of the answer")
    difficulty: str = Field(..., description="Difficulty level")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class QuizCreate(BaseModel):
    """Schema for creating a quiz."""

    knowledge_base_id: str = Field(..., description="ID of the knowledge base")
    title: str = Field(..., min_length=1, max_length=255, description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")


class Quiz(BaseModel):
    """Schema for a quiz."""

    id: str = Field(..., description="Unique identifier")
    knowledge_base_id: str = Field(..., description="ID of the knowledge base")
    title: str = Field(..., description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    questions: list[QuizQuestion] = Field(default_factory=list, description="Quiz questions")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class QuizGenerateRequest(BaseModel):
    """Schema for requesting quiz generation."""

    num_questions: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: str = Field("medium", description="Difficulty level")
    question_types: list[str] = Field(
        default_factory=lambda: ["multiple_choice"],
        description="Types of questions to generate",
    )
