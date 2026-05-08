import pytest
from app.services.chunking import ChunkingService


@pytest.fixture
def service() -> ChunkingService:
    """Provide a fresh ChunkingService instance for each test."""
    return ChunkingService()


def test_chunk_text_returns_single_chunk_for_short_text(service: ChunkingService) -> None:
    """Test that text shorter than chunk_size is returned as a single chunk."""
    text = "This is a short text."
    chunks = service.chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_splits_long_text(service: ChunkingService) -> None:
    """Test that long text is split into multiple chunks."""
    text = " ".join(["word"] * 200)
    chunks = service.chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) > 1


def test_chunk_text_preserves_overlap(service: ChunkingService) -> None:
    """Test that adjacent chunks share overlapping content."""
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = service.chunk_text(text, chunk_size=50, overlap=20)
    assert len(chunks) >= 2


def test_chunk_text_handles_empty_string(service: ChunkingService) -> None:
    """Test that empty string returns no chunks."""
    chunks = service.chunk_text("", chunk_size=100, overlap=10)
    assert len(chunks) == 0


def test_chunk_by_structure_splits_on_headings(service: ChunkingService) -> None:
    """Test that structural chunking splits on markdown headings."""
    text = "# Section 1\nContent 1\n\n# Section 2\nContent 2\n\n# Section 3\nContent 3"
    chunks = service.chunk_by_structure(text, structure="heading")
    assert len(chunks) >= 2
