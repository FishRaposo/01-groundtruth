from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.queries import router as queries_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize database tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title="GroundTruth",
    description="A production-minded RAG assistant template",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(queries_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic API information."""
    return {
        "name": "GroundTruth API",
        "version": "0.1.0",
        "docs": "/docs",
    }
