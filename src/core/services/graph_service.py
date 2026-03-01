from typing import List, Dict, Any
from src.db.client import db_client
from src.infrastructure.llm.factory import EmbeddingFactory
from src.core.logging import get_logger

logger = get_logger(__name__)

class GraphRAGService:
    """
    Application service for GraphRAG queries and simulations.
    Decouples SurrealDB logic from CLI and FastMCP.
    """

    async def get_graph_stats(self) -> Dict[str, Any]:
        """Gets sample nodes and edges for graph visualization."""
        db = await db_client.connect()
        try:
            query_nodes = "SELECT id, file_path, content, array::len(embedding) AS vector_size FROM code_chunk LIMIT 30;"
            nodes_result = await db.query(query_nodes)
            
            query_edges = "SELECT id, in AS source_node, out AS target_node FROM DEPENDS_ON LIMIT 10;"
            edges_result = await db.query(query_edges)
            
            def extract(res):
                if not res or not isinstance(res, list): return []
                if isinstance(res[0], list): return res[0]
                if isinstance(res[0], dict): return res[0].get("result", res)
                return res
            
            return {
                "nodes": extract(nodes_result),
                "edges": extract(edges_result)
            }
        finally:
            await db_client.close()

    async def simulate_query(self, query: str) -> Dict[str, Any]:
        """Executes a full GraphRAG simulation: Vector search + Blast Radius."""
        db = await db_client.connect()
        try:
            # 1. Vector Search
            embedding_service = EmbeddingFactory.create()
            embeddings = await embedding_service.get_document_embeddings([query])
            query_vector = embeddings[0]

            search_query = """
                SELECT id, file_path, content, vector::similarity::cosine(embedding, $query_vector) AS score
                FROM code_chunk ORDER BY score DESC LIMIT 1;
            """
            result = await db.query(search_query, {"query_vector": query_vector})
            
            def extract(res):
                if not res or not isinstance(res, list): return []
                if isinstance(res[0], list): return res[0]
                if isinstance(res[0], dict): return res[0].get("result", res)
                return res

            records = extract(result)
            if not records:
                return {"best_match": None}
                
            best_match = records[0]
            node_id = str(best_match.get("id"))
            
            # 2. Backward Search (Blast Radius)
            blast_query = "SELECT array::distinct(<-DEPENDS_ON<-code_chunk.file_path) AS impacted_files FROM type::record($node_id);"
            blast_result = await db.query(blast_query, {"node_id": node_id})
            blast_records = extract(blast_result)
            impacted = []
            if blast_records and blast_records[0].get("impacted_files"):
                imp = blast_records[0]["impacted_files"]
                impacted = [item for sublist in imp for item in sublist] if isinstance(imp[0], list) else imp

            # 3. Forward Search (Dependencies)
            deps_query = "SELECT array::distinct(->DEPENDS_ON->code_chunk.file_path) AS dependencies FROM type::record($node_id);"
            deps_result = await db.query(deps_query, {"node_id": node_id})
            deps_records = extract(deps_result)
            dependencies = []
            if deps_records and deps_records[0].get("dependencies"):
                deps = deps_records[0]["dependencies"]
                dependencies = [item for sublist in deps for item in sublist] if isinstance(deps[0], list) else deps
                
            return {
                "best_match": best_match,
                "impacted_files": impacted,
                "dependencies": dependencies
            }
        finally:
            await db_client.close()
