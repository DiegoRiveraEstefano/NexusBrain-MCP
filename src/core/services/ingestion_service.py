import time
from pathlib import Path
from typing import List, Callable, Optional, Any, Dict

from src.core.logging import get_logger
from src.db.client import db_client
from src.ingestion.processor import process_files_batch
from src.ingestion.indexer import index_chunks
from src.ingestion.graph_builder import build_graph_edges

logger = get_logger(__name__)

class IngestionService:
    """
    Application service to orchestrate codebase ingestion.
    Decoupled from user interface (UI/Console).
    """

    def scan_directory(self, repo_path: Path, ignore_dirs: Optional[List[str]] = None) -> List[Path]:
        """Recursively searches for valid source code files."""
        if ignore_dirs is None:
            ignore_dirs = [".git", ".venv", "node_modules", "__pycache__", "data", "logs", ".idea", "dist", "build"]

        valid_extensions = {".py", ".md", ".ts", ".js"}
        found_files = []

        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in valid_extensions:
                if not any(ignored in file_path.parts for ignored in ignore_dirs):
                    found_files.append(file_path)

        return found_files

    async def run_ingestion(
        self, 
        repo_path_str: str, 
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the full modular ingestion flow.
        Notifies progress through progress_callback to paint interfaces if required.
        """
        repo_path = Path(repo_path_str).resolve()
        
        if not repo_path.exists() or not repo_path.is_dir():
            raise ValueError(f"Path {repo_path} is not a valid directory.")
            
        start_time = time.time()
        
        try:
            # Phase 1: Scanning
            if progress_callback: progress_callback("scan_start", 0, 0)
            files = self.scan_directory(repo_path)
            if not files:
                return {"status": "empty", "files": 0, "time": time.time() - start_time}
            if progress_callback: progress_callback("scan_done", len(files), 0)

            # Phase 2: AST Processing
            if progress_callback: progress_callback("process_start", 0, 0)
            chunks, imports_map = await process_files_batch(files, repo_path)
            if progress_callback: progress_callback("process_done", len(chunks), 0)

            # Phase 3: Indexing
            if progress_callback: progress_callback("index_start", 0, 0)
            file_to_ids = await index_chunks(chunks)
            if progress_callback: progress_callback("index_done", 0, 0)

            # Phase 4: Graph
            if progress_callback: progress_callback("graph_start", 0, 0)
            edges_created = await build_graph_edges(file_to_ids, imports_map)
            if progress_callback: progress_callback("graph_done", edges_created, 0)

            elapsed = time.time() - start_time
            return {
                "status": "success",
                "files": len(files),
                "chunks": len(chunks),
                "edges": edges_created,
                "time": elapsed
            }
        except Exception as e:
            logger.error("IngestionService.run_ingestion.failed", error=str(e), exc_info=True)
            raise
        finally:
            await db_client.close()
