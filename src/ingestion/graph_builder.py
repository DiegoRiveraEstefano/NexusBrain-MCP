"""
Graph Building Module (GraphRAG).
Responsible for creating edges (relationships) between code chunks
in SurrealDB based on previously extracted dependencies.
"""

from pathlib import Path
from typing import Any, Dict, List

from src.core.logging import get_logger
from src.db.client import db_client
from src.db.repositories.queries import INGEST_RELATE_CHUNKS_TEMPLATE

logger = get_logger(__name__)


async def build_graph_edges(
    file_to_ids: Dict[str, List[str]], file_imports_map: Dict[str, List[str]]
) -> int:
    """
    Builds the Graph using fuzzy resolution for module names.
    Applies the "Dependency Inheritance" principle: if a file imports a module,
    all chunks of that file inherit the dependency.
    """
    edges_created = 0

    if not file_to_ids or not file_imports_map:
        logger.warning("GraphBuilder.build_graph_edges.insufficient_data")
        return 0

    logger.info("GraphBuilder.build_graph_edges.start")

    # Connect to DB
    db = await db_client.connect()

    # 1. Create index of Stems to IDs for O(1) lookups
    # Example: 'client' -> ['code_chunk:123', 'code_chunk:124']
    stem_to_ids: Dict[str, List[str]] = {}
    for target_file, target_chunk_ids in file_to_ids.items():
        base_name = Path(target_file).stem
        stem_to_ids[base_name] = target_chunk_ids

    # 2. Connect Nodes iterating over our in-memory map
    for source_file, source_chunk_ids in file_to_ids.items():
        source_stem = Path(source_file).stem

        # Get rich imports (Ex: ['src.db.client.DatabaseClient'])
        imported_modules = file_imports_map.get(source_file, [])

        for full_import_string in imported_modules:
            # Break down string for fuzzy search:
            # 'src.db.client.DatabaseClient' -> ['src', 'db', 'client', 'DatabaseClient']
            parts = full_import_string.replace("/", ".").split(".")

            for part in parts:
                # If any of the parts matches the name of a local file
                if part in stem_to_ids and part != source_stem:
                    # The target will be the first chunk of the imported file (usually the header/main class)
                    target_id = stem_to_ids[part][0]

                    # We inherit the connection to ALL chunks of the source file
                    for source_id in source_chunk_ids:
                        try:
                            await db.query(
                                INGEST_RELATE_CHUNKS_TEMPLATE.format(
                                    source_id=source_id, target_id=target_id
                                )
                            )
                            edges_created += 1
                        except Exception as e:
                            logger.error(
                                "GraphBuilder.build_graph_edges.create_edge_failed",
                                source_id=source_id,
                                target_id=target_id,
                                error=str(e),
                            )

                    # Break inner loop to not create duplicate relations
                    # if the import had the same name twice (e.g. db.db)
                    break

    return edges_created
