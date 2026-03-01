from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IGraphRepository(ABC):
    """Interface to interact with the graph and vector database."""

    @abstractmethod
    async def search_similar_code(
        self, query_vector: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches for code chunks by semantic similarity."""
        pass

    @abstractmethod
    async def analyze_blast_radius(self, node_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        """Analyzes the blast radius of a specific node."""
        pass

    @abstractmethod
    async def get_dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        """Gets outgoing dependencies of a node."""
        pass


class IMemoryRepository(ABC):
    """Interface to persist and search technical decisions."""

    @abstractmethod
    async def record_decision(
        self, topic: str, rationale: str, related_code_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records an architectural or code decision."""
        pass

    @abstractmethod
    async def search_memory(self, keyword: str) -> List[Dict[str, Any]]:
        """Searches past decision history."""
        pass
