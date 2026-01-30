"""Pydantic models for request/response validation."""

from .knowledge_base import KnowledgeBase, KnowledgeBaseCreate
from .document import Document, DocumentCreate, DocumentChunk
from .chat import ChatMessage, ChatMessageCreate, ChatRequest, ChatResponse
from .quiz import Quiz, QuizCreate, QuizQuestion, QuizQuestionCreate

__all__ = [
    "KnowledgeBase",
    "KnowledgeBaseCreate",
    "Document",
    "DocumentCreate",
    "DocumentChunk",
    "ChatMessage",
    "ChatMessageCreate",
    "ChatRequest",
    "ChatResponse",
    "Quiz",
    "QuizCreate",
    "QuizQuestion",
    "QuizQuestionCreate",
]
