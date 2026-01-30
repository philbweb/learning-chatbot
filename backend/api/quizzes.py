"""Quiz endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from db import get_db
from db.repositories import KnowledgeBaseRepository, QuizRepository, DocumentRepository
from models.quiz import Quiz, QuizCreate, QuizQuestion, QuizQuestionCreate, QuizGenerateRequest
from services.quiz_generator import QuizGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])

# Service instance (initialized in main.py lifespan)
quiz_generator: Optional[QuizGenerator] = None


def set_services(generator: QuizGenerator) -> None:
    """Set service instance from main app."""
    global quiz_generator
    quiz_generator = generator


@router.get("/{kb_id}", response_model=list[Quiz])
async def list_quizzes(kb_id: str):
    """List all quizzes for a knowledge base."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        quiz_repo = QuizRepository(db)
        return await quiz_repo.get_by_knowledge_base(kb_id)


@router.post("/{kb_id}", response_model=Quiz, status_code=201)
async def create_quiz(kb_id: str, quiz: QuizCreate):
    """Create a new quiz."""
    if quiz.knowledge_base_id != kb_id:
        raise HTTPException(status_code=400, detail="Knowledge base ID mismatch")

    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        quiz_repo = QuizRepository(db)
        return await quiz_repo.create(quiz)


@router.get("/{kb_id}/{quiz_id}", response_model=Quiz)
async def get_quiz(kb_id: str, quiz_id: str):
    """Get a quiz by ID."""
    async with get_db() as db:
        quiz_repo = QuizRepository(db)
        quiz = await quiz_repo.get_by_id(quiz_id)

        if not quiz or quiz.knowledge_base_id != kb_id:
            raise HTTPException(status_code=404, detail="Quiz not found")

        return quiz


@router.delete("/{kb_id}/{quiz_id}")
async def delete_quiz(kb_id: str, quiz_id: str):
    """Delete a quiz."""
    async with get_db() as db:
        quiz_repo = QuizRepository(db)
        quiz = await quiz_repo.get_by_id(quiz_id)

        if not quiz or quiz.knowledge_base_id != kb_id:
            raise HTTPException(status_code=404, detail="Quiz not found")

        if not await quiz_repo.delete(quiz_id):
            raise HTTPException(status_code=500, detail="Failed to delete quiz")

    return JSONResponse(content={"message": "Quiz deleted"})


@router.post("/{kb_id}/{quiz_id}/questions", response_model=QuizQuestion, status_code=201)
async def add_question(kb_id: str, quiz_id: str, question: QuizQuestionCreate):
    """Add a question to a quiz."""
    if question.quiz_id != quiz_id:
        raise HTTPException(status_code=400, detail="Quiz ID mismatch")

    async with get_db() as db:
        quiz_repo = QuizRepository(db)
        quiz = await quiz_repo.get_by_id(quiz_id)

        if not quiz or quiz.knowledge_base_id != kb_id:
            raise HTTPException(status_code=404, detail="Quiz not found")

        return await quiz_repo.add_question(question)


@router.post("/{kb_id}/generate", response_model=Quiz, status_code=201)
async def generate_quiz(kb_id: str, request: QuizGenerateRequest):
    """Generate a quiz from knowledge base content."""
    if not quiz_generator:
        raise HTTPException(status_code=503, detail="Quiz generator not available")

    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get content from documents
        doc_repo = DocumentRepository(db)
        documents = await doc_repo.get_by_knowledge_base(kb_id)

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base has no documents. Upload documents first.",
            )

        # Gather content from chunks
        content_parts = []
        for doc in documents[:5]:  # Limit to first 5 documents
            chunks = await doc_repo.get_chunks_by_document(doc.id)
            for chunk in chunks[:10]:  # Limit chunks per document
                content_parts.append(chunk.content)

        if not content_parts:
            raise HTTPException(
                status_code=400,
                detail="No content found in documents. Process documents first.",
            )

        content = "\n\n".join(content_parts)

        # Generate questions
        questions = await quiz_generator.generate_questions(
            content=content,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            question_types=request.question_types,
        )

        # Create quiz
        quiz_repo = QuizRepository(db)
        quiz = await quiz_repo.create(
            QuizCreate(
                knowledge_base_id=kb_id,
                title=f"Quiz: {kb.name}",
                description=f"Auto-generated quiz with {len(questions)} questions",
            )
        )

        # Add questions to quiz
        for q in questions:
            await quiz_repo.add_question(
                QuizQuestionCreate(
                    quiz_id=quiz.id,
                    question=q["question"],
                    question_type=q["question_type"],
                    options=q.get("options"),
                    correct_answer=q["correct_answer"],
                    explanation=q.get("explanation"),
                    difficulty=q.get("difficulty", request.difficulty),
                )
            )

        # Return quiz with questions
        return await quiz_repo.get_by_id(quiz.id)
