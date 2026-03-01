"""
Central application configuration.
Uses Pydantic Settings for type validation and loading from the .env file.
"""

from typing import Literal
from unittest import case

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global configuration variables for NexusBrain.
    Can be overridden via environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment and Log
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # host and ports
    port: int = Field(default=8000, alias="APP_PORT")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")

    # SurrealDB Configuration
    surreal_url: str = Field(default="file://data/database", alias="SURREAL_URL")
    surreal_user: str = Field(default="root", alias="SURREAL_USER")
    surreal_pass: str = Field(default="root", alias="SURREAL_PASS")
    surreal_namespace: str = Field(default="nexusbrain", alias="SURREAL_NS")
    surreal_database: str = Field(default="graphrag", alias="SURREAL_DB")

    # Models and AI Configuration (Ollama / HuggingFace)
    embedding_service: Literal["ollama", "huggingface"] = Field(
        default="huggingface", alias="EMBEDDING_SERVICE"
    )
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    max_thread_pool_workers: int = Field(default=2, alias="MAX_THREAD_POOL_WORKERS")

    class Meta:
        env_file = ".env"


# Global instance (Singleton) to be imported throughout the app
settings = Settings()
