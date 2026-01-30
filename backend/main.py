"""FastAPI application with lifespan context manager."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db import init_db
from api import knowledge_bases_router, chat_router, quizzes_router
from api.knowledge_bases import set_services as set_kb_services
from api.chat import set_services as set_chat_services
from api.quizzes import set_services as set_quiz_services
from services.rag_engine import RAGEngine
from services.document_ingest import DocumentIngestService
from services.quiz_generator import QuizGenerator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for startup/shutdown."""
    logger.info("Starting Learning Chatbot API...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize services
    rag_engine = RAGEngine()
    await rag_engine.initialize()

    ingest_service = DocumentIngestService()

    quiz_generator = QuizGenerator()
    await quiz_generator.initialize()

    # Inject services into routers
    set_kb_services(rag_engine, ingest_service)
    set_chat_services(rag_engine)
    set_quiz_services(quiz_generator)

    logger.info(f"Services initialized (mock_mode={settings.is_mock_mode})")

    yield

    # Shutdown
    logger.info("Shutting down Learning Chatbot API...")


app = FastAPI(
    title="Learning Chatbot API",
    description="Backend API for the Learning Chatbot with RAG and quiz generation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for Tauri and dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",  # Tauri Vite dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "tauri://localhost",  # Tauri
        "https://tauri.localhost",  # Tauri (alternative)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_bases_router)
app.include_router(chat_router)
app.include_router(quizzes_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "mock_mode": settings.is_mock_mode,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
