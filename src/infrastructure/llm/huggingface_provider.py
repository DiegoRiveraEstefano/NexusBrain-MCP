from concurrent.futures.thread import ThreadPoolExecutor
from typing import List
import asyncio
from typing import TYPE_CHECKING
from src.core.interfaces.llm import IEmbeddingProvider
from src.core.logging import get_logger
from src.core.settings import settings

if TYPE_CHECKING:
    from langchain_huggingface import HuggingFaceEmbeddings


logger = get_logger(__name__)


class HuggingFaceProvider(IEmbeddingProvider):
    def __init__(self, model_name: str):
        logger.info("HuggingFaceProvider.__init__.start", model_name=model_name)
        self._model_name = model_name
        self._embeddings = None
        self._lock = asyncio.Lock()
        self._thread_executor = ThreadPoolExecutor(max_workers=settings.max_thread_pool_workers)

    def _load_model(self) -> "HuggingFaceEmbeddings":
        """Carga el modelo de forma síncrona. Se ejecutará en el ThreadPool."""
        logger.info("HuggingFaceProvider._load_model.start", model_name=self._model_name)
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=self._model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    async def _get_or_load_embeddings(self) -> "HuggingFaceEmbeddings":
        """Retorna el modelo cargado, instanciándolo perezosamente en un hilo si es necesario."""
        if self._embeddings is None:
            async with self._lock:
                # Patrón Double-Checked Locking
                if self._embeddings is None:
                    loop = asyncio.get_running_loop()
                    logger.info("HuggingFaceProvider._get_or_load_embeddings.loading")
                    # Delegamos la inicialización bloqueante a nuestro ThreadPool
                    self._embeddings = await loop.run_in_executor(
                        self._thread_executor, self._load_model
                    )
                    logger.info("HuggingFaceProvider._get_or_load_embeddings.loaded")
        return self._embeddings

    async def get_query_embedding(self, text: str) -> List[float]:
        embeddings = await self._get_or_load_embeddings()
        loop = asyncio.get_running_loop()
        # Usamos embed_query síncrono delegado a nuestro ThreadPool
        return await loop.run_in_executor(self._thread_executor, embeddings.embed_query, text)

    async def get_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = await self._get_or_load_embeddings()
        loop = asyncio.get_running_loop()
        # Usamos embed_documents síncrono delegado a nuestro ThreadPool
        return await loop.run_in_executor(self._thread_executor, embeddings.embed_documents, texts)
