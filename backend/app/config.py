from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://groundtruth:groundtruth_dev@localhost:5432/groundtruth"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "groundtruth"
    DATABASE_USER: str = "groundtruth"
    DATABASE_PASSWORD: str = "groundtruth_dev"

    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    REFUSAL_CONFIDENCE_THRESHOLD: float = 0.5

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
