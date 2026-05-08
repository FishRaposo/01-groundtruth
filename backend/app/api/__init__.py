from app.api.documents import router as documents_router
from app.api.queries import router as queries_router
from app.api.health import router as health_router

__all__ = ["documents_router", "queries_router", "health_router"]
