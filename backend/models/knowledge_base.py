"""Knowledge base schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the knowledge base")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")


class KnowledgeBase(BaseModel):
    """Schema for a knowledge base."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the knowledge base")
    description: Optional[str] = Field(None, description="Optional description")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
