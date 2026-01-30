"""Repository classes for database operations."""

import json
import uuid
from datetime import datetime
from typing import Optional

import aiosqlite

from models.knowledge_base import KnowledgeBase, KnowledgeBaseCreate
from models.document import Document, DocumentCreate, DocumentChunk
from models.chat import ChatMessage, ChatMessageCreate
from models.quiz import Quiz, QuizCreate, QuizQuestion, QuizQuestionCreate


class KnowledgeBaseRepository:
    """Repository for knowledge base operations."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, kb: KnowledgeBaseCreate) -> KnowledgeBase:
        """Create a new knowledge base."""
        kb_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        await self.db.execute(
            """
            INSERT INTO knowledge_bases (id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (kb_id, kb.name, kb.description, now, now),
        )
        await self.db.commit()

        return KnowledgeBase(
            id=kb_id,
            name=kb.name,
            description=kb.description,
            created_at=now,
            updated_at=now,
        )

    async def get_all(self) -> list[KnowledgeBase]:
        """Get all knowledge bases."""
        cursor = await self.db.execute(
            "SELECT id, name, description, created_at, updated_at FROM knowledge_bases ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [
            KnowledgeBase(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    async def get_by_id(self, kb_id: str) -> Optional[KnowledgeBase]:
        """Get a knowledge base by ID."""
        cursor = await self.db.execute(
            "SELECT id, name, description, created_at, updated_at FROM knowledge_bases WHERE id = ?",
            (kb_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        return KnowledgeBase(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def update(self, kb_id: str, kb: KnowledgeBaseCreate) -> Optional[KnowledgeBase]:
        """Update a knowledge base."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            "UPDATE knowledge_bases SET name = ?, description = ?, updated_at = ? WHERE id = ?",
            (kb.name, kb.description, now, kb_id),
        )
        await self.db.commit()
        return await self.get_by_id(kb_id)

    async def delete(self, kb_id: str) -> bool:
        """Delete a knowledge base."""
        cursor = await self.db.execute(
            "DELETE FROM knowledge_bases WHERE id = ?", (kb_id,)
        )
        await self.db.commit()
        return cursor.rowcount > 0


class DocumentRepository:
    """Repository for document operations."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, doc: DocumentCreate) -> Document:
        """Create a new document."""
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        await self.db.execute(
            """
            INSERT INTO documents (id, knowledge_base_id, filename, file_type, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (doc_id, doc.knowledge_base_id, doc.filename, doc.file_type, doc.file_size, now),
        )
        await self.db.commit()

        return Document(
            id=doc_id,
            knowledge_base_id=doc.knowledge_base_id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            created_at=now,
        )

    async def get_by_knowledge_base(self, kb_id: str) -> list[Document]:
        """Get all documents for a knowledge base."""
        cursor = await self.db.execute(
            """
            SELECT id, knowledge_base_id, filename, file_type, file_size, created_at
            FROM documents WHERE knowledge_base_id = ? ORDER BY created_at DESC
            """,
            (kb_id,),
        )
        rows = await cursor.fetchall()
        return [
            Document(
                id=row["id"],
                knowledge_base_id=row["knowledge_base_id"],
                filename=row["filename"],
                file_type=row["file_type"],
                file_size=row["file_size"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        cursor = await self.db.execute(
            "SELECT id, knowledge_base_id, filename, file_type, file_size, created_at FROM documents WHERE id = ?",
            (doc_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        return Document(
            id=row["id"],
            knowledge_base_id=row["knowledge_base_id"],
            filename=row["filename"],
            file_type=row["file_type"],
            file_size=row["file_size"],
            created_at=row["created_at"],
        )

    async def delete(self, doc_id: str) -> bool:
        """Delete a document and its chunks."""
        cursor = await self.db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        await self.db.commit()
        return cursor.rowcount > 0

    async def create_chunk(
        self,
        document_id: str,
        content: str,
        chunk_index: int,
        metadata: Optional[dict] = None,
        embedding_id: Optional[str] = None,
    ) -> DocumentChunk:
        """Create a document chunk."""
        chunk_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        await self.db.execute(
            """
            INSERT INTO document_chunks (id, document_id, content, chunk_index, metadata, embedding_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (chunk_id, document_id, content, chunk_index, metadata_json, embedding_id, now),
        )
        await self.db.commit()

        return DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            metadata=metadata,
            embedding_id=embedding_id,
            created_at=now,
        )

    async def get_chunks_by_document(self, doc_id: str) -> list[DocumentChunk]:
        """Get all chunks for a document."""
        cursor = await self.db.execute(
            """
            SELECT id, document_id, content, chunk_index, metadata, embedding_id, created_at
            FROM document_chunks WHERE document_id = ? ORDER BY chunk_index
            """,
            (doc_id,),
        )
        rows = await cursor.fetchall()
        return [
            DocumentChunk(
                id=row["id"],
                document_id=row["document_id"],
                content=row["content"],
                chunk_index=row["chunk_index"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                embedding_id=row["embedding_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


class ChatRepository:
    """Repository for chat history operations."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, message: ChatMessageCreate) -> ChatMessage:
        """Create a new chat message."""
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        sources_json = json.dumps(message.sources) if message.sources else None

        await self.db.execute(
            """
            INSERT INTO chat_history (id, knowledge_base_id, role, content, sources, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (msg_id, message.knowledge_base_id, message.role, message.content, sources_json, now),
        )
        await self.db.commit()

        return ChatMessage(
            id=msg_id,
            knowledge_base_id=message.knowledge_base_id,
            role=message.role,
            content=message.content,
            sources=message.sources,
            created_at=now,
        )

    async def get_by_knowledge_base(
        self, kb_id: str, limit: int = 50
    ) -> list[ChatMessage]:
        """Get chat history for a knowledge base."""
        cursor = await self.db.execute(
            """
            SELECT id, knowledge_base_id, role, content, sources, created_at
            FROM chat_history WHERE knowledge_base_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (kb_id, limit),
        )
        rows = await cursor.fetchall()
        return [
            ChatMessage(
                id=row["id"],
                knowledge_base_id=row["knowledge_base_id"],
                role=row["role"],
                content=row["content"],
                sources=json.loads(row["sources"]) if row["sources"] else None,
                created_at=row["created_at"],
            )
            for row in reversed(rows)  # Return in chronological order
        ]

    async def clear_history(self, kb_id: str) -> int:
        """Clear chat history for a knowledge base."""
        cursor = await self.db.execute(
            "DELETE FROM chat_history WHERE knowledge_base_id = ?", (kb_id,)
        )
        await self.db.commit()
        return cursor.rowcount


class QuizRepository:
    """Repository for quiz operations."""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(self, quiz: QuizCreate) -> Quiz:
        """Create a new quiz."""
        quiz_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        await self.db.execute(
            """
            INSERT INTO quizzes (id, knowledge_base_id, title, description, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (quiz_id, quiz.knowledge_base_id, quiz.title, quiz.description, now),
        )
        await self.db.commit()

        return Quiz(
            id=quiz_id,
            knowledge_base_id=quiz.knowledge_base_id,
            title=quiz.title,
            description=quiz.description,
            questions=[],
            created_at=now,
        )

    async def get_by_id(self, quiz_id: str) -> Optional[Quiz]:
        """Get a quiz by ID with its questions."""
        cursor = await self.db.execute(
            "SELECT id, knowledge_base_id, title, description, created_at FROM quizzes WHERE id = ?",
            (quiz_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        questions = await self.get_questions(quiz_id)

        return Quiz(
            id=row["id"],
            knowledge_base_id=row["knowledge_base_id"],
            title=row["title"],
            description=row["description"],
            questions=questions,
            created_at=row["created_at"],
        )

    async def get_by_knowledge_base(self, kb_id: str) -> list[Quiz]:
        """Get all quizzes for a knowledge base."""
        cursor = await self.db.execute(
            """
            SELECT id, knowledge_base_id, title, description, created_at
            FROM quizzes WHERE knowledge_base_id = ? ORDER BY created_at DESC
            """,
            (kb_id,),
        )
        rows = await cursor.fetchall()

        quizzes = []
        for row in rows:
            questions = await self.get_questions(row["id"])
            quizzes.append(
                Quiz(
                    id=row["id"],
                    knowledge_base_id=row["knowledge_base_id"],
                    title=row["title"],
                    description=row["description"],
                    questions=questions,
                    created_at=row["created_at"],
                )
            )
        return quizzes

    async def delete(self, quiz_id: str) -> bool:
        """Delete a quiz."""
        cursor = await self.db.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        await self.db.commit()
        return cursor.rowcount > 0

    async def add_question(self, question: QuizQuestionCreate) -> QuizQuestion:
        """Add a question to a quiz."""
        question_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        options_json = json.dumps(question.options) if question.options else None

        await self.db.execute(
            """
            INSERT INTO quiz_questions (id, quiz_id, question, question_type, options, correct_answer, explanation, difficulty, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                question.quiz_id,
                question.question,
                question.question_type,
                options_json,
                question.correct_answer,
                question.explanation,
                question.difficulty,
                now,
            ),
        )
        await self.db.commit()

        return QuizQuestion(
            id=question_id,
            quiz_id=question.quiz_id,
            question=question.question,
            question_type=question.question_type,
            options=question.options,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            difficulty=question.difficulty,
            created_at=now,
        )

    async def get_questions(self, quiz_id: str) -> list[QuizQuestion]:
        """Get all questions for a quiz."""
        cursor = await self.db.execute(
            """
            SELECT id, quiz_id, question, question_type, options, correct_answer, explanation, difficulty, created_at
            FROM quiz_questions WHERE quiz_id = ? ORDER BY created_at
            """,
            (quiz_id,),
        )
        rows = await cursor.fetchall()
        return [
            QuizQuestion(
                id=row["id"],
                quiz_id=row["quiz_id"],
                question=row["question"],
                question_type=row["question_type"],
                options=json.loads(row["options"]) if row["options"] else None,
                correct_answer=row["correct_answer"],
                explanation=row["explanation"],
                difficulty=row["difficulty"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
