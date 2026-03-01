"""
Ingestion Processing Module.
Responsible for reading files, sending them to the AST engine for analysis,
and injecting context metadata (headers) before vectorizing them.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.infrastructure.ast.factory import ParserFactory
from src.core.logging import get_logger

logger = get_logger(__name__)


async def process_file(
    file_path: Path, repo_path: Path
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Reads the file, extracts dependencies using the AST Manager and generates enriched chunks.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("Processor.process_file.decode_error", file_path=str(file_path))
        return [], []

    if not content.strip():
        return [], []

    extension = file_path.suffix
    relative_path = str(file_path.relative_to(repo_path))

    # Extract basic spatial metadata
    path_parts = relative_path.split(os.sep)
    directory = os.sep.join(path_parts[:-1]) if len(path_parts) > 1 else 'root'
    lang_hint = extension.lstrip('.') if extension else 'text'

    parser = ParserFactory.get_parser(extension)
    ast_chunks, relations = parser.parse(content, extension)

    # Extract globally detected imports in this file
    file_imports = relations.get("imports", [])
    imports_str = ", ".join(file_imports) if file_imports else "None"

    processed_chunks = []

    for i, chunk in enumerate(ast_chunks):
        # The ASTChunker gives us precise names (e.g. 'DatabaseClient.connect')
        symbol = chunk.get("symbol_name", "module")
        node_type = chunk.get("node_type", "chunk")

        # 💉 ULTRA-ENRICHED CONTEXT INJECTION
        context_header = (
            f"### PATH: {relative_path}\n"
            f"### DIR: {directory}\n"
            f"### LANG: {lang_hint}\n"
            f"### SYMBOL: {symbol} ({node_type})\n"  # <- New level of detail thanks to AST!
            f"### IMPORTS: {imports_str}\n"
            f"### CHUNK: {i + 1} of {len(ast_chunks)}\n\n"
        )

        # Join the header with the actual code
        contextual_text = context_header + chunk["raw_content"]

        # Prepare the exact dictionary expected by the Indexer (SurrealDB)
        processed_chunks.append({
            "file_path": relative_path,
            "content": contextual_text,  # Text the model will read and vectorize
            "raw_content": chunk["raw_content"],  # Save raw code just in case
            "symbol_name": symbol,
            "node_type": node_type,
            "embedding": []  # Empty list to be filled in the next phase
        })

    return processed_chunks, file_imports


async def process_files_batch(
    files: List[Path], repo_path: Path
) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    """
    Processes a complete list of files and consolidates the results
    to pass them to the Indexing phase.
    """
    all_chunks = []
    file_imports_map = {}

    for file_path in files:
        chunks, imports = await process_file(file_path, repo_path)

        if chunks:
            all_chunks.extend(chunks)
            # Save the imports map using the relative path for the Graph
            rel_path = str(file_path.relative_to(repo_path))
            file_imports_map[rel_path] = imports

    return all_chunks, file_imports_map
