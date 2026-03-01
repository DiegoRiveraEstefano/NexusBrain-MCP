from typing import List, Dict, Any, Optional
from src.core.interfaces.db import IMemoryRepository
from src.core.logging import get_logger

logger = get_logger(__name__)

class MemoryService:
    """Application service to record and search technical decisions."""

    def __init__(self, repo: IMemoryRepository):
        self.repo = repo

    async def record_decision(self, topic: str, rationale: str, related_code_id: Optional[str] = None) -> Dict[str, Any]:
        """Records a decision in the repository."""
        return await self.repo.record_decision(topic, rationale, related_code_id)

    async def search_memory(self, keyword: str) -> List[Dict[str, Any]]:
        """Searches past decisions in the repository."""
        return await self.repo.search_memory(keyword)
