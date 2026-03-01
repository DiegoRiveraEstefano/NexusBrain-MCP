from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from src.core.interfaces.llm import IEmbeddingProvider
from src.core.logging import get_logger

logger = get_logger(__name__)

class HuggingFaceProvider(IEmbeddingProvider):
    def __init__(self, model_name: str):
        logger.info("HuggingFaceProvider.__init__.start", model_name=model_name)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    async def get_query_embedding(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)

    async def get_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)
