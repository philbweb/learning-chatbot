"""Application configuration using Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Database settings
    DATABASE_PATH: Path = Path("data/learning_chatbot.db")
    KNOWLEDGE_BASE_PATH: Path = Path("data/knowledge_bases")

    # RAG settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "claude-3-haiku-20240307"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Mock mode for development without models
    # Auto-disabled when ANTHROPIC_API_KEY is set
    MOCK_MODE: bool = True

    # Anthropic API
    ANTHROPIC_API_KEY: str = ""

    @property
    def is_mock_mode(self) -> bool:
        """Return True if mock mode is enabled or API key is missing."""
        if not self.MOCK_MODE and self.ANTHROPIC_API_KEY:
            return False
        return self.MOCK_MODE or not self.ANTHROPIC_API_KEY

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)


settings = Settings()
