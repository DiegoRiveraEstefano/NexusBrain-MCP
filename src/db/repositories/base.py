"""
Base class for all SurrealDB repositories.
"""

from typing import Any
from surrealdb import Surreal
from src.db.client import db_client


class BaseRepository:
    """
    Base class that provides access to the database connection
    for domain-specific repositories.
    """

    @property
    async def db(self) -> Surreal:
        """Gets the active connection to SurrealDB."""
        return await db_client.connect()

    async def raw_query(
        self, query: str, vars: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Executes a raw SurrealQL query and extracts the results from the standard SurrealDB format.
        """
        db = await self.db
        result = await db.query(query, vars or {})

        # SurrealDB returns a list of results (one for each statement in the query)
        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get("result", [])
        return []
