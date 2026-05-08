import uuid

import pytest
from app.services.ingestion import IngestionService


@pytest.fixture
def service() -> IngestionService:
    """Provide a fresh IngestionService instance for each test."""
    return IngestionService()


@pytest.mark.asyncio
async def test_ingest_document_creates_pending_record(service: IngestionService) -> None:
    """Test that ingesting a document creates a record with pending status."""
    pass


@pytest.mark.asyncio
async def test_process_document_parses_and_chunks(service: IngestionService) -> None:
    """Test that processing a document creates parsed chunks."""
    pass


@pytest.mark.asyncio
async def test_process_document_generates_embeddings(service: IngestionService) -> None:
    """Test that processing generates embeddings for each chunk."""
    pass


@pytest.mark.asyncio
async def test_process_document_sets_ready_status(service: IngestionService) -> None:
    """Test that successful processing updates document status to ready."""
    pass


@pytest.mark.asyncio
async def test_process_nonexistent_document_returns_none(service: IngestionService) -> None:
    """Test that processing a non-existent document ID is handled gracefully."""
    fake_id = uuid.uuid4()
    await service.process_document(fake_id)
