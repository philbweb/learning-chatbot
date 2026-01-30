"""Knowledge base CRUD endpoints."""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from config import settings
from db import get_db
from db.repositories import KnowledgeBaseRepository, DocumentRepository
from models.knowledge_base import KnowledgeBase, KnowledgeBaseCreate
from models.document import Document
from services.document_ingest import DocumentIngestService
from services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])

# Service instances (initialized in main.py lifespan)
rag_engine: Optional[RAGEngine] = None
ingest_service: Optional[DocumentIngestService] = None


def set_services(rag: RAGEngine, ingest: DocumentIngestService) -> None:
    """Set service instances from main app."""
    global rag_engine, ingest_service
    rag_engine = rag
    ingest_service = ingest


@router.get("", response_model=list[KnowledgeBase])
async def list_knowledge_bases():
    """List all knowledge bases."""
    async with get_db() as db:
        repo = KnowledgeBaseRepository(db)
        return await repo.get_all()


@router.post("", response_model=KnowledgeBase, status_code=201)
async def create_knowledge_base(kb: KnowledgeBaseCreate):
    """Create a new knowledge base."""
    async with get_db() as db:
        repo = KnowledgeBaseRepository(db)
        return await repo.create(kb)


@router.get("/{kb_id}", response_model=KnowledgeBase)
async def get_knowledge_base(kb_id: str):
    """Get a knowledge base by ID."""
    async with get_db() as db:
        repo = KnowledgeBaseRepository(db)
        kb = await repo.get_by_id(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        return kb


@router.put("/{kb_id}", response_model=KnowledgeBase)
async def update_knowledge_base(kb_id: str, kb: KnowledgeBaseCreate):
    """Update a knowledge base."""
    async with get_db() as db:
        repo = KnowledgeBaseRepository(db)
        existing = await repo.get_by_id(kb_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        return await repo.update(kb_id, kb)


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """Delete a knowledge base."""
    async with get_db() as db:
        repo = KnowledgeBaseRepository(db)
        if not await repo.delete(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Clean up files
    kb_path = settings.KNOWLEDGE_BASE_PATH / kb_id
    if kb_path.exists():
        shutil.rmtree(kb_path)

    return JSONResponse(content={"message": "Knowledge base deleted"})


@router.get("/{kb_id}/documents", response_model=list[Document])
async def list_documents(kb_id: str):
    """List all documents in a knowledge base."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        doc_repo = DocumentRepository(db)
        return await doc_repo.get_by_knowledge_base(kb_id)


@router.post("/{kb_id}/documents", response_model=Document, status_code=201)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    process: bool = Form(True),
):
    """Upload a document to a knowledge base."""
    async with get_db() as db:
        kb_repo = KnowledgeBaseRepository(db)
        if not await kb_repo.get_by_id(kb_id):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Validate file type
    filename = file.filename or "unknown"
    file_ext = Path(filename).suffix.lower().lstrip(".")
    supported_types = {"pdf", "md", "txt", "docx"}

    if file_ext not in supported_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(supported_types)}",
        )

    # Save file
    kb_path = settings.KNOWLEDGE_BASE_PATH / kb_id
    kb_path.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = kb_path / f"{file_id}_{filename}"

    try:
        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Create document record
    async with get_db() as db:
        doc_repo = DocumentRepository(db)
        from models.document import DocumentCreate

        doc = await doc_repo.create(
            DocumentCreate(
                knowledge_base_id=kb_id,
                filename=filename,
                file_type=file_ext,
                file_size=file_size,
            )
        )

        # Process document if requested
        if process and ingest_service and rag_engine:
            try:
                chunks = await ingest_service.process_file(file_path, file_ext, doc.id)

                # Store chunks in database
                for chunk in chunks:
                    await doc_repo.create_chunk(
                        document_id=doc.id,
                        content=chunk["content"],
                        chunk_index=chunk["chunk_index"],
                        metadata=chunk.get("metadata"),
                    )

                # Embed chunks
                await rag_engine.embed_chunks(kb_id, chunks)

                logger.info(f"Processed document {doc.id}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Document processing failed: {e}")
                # Document is saved but not processed

        return doc


@router.delete("/{kb_id}/documents/{doc_id}")
async def delete_document(kb_id: str, doc_id: str):
    """Delete a document from a knowledge base."""
    async with get_db() as db:
        doc_repo = DocumentRepository(db)
        doc = await doc_repo.get_by_id(doc_id)

        if not doc or doc.knowledge_base_id != kb_id:
            raise HTTPException(status_code=404, detail="Document not found")

        if not await doc_repo.delete(doc_id):
            raise HTTPException(status_code=500, detail="Failed to delete document")

    return JSONResponse(content={"message": "Document deleted"})
