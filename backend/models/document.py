"""Document schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Schema for creating a document."""

    knowledge_base_id: str = Field(..., description="ID of the parent knowledge base")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (pdf, md, txt, docx)")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class Document(BaseModel):
    """Schema for a document."""

    id: str = Field(..., description="Unique identifier")
    knowledge_base_id: str = Field(..., description="ID of the parent knowledge base")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    """Schema for a document chunk."""

    id: str = Field(..., description="Unique identifier")
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Index of this chunk within the document")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    embedding_id: Optional[str] = Field(None, description="ID in the vector store")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
