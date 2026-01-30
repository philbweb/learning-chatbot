"""Async SQLite database setup with aiosqlite."""

import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config import settings


async def init_db() -> None:
    """Initialize the database with required tables."""
    settings.ensure_directories()

    async with aiosqlite.connect(settings.DATABASE_PATH) as db:
        await db.executescript(
            """
            -- Knowledge Bases table
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Documents table
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
            );

            -- Document chunks for RAG
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                metadata TEXT,
                embedding_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            -- Chat history
            CREATE TABLE IF NOT EXISTS chat_history (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
            );

            -- Quizzes
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
            );

            -- Quiz questions
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id TEXT PRIMARY KEY,
                quiz_id TEXT NOT NULL,
                question TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options TEXT,
                correct_answer TEXT NOT NULL,
                explanation TEXT,
                difficulty TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            );

            -- Create indexes for common queries
            CREATE INDEX IF NOT EXISTS idx_documents_kb ON documents(knowledge_base_id);
            CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(document_id);
            CREATE INDEX IF NOT EXISTS idx_chat_kb ON chat_history(knowledge_base_id);
            CREATE INDEX IF NOT EXISTS idx_quizzes_kb ON quizzes(knowledge_base_id);
            CREATE INDEX IF NOT EXISTS idx_questions_quiz ON quiz_questions(quiz_id);
            """
        )
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for database connections."""
    db = await aiosqlite.connect(settings.DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
