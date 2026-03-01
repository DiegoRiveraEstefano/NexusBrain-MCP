"""
Main entry point for the NexusBrain MCP server.
Manages the lifecycle of the HTTP/SSE connection using an ASGI server (Uvicorn).
"""

import asyncio
import sys

print("a")
from mcp.server.fastmcp import FastMCP

print("b")
from src.core.consts import APP_NAME

print("c")
from src.core.logging import get_logger, setup_logging

print("d")
from src.core.settings import settings

print("e")
from src.db.client import db_client

print("f")
from src.presentation.mcp.routes import register_routes

print("g")
# Configure logging (now we can use stdout freely thanks to SSE)
setup_logging()
logger = get_logger(__name__)

# Initialize FastMCP server in HTTP/SSE mode
mcp = FastMCP(
    name=APP_NAME,
    host=settings.host,
    port=settings.port,
)
# Register all tools (routes)
register_routes(mcp)


async def init_infrastructure() -> None:
    """Ensures SurrealDB is alive and schemas are created."""
    try:
        logger.info("Server.init_infrastructure.checking_database")
        await db_client.setup_schema()
    except Exception as e:
        logger.error("Server.init_infrastructure.failed", error=str(e))
        sys.exit(1)


def main() -> None:
    """Startup function."""
    logger.info("Server.main.startup", mode="SSE")

    try:
        # Initialize the database
        asyncio.run(init_infrastructure())
    except KeyboardInterrupt:
        logger.info("Server.main.cancelled")
        sys.exit(0)

    logger.info("Server.main.infrastructure_ready", url="http://localhost:8080/sse")

    try:
        # Use SSE transport; FastMCP starts uvicorn internally
        mcp.run(transport="sse")
    except Exception as e:
        logger.error("Server.main.unexpected_error", error=str(e))
    finally:
        logger.info("Server.main.shutdown")


if __name__ == "__main__":
    main()
