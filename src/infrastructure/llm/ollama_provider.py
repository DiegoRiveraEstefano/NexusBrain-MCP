from typing import List
from langchain_ollama import OllamaEmbeddings
from src.core.interfaces.llm import IEmbeddingProvider
from src.core.logging import get_logger

logger = get_logger(__name__)

class OllamaProvider(IEmbeddingProvider):
    def __init__(self, base_url: str, model_name: str):
        logger.info("OllamaProvider.__init__.start", base_url=base_url, model_name=model_name)
        self.embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url,
        )

    async def get_query_embedding(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)

    async def get_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)
