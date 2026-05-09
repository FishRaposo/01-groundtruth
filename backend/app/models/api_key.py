import secrets
import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ApiKey(Base):
    """SQLAlchemy model for API key authentication and rate limiting."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(8), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(min_length=1, max_length=256, description="Human-readable key name")
    is_admin: bool = Field(default=False, description="Whether the key has admin privileges")
    rate_limit: int = Field(default=60, ge=1, le=10000, description="Requests per minute")


class ApiKeyCreateResponse(BaseModel):
    """Schema returned once when a new API key is created."""

    id: uuid.UUID = Field(description="Unique key identifier")
    name: str = Field(description="Human-readable key name")
    key: str = Field(description="Raw API key - save this, it won't be shown again")
    is_admin: bool = Field(description="Whether the key has admin privileges")
    rate_limit: int = Field(description="Requests per minute")
    created_at: datetime = Field(description="Timestamp when key was created")

    model_config = {"from_attributes": True}


class ApiKeyResponse(BaseModel):
    """Schema for reading API key details (never includes raw key)."""

    id: uuid.UUID = Field(description="Unique key identifier")
    name: str = Field(description="Human-readable key name")
    key_prefix: str = Field(description="First 8 characters of the raw key for identification")
    is_active: bool = Field(description="Whether the key is currently active")
    is_admin: bool = Field(description="Whether the key has admin privileges")
    rate_limit: int = Field(description="Requests per minute")
    created_at: datetime = Field(description="Timestamp when key was created")
    last_used_at: datetime | None = Field(description="Timestamp when key was last used")

    model_config = {"from_attributes": True}


class ApiKeyUpdate(BaseModel):
    """Schema for updating an existing API key."""

    name: str | None = Field(default=None, min_length=1, max_length=256, description="New key name")
    rate_limit: int | None = Field(
        default=None, ge=1, le=10000, description="New requests per minute limit"
    )


class ApiKeyListResponse(BaseModel):
    """Schema for paginated API key listing."""

    keys: list[ApiKeyResponse] = Field(description="List of API keys")
    total: int = Field(description="Total number of API keys")


def generate_api_key() -> tuple[str, str, str]:
    """Generate a raw API key, its SHA-256 hash, and prefix.

    Returns:
        A tuple of (raw_key, key_hash, key_prefix).
    """
    raw_key = f"gt_{secrets.token_urlsafe(32)}"
    import hashlib

    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:8]
    return raw_key, key_hash, key_prefix
