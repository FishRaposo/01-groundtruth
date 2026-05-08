import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.config import get_settings
from app.db.session import Base

settings = get_settings()


class Chunk(Base):
    """SQLAlchemy model for document chunks with vector embeddings."""

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding = mapped_column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ChunkResponse(BaseModel):
    """Schema for reading a chunk without score information."""

    id: uuid.UUID = Field(description="Unique chunk identifier")
    document_id: uuid.UUID = Field(description="Parent document identifier")
    content: str = Field(description="Text content of the chunk")
    chunk_index: int = Field(description="Position of this chunk within the document")
    metadata: dict[str, Any] | None = Field(description="Chunk-level metadata")
    created_at: datetime = Field(description="Timestamp when chunk was created")

    model_config = {"from_attributes": True}


class ChunkWithScore(BaseModel):
    """Schema for a chunk returned during retrieval with a relevance score."""

    id: uuid.UUID = Field(description="Unique chunk identifier")
    document_id: uuid.UUID = Field(description="Parent document identifier")
    content: str = Field(description="Text content of the chunk")
    chunk_index: int = Field(description="Position of this chunk within the document")
    metadata: dict[str, Any] | None = Field(description="Chunk-level metadata")
    relevance_score: float = Field(description="Relevance score from retrieval or reranking")

    model_config = {"from_attributes": True}
