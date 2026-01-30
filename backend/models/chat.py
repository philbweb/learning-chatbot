"""Chat message schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    knowledge_base_id: str = Field(..., description="ID of the knowledge base")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    sources: Optional[list[str]] = Field(None, description="Source document IDs used")


class ChatMessage(BaseModel):
    """Schema for a chat message."""

    id: str = Field(..., description="Unique identifier")
    knowledge_base_id: str = Field(..., description="ID of the knowledge base")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    sources: Optional[list[str]] = Field(None, description="Source document IDs used")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for a chat request."""

    message: str = Field(..., min_length=1, description="User's question or message")
    include_sources: bool = Field(True, description="Whether to include source references")


class ChatResponse(BaseModel):
    """Schema for a chat response."""

    message: str = Field(..., description="Assistant's response")
    sources: Optional[list[dict]] = Field(None, description="Source chunks used for the response")
