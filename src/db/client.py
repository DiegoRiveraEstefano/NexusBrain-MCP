"""
Main SurrealDB client and schema definition.
Handles connection, authentication, and creation of tables/indexes (graphs and vectors).
"""

from surrealdb import AsyncSurreal

from src.core.logging import get_logger
from src.core.settings import settings
from src.db.repositories.queries import SCHEMA_DEFINITION_TEMPLATE

logger = get_logger(__name__)

# Dimensions of the huggingface all-MiniLM-L6-v2 model
EMBEDDING_DIMENSIONS = 384


class DatabaseClient:
    """Manages the Singleton connection to SurrealDB."""

    def __init__(self) -> None:
        self.db: AsyncSurreal | None = None
        self._token: str | None = None

    async def connect(self) -> AsyncSurreal:
        """
        Establishes connection with SurrealDB and authenticates the user.

        Returns:
            Surreal: The connected database instance.

        Raises:
            ConnectionError: If the connection to the database fails.
        """
        if self.db is not None:
            return self.db

        try:
            logger.info("DatabaseClient.connect.start", url=settings.surreal_url)
            self.db = AsyncSurreal(settings.surreal_url)
            await self.db.connect()
            if (
                not settings.surreal_url.startswith("file")
                or settings.surreal_url.startswith("surrealkv")
                or settings.surreal_url.startswith("mem")
            ):
                self._token = await self.db.signin(
                    {"username": settings.surreal_user, "password": settings.surreal_pass}
                )
            await self.db.use(settings.surreal_namespace, settings.surreal_database)

            logger.info("DatabaseClient.connect.success")
            return self.db
        except Exception as e:
            logger.error("DatabaseClient.connect.failed", error=str(e))
            raise ConnectionError(f"Could not initialize DB: {e}") from e

    async def close(self) -> None:
        """Closes the connection with the database."""
        if self.db:
            await self.db.close()
            self.db = None
            logger.info("DatabaseClient.close.success")

    async def setup_schema(self) -> None:
        """
        Initializes the tables, fields, and vector indexes necessary
        for GraphRAG to work.
        """
        db = await self.connect()
        logger.info("DatabaseClient.setup_schema.start")

        schema_queries = SCHEMA_DEFINITION_TEMPLATE.format(
            embedding_dimensions=EMBEDDING_DIMENSIONS
        )
        try:
            await db.query(schema_queries)
            logger.info("DatabaseClient.setup_schema.success")
        except Exception as e:
            logger.error("DatabaseClient.setup_schema.failed", error=str(e))
            raise


# Global instance to be injected into repositories
db_client = DatabaseClient()
