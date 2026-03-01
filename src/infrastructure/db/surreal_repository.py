from typing import List, Dict, Any, Optional

from src.core.interfaces.db import IGraphRepository, IMemoryRepository
from src.db.repositories.base import BaseRepository
from src.db.repositories.queries import (
    ANALYZE_BLAST_RADIUS_QUERY_TEMPLATE,
    GET_DEPENDENCIES_QUERY_TEMPLATE,
    SEARCH_SIMILAR_CODE_QUERY,
    RECORD_DECISION_QUERY,
    RELATE_DECISION_TO_CODE_TEMPLATE,
    SEARCH_MEMORY_QUERY,
)
from src.core.logging import get_logger

logger = get_logger(__name__)

class SurrealGraphRepository(BaseRepository, IGraphRepository):
    """Implementation of IGraphRepository for SurrealDB."""

    async def search_similar_code(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        logger.debug("SurrealGraphRepository.search_similar_code.execute", limit=limit)
        return await self.raw_query(
            SEARCH_SIMILAR_CODE_QUERY, {"query_vector": query_vector, "limit": limit}
        )

    async def analyze_blast_radius(self, node_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        query = ANALYZE_BLAST_RADIUS_QUERY_TEMPLATE.format(node_id=node_id)
        logger.debug("SurrealGraphRepository.analyze_blast_radius.execute", node_id=node_id, depth=depth)
        return await self.raw_query(query)

    async def get_dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        query = GET_DEPENDENCIES_QUERY_TEMPLATE.format(node_id=node_id)
        return await self.raw_query(query)


class SurrealMemoryRepository(BaseRepository, IMemoryRepository):
    """Implementation of IMemoryRepository for SurrealDB."""

    async def record_decision(self, topic: str, rationale: str, related_code_id: Optional[str] = None) -> Dict[str, Any]:
        result = await self.raw_query(
            RECORD_DECISION_QUERY, {"topic": topic, "rationale": rationale}
        )

        created_record = result[0] if result else {}

        if related_code_id and created_record:
            log_id = created_record.get("id")
            query_rel = RELATE_DECISION_TO_CODE_TEMPLATE.format(
                log_id=log_id, related_code_id=related_code_id
            )
            await self.raw_query(query_rel)
            logger.info("SurrealMemoryRepository.record_decision.linked_code", related_code_id=related_code_id)

        logger.info("SurrealMemoryRepository.record_decision.success", topic=topic)
        return created_record

    async def search_memory(self, keyword: str) -> List[Dict[str, Any]]:
        return await self.raw_query(SEARCH_MEMORY_QUERY, {"keyword": keyword})
