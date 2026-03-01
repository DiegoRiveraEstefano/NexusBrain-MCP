from src.core.interfaces.llm import IEmbeddingProvider

from src.infrastructure.llm.huggingface_provider import HuggingFaceProvider

print("a.3")
from src.infrastructure.llm.ollama_provider import OllamaProvider

from src.core.settings import settings


class EmbeddingFactory:
    """Factory to instantiate the correct embedding provider based on configuration."""

    @staticmethod
    def create() -> IEmbeddingProvider:
        if settings.embedding_service == "huggingface":
            return HuggingFaceProvider(model_name=settings.embedding_model)
        elif settings.embedding_service == "ollama":
            return OllamaProvider(
                base_url=settings.ollama_base_url, model_name=settings.embedding_model
            )
        else:
            raise NotImplementedError(
                f"Embedding service '{settings.embedding_service}' not supported."
            )
