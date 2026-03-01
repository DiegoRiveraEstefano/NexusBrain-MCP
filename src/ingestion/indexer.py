"""
Indexing Module.
Generates vector embeddings for code chunks and
inserts them concurrently into the SurrealDB database.
"""

import asyncio
from typing import Any, Coroutine, Dict, List

from src.core.logging import get_logger
from src.db.client import db_client
from src.db.repositories.queries import INGEST_CREATE_CODE_CHUNK_QUERY
from src.infrastructure.llm.factory import EmbeddingFactory

logger = get_logger(__name__)


async def insert_chunk(db: Any, chunk_data: Dict[str, Any]) -> Dict[str, str] | None:
    """
    Inserts a single chunk into SurrealDB safely.
    Includes universal logic to unpack responses from the Rust SDK.
    """
    try:
        result = await db.query(INGEST_CREATE_CODE_CHUNK_QUERY, chunk_data)
    except Exception as e:
        logger.error(
            "Indexer.insert_chunk.failed", error=str(e), file_path=chunk_data.get("file_path")
        )
        return None

    records = []
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list):
            records = result[0]
        elif isinstance(result[0], dict):
            # Format with 'result' wrapper
            if "result" in result[0]:
                if result[0].get("status") == "ERR":
                    logger.error("Indexer.insert_chunk.db_error", detail=result[0].get("detail"))
                    return None
                records = result[0].get("result", [])
            else:
                # Raw data directly
                records = result

    if records and isinstance(records, list) and len(records) > 0:
        record_id = str(records[0].get("id", ""))
        return {"id": record_id, "file_path": chunk_data["file_path"]}

    return None


async def index_chunks(chunks_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Takes the enriched chunks, calculates their embeddings in batch,
    inserts them into the database concurrently, and returns a map
    of files and their real IDs to build the Graph later.
    """
    if not chunks_data:
        return {}

    logger.info("Indexer.index_chunks.start_embeddings", chunks_count=len(chunks_data))

    # 1. Extract only the enriched text for the model
    all_contents = [chunk["content"] for chunk in chunks_data]

    # 2. Batch Generation (Much faster than one by one)
    embedding_service = EmbeddingFactory.create()
    all_embeddings = await embedding_service.get_document_embeddings(all_contents)

    # 3. Assign the vector back to its corresponding dictionary
    for i, chunk in enumerate(chunks_data):
        chunk["embedding"] = all_embeddings[i]

    logger.info("Indexer.index_chunks.start_insert", chunks_count=len(chunks_data))

    # Connect to DB for this batch
    db = await db_client.connect()

    # 4. Asynchronous Bulk Insertion
    tasks: List[Coroutine[Any, Any, Dict[str, str] | None]] = []
    for data in chunks_data:
        tasks.append(insert_chunk(db, data))

    # Wait for ALL insertions to finish at the same time
    results = await asyncio.gather(*tasks)

    # 5. Build the map of paths to IDs (file_to_ids)
    file_to_ids: Dict[str, List[str]] = {}
    for res in results:
        if res:
            chunk_id = res["id"]
            file_path = res["file_path"]
            if file_path not in file_to_ids:
                file_to_ids[file_path] = []
            file_to_ids[file_path].append(chunk_id)

    return file_to_ids
