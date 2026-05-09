"""API key model for service-to-service authentication."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ApiKey(Base):
    """SQLAlchemy model for API keys used for programmatic access."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    prefix: Mapped[str] = mapped_column(String(8), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rate_limit: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(min_length=1, max_length=256, description="Human-readable name for the API key")
    rate_limit: int = Field(default=60, description="Requests per minute allowed for this key")


class ApiKeyResponse(BaseModel):
    """Schema returned when reading an API key (never includes the raw key)."""

    id: uuid.UUID = Field(description="Unique API key identifier")
    name: str = Field(description="Human-readable name for the API key")
    prefix: str = Field(description="First 8 characters of the raw key for identification")
    is_active: bool = Field(description="Whether the API key is currently active")
    created_at: datetime = Field(description="Timestamp when the API key was created")
    last_used_at: datetime | None = Field(default=None, description="Timestamp of last usage")
    rate_limit: int = Field(description="Requests per minute allowed for this key")

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(ApiKeyResponse):
    """Schema returned once at creation time including the raw key value."""

    key: str = Field(description="The raw API key (shown only once)")
