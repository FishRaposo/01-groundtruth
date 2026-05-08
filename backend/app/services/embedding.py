import os
from typing import Any

from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Generates vector embeddings for text using either OpenAI or a local model.

    The provider is selected based on configuration. If OPENAI_API_KEY is set,
    the OpenAI embedding API is used. Otherwise, a local sentence-transformers
    model is loaded lazily.
    """

    def __init__(self) -> None:
        self._model: Any = None
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initialize and return the OpenAI client."""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def _get_model(self) -> Any:
        """Lazily load and return the local sentence-transformers model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text strings.

        Uses OpenAI if an API key is configured, otherwise falls back
        to a local sentence-transformers model.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.
        """
        if not texts:
            return []

        if settings.OPENAI_API_KEY:
            return await self._embed_openai(texts)

        return self._embed_local(texts)

    async def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query string.

        Args:
            query: The query text to embed.

        Returns:
            A single embedding vector.
        """
        results = await self.embed_texts([query])
        return results[0]

    async def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using the OpenAI API.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors from the OpenAI response.
        """
        client = self._get_client()
        response = client.embeddings.create(
            input=texts,
            model=settings.EMBEDDING_MODEL,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        return [item.embedding for item in response.data]

    def _embed_local(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using a local sentence-transformers model.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors from the local model.
        """
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


embedding_service = EmbeddingService()
