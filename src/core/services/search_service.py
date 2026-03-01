from typing import List, Dict, Any
from src.core.interfaces.db import IGraphRepository
from src.core.interfaces.llm import IEmbeddingProvider
from src.core.logging import get_logger

logger = get_logger(__name__)


class SearchService:
    """Application service to search and navigate the knowledge graph."""

    def __init__(self, repo: IGraphRepository, embedding_provider: IEmbeddingProvider):
        self.repo = repo
        self.embedding_provider = embedding_provider

    async def search_similar_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Converts query to vector and searches for similar code."""
        query_vector = await self.embedding_provider.get_query_embedding(query)
        return await self.repo.search_similar_code(query_vector, limit)

    async def analyze_blast_radius(self, node_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        """Gets components affected by a change in the node."""
        return await self.repo.analyze_blast_radius(node_id, depth)

    async def get_execution_flow(self, node_id: str) -> List[Dict[str, Any]]:
        """Gets outgoing dependencies of a node."""
        return await self.repo.get_dependencies(node_id)
