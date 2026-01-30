"""API route modules."""

from .knowledge_bases import router as knowledge_bases_router
from .chat import router as chat_router
from .quizzes import router as quizzes_router

__all__ = ["knowledge_bases_router", "chat_router", "quizzes_router"]
