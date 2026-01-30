"""Chat endpoint with RAG and SSE streaming."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from db import get_db
from db.repositories import KnowledgeBaseRepository, ChatRepository
from models.chat import ChatRequest, ChatResponse, ChatMessage, ChatMessageCreate
from services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Service instance (initialized in main.py lifespan)
rag_engine: Optional[RAGEngine] = None


def set_services(rag: RAGEngine) -> None:
    """Set service instance from main app."""
    global rag_engine
    rag_engine = rag


@router.post("/{kb_id}", response_model=ChatResponse)
async def chat(kb_id: str, request: ChatRequest):
    """Send a message and get a response using RAG."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available")

    # Search for relevant context
    context = await rag_engine.search(kb_id, request.message)

    # Generate response
    response_text = await rag_engine.generate_response(request.message, context)

    # Save messages to history
    async with get_db() as db:
        chat_repo = ChatRepository(db)

        # Save user message
        await chat_repo.create(
            ChatMessageCreate(
                knowledge_base_id=kb_id,
                role="user",
                content=request.message,
            )
        )

        # Save assistant message with sources
        source_ids = [c["document_id"] for c in context] if request.include_sources else None
        await chat_repo.create(
            ChatMessageCreate(
                knowledge_base_id=kb_id,
                role="assistant",
                content=response_text,
                sources=source_ids,
            )
        )

    sources = None
    if request.include_sources:
        sources = [
            {"content": c["content"][:200], "document_id": c["document_id"], "score": c.get("score")}
            for c in context
        ]

    return ChatResponse(message=response_text, sources=sources)


@router.post("/{kb_id}/stream")
async def chat_stream(kb_id: str, request: ChatRequest):
    """Send a message and get a streaming response using SSE."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not available")

    # Search for relevant context
    context = await rag_engine.search(kb_id, request.message)

    async def generate():
        full_response = []

        # Send sources first if requested
        if request.include_sources:
            sources = [
                {"content": c["content"][:200], "document_id": c["document_id"]}
                for c in context
            ]
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

        # Stream response chunks
        async for chunk in rag_engine.generate_stream(request.message, context):
            full_response.append(chunk)
            yield f"data: {json.dumps({'type': 'chunk', 'data': chunk})}\n\n"

        # Save messages after streaming completes
        async with get_db() as db:
            chat_repo = ChatRepository(db)

            await chat_repo.create(
                ChatMessageCreate(
                    knowledge_base_id=kb_id,
                    role="user",
                    content=request.message,
                )
            )

            source_ids = [c["document_id"] for c in context] if request.include_sources else None
            await chat_repo.create(
                ChatMessageCreate(
                    knowledge_base_id=kb_id,
                    role="assistant",
                    content="".join(full_response),
                    sources=source_ids,
                )
            )

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/{kb_id}/history", response_model=list[ChatMessage])
async def get_chat_history(kb_id: str, limit: int = 50):
    """Get chat history for a knowledge base."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        chat_repo = ChatRepository(db)
        return await chat_repo.get_by_knowledge_base(kb_id, limit)


@router.delete("/{kb_id}/history")
async def clear_chat_history(kb_id: str):
    """Clear chat history for a knowledge base."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        chat_repo = ChatRepository(db)
        count = await chat_repo.clear_history(kb_id)

    return {"message": f"Cleared {count} messages"}
