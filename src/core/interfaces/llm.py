from typing import List
from abc import ABC, abstractmethod

class IEmbeddingProvider(ABC):
    """
    Contract for Embedding providers (Ollama, HuggingFace, OpenAI, etc.).
    """

    @abstractmethod
    async def get_query_embedding(self, text: str) -> List[float]:
        """Generates the semantic vector for a single text string."""
        pass

    @abstractmethod
    async def get_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates semantic vectors for a list of texts in batch."""
        pass
