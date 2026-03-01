from typing import List, Dict, Any, Tuple
from src.core.interfaces.ast import IParser
from src.infrastructure.ast.chunker import ASTChunker
from src.infrastructure.ast.extractor import ASTExtractor


class TreeSitterPythonParser(IParser):
    """Adapter that encapsulates the original Tree-sitter logic for Python."""

    def __init__(self):
        self.chunker = ASTChunker()
        self.extractor = ASTExtractor()

    def parse(
        self, content: str, extension: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
        # We forcefully use 'python' here since this parser is specific
        chunks = self.chunker.get_semantic_chunks(content, language_hint="python")
        relations = self.extractor.get_relationships(content, language_hint="python")
        return chunks, relations
