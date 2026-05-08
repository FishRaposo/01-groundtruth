from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str | int]:
    """Return service health status including database connectivity and document count."""
    try:
        result = await db.execute(select(func.count()).select_from(Document))
        document_count: int = result.scalar() or 0
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        document_count = 0

    return {
        "status": "healthy",
        "database": db_status,
        "document_count": document_count,
        "version": "0.1.0",
    }
