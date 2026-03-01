"""
MCP routes and tools exposed to the AI.
The tools delegate the logic to the services layer.
"""

from mcp.server.fastmcp import FastMCP

from src.core.consts import (
    BLAST_RADIUS_FOOTER,
    BLAST_RADIUS_HEADER_TEMPLATE,
    BLAST_RADIUS_NO_AFFECTED_NODES_TEMPLATE,
    BLAST_RADIUS_NO_DEPENDENTS_TEMPLATE,
    BLAST_RADIUS_RESULT_ITEM_TEMPLATE,
    EXEC_FLOW_HEADER_TEMPLATE,
    EXEC_FLOW_NO_DEPENDENCIES_TEMPLATE,
    EXEC_FLOW_NO_OUTGOING_TEMPLATE,
    EXEC_FLOW_RESULT_ITEM_TEMPLATE,
    NO_RATIONALE,
    NO_TITLE,
    RECORD_DECISION_FAILURE,
    RECORD_DECISION_LINK_SUCCESS_TEMPLATE,
    RECORD_DECISION_SUCCESS_TEMPLATE,
    RECORD_DECISION_TOPIC_TEMPLATE,
    SEARCH_MEMORY_HEADER_TEMPLATE,
    SEARCH_MEMORY_NO_RESULTS_TEMPLATE,
    SEARCH_MEMORY_RESULT_ITEM_TEMPLATE,
    SEMANTIC_SEARCH_CODE_BLOCK_TEMPLATE,
    SEMANTIC_SEARCH_HEADER_TEMPLATE,
    SEMANTIC_SEARCH_NO_RESULTS,
    SEMANTIC_SEARCH_RESULT_ITEM_TEMPLATE,
    TOOL_ERROR_TEMPLATE,
    UNKNOWN_DATE,
    UNKNOWN_ID,
    UNKNOWN_PATH,
    INGEST_REPO_RESULT_TEMPLATE,
)
from src.core.logging import get_logger
from src.core.services.ingestion_service import IngestionService

# Import Concrete Services and Repositories
from src.core.services.search_service import SearchService
from src.core.services.memory_service import MemoryService

from src.infrastructure.db.surreal_repository import SurrealGraphRepository, SurrealMemoryRepository

print("a.2")
from src.infrastructure.llm.factory import EmbeddingFactory

logger = get_logger(__name__)

# Dependency instantiation (Ideally through a DI container,
# but doing it here to simplify for now)
graph_repo = SurrealGraphRepository()
memory_repo = SurrealMemoryRepository()


def get_search_service() -> SearchService:
    # Created on demand to instantiate the EmbeddingProvider correctly (depends on config)
    return SearchService(graph_repo, EmbeddingFactory.create())


def get_memory_service() -> MemoryService:
    return MemoryService(memory_repo)


def register_routes(mcp: FastMCP):

    @mcp.tool()
    async def semantic_code_search(query: str, limit: int = 5) -> str:
        """
        Searches for code chunks in the repository using semantic search (meaning).
        """
        logger.info("MCP.semantic_code_search.start", query=query, limit=limit)
        try:
            service = get_search_service()
            results = await service.search_similar_code(query, limit)

            if not results:
                return SEMANTIC_SEARCH_NO_RESULTS

            formatted_response = SEMANTIC_SEARCH_HEADER_TEMPLATE.format(query=query)
            for idx, match in enumerate(results, 1):
                file_path = match.get("file_path", UNKNOWN_PATH)
                score = match.get("similarity_score", 0.0)
                content = match.get("content", "")

                formatted_response += SEMANTIC_SEARCH_RESULT_ITEM_TEMPLATE.format(
                    index=idx, file_path=file_path, score=score
                )
                formatted_response += SEMANTIC_SEARCH_CODE_BLOCK_TEMPLATE.format(content=content)

            return formatted_response
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="semantic_code_search", error=str(e))
            logger.error("MCP.semantic_code_search.error", error=str(e))
            return error_msg

    @mcp.tool()
    async def analyze_blast_radius(node_id: str, depth: int = 2) -> str:
        """
        Analyzes the "blast radius" of a code chunk.
        """
        logger.info("MCP.analyze_blast_radius.start", node_id=node_id, depth=depth)
        try:
            service = get_search_service()
            results = await service.analyze_blast_radius(node_id, depth)

            if not results:
                return BLAST_RADIUS_NO_DEPENDENTS_TEMPLATE.format(node_id=node_id)

            formatted_response = BLAST_RADIUS_HEADER_TEMPLATE.format(node_id=node_id)
            affected_nodes = results[0].get("affected_by", [])

            if not affected_nodes:
                return BLAST_RADIUS_NO_AFFECTED_NODES_TEMPLATE.format(node_id=node_id)

            for idx, node in enumerate(affected_nodes, 1):
                file_path = node.get("file_path", UNKNOWN_PATH)
                formatted_response += BLAST_RADIUS_RESULT_ITEM_TEMPLATE.format(
                    index=idx, file_path=file_path, node_id=node.get("id")
                )

            formatted_response += BLAST_RADIUS_FOOTER
            return formatted_response
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="analyze_blast_radius", error=str(e))
            logger.error("MCP.analyze_blast_radius.error", error=str(e))
            return error_msg

    @mcp.tool()
    async def get_execution_flow(node_id: str) -> str:
        """
        Shows the execution flow or outgoing dependencies of a code chunk.
        """
        logger.info("MCP.get_execution_flow.start", node_id=node_id)
        try:
            service = get_search_service()
            results = await service.get_execution_flow(node_id)

            if not results:
                return EXEC_FLOW_NO_DEPENDENCIES_TEMPLATE.format(node_id=node_id)

            formatted_response = EXEC_FLOW_HEADER_TEMPLATE.format(node_id=node_id)
            dependencies = results[0].get("dependencies", [])

            if not dependencies:
                return EXEC_FLOW_NO_OUTGOING_TEMPLATE.format(node_id=node_id)

            for dep in dependencies:
                file_path = dep.get("file_path", UNKNOWN_PATH)
                formatted_response += EXEC_FLOW_RESULT_ITEM_TEMPLATE.format(
                    file_path=file_path, dep_id=dep.get("id")
                )
            return formatted_response
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="get_execution_flow", error=str(e))
            logger.error("MCP.get_execution_flow.error", error=str(e))
            return error_msg

    @mcp.tool()
    async def record_decision(
        topic: str, rationale: str, related_code_id: str | None = None
    ) -> str:
        """
        Records an architectural decision, the solution to a complex bug, or a business rule.
        """
        logger.info("MCP.record_decision.start", topic=topic, related_code_id=related_code_id)
        try:
            service = get_memory_service()
            result = await service.record_decision(topic, rationale, related_code_id)

            if not result:
                return RECORD_DECISION_FAILURE

            record_id = result.get("id", UNKNOWN_ID)
            response = RECORD_DECISION_SUCCESS_TEMPLATE.format(record_id=record_id) + "\n"
            response += RECORD_DECISION_TOPIC_TEMPLATE.format(topic=topic) + "\n"

            if related_code_id:
                response += RECORD_DECISION_LINK_SUCCESS_TEMPLATE.format(
                    related_code_id=related_code_id
                )

            return response
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="record_decision", error=str(e))
            logger.error("MCP.record_decision.error", error=str(e))
            return error_msg

    @mcp.tool()
    async def search_memory(keyword: str) -> str:
        """
        Searches the project historical log (long-term memory).
        """
        logger.info("MCP.search_memory.start", keyword=keyword)
        try:
            service = get_memory_service()
            results = await service.search_memory(keyword)

            if not results:
                return SEARCH_MEMORY_NO_RESULTS_TEMPLATE.format(keyword=keyword)

            formatted_response = SEARCH_MEMORY_HEADER_TEMPLATE.format(keyword=keyword)
            for idx, log in enumerate(results, 1):
                topic = log.get("topic", NO_TITLE)
                rationale = log.get("rationale", NO_RATIONALE)
                created_at = log.get("created_at", UNKNOWN_DATE)

                formatted_response += SEARCH_MEMORY_RESULT_ITEM_TEMPLATE.format(
                    index=idx, topic=topic, created_at=created_at, rationale=rationale
                )
            return formatted_response
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="search_memory", error=str(e))
            logger.error("MCP.search_memory.error", error=str(e))
            return error_msg

    @mcp.tool()
    async def ingest_path(repo_path: str):
        logger.info("MCP.ingest_path.start", repo_path=repo_path)
        service = IngestionService()
        try:
            result = await service.run_ingestion(repo_path_str=repo_path)
            return INGEST_REPO_RESULT_TEMPLATE.format(**result)
        except Exception as e:
            error_msg = TOOL_ERROR_TEMPLATE.format(tool_name="ingest_path", error=str(e))
            logger.error("MCP.ingest_path.error", error=str(e))
            return error_msg
