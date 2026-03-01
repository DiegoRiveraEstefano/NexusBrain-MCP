"""
Semantic Chunking Module using Tree-sitter.
Replaces text-based splitters with Abstract Syntax Tree (AST) analyzers.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Import Tree-sitter dependencies
from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython

from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SemanticChunk:
    """Represents a code fragment with real structural meaning."""
    name: str  # Ex: "get_embeddings" or "DatabaseClient.connect"
    node_type: str  # Ex: "function", "class", "module_header"
    content: str  # The actual source code of the fragment
    start_line: int
    end_line: int
    parent_class: str = ""  # If it is a method, the class name goes here


class ASTChunker:
    """
    Chunks source code based on its logical structure (Classes and Functions)
    instead of counting arbitrary characters.
    """

    def __init__(self):
        # Initialize parser for Python by default.
        # In the future you can add a dictionary of languages for TS, JS, Go.
        self.py_language = Language(tspython.language())
        self.parser = Parser()
        self.parser.language = self.py_language

    def _get_node_name(self, node: Node, source_bytes: bytes) -> str:
        """Extracts the name of a class or function by looking for its 'identifier' node."""
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf8')
        return "anonymous"

    def _walk_tree(self, node: Node, source_bytes: bytes, current_class: str = "") -> List[SemanticChunk]:
        """
        Recursively walks the AST.
        If it finds a function, it extracts the whole function.
        If it finds a class, it saves the context and extracts its methods.
        """
        chunks = []

        if node.type == 'class_definition':
            # It's a class. Get its name.
            class_name = self._get_node_name(node, source_bytes)

            # (Optional) We could extract the class docstring here

            # Walk the class body looking for methods (functions)
            for child in node.children:
                if child.type == 'block':
                    for statement in child.children:
                        # Pass the class name as context
                        chunks.extend(self._walk_tree(statement, source_bytes, current_class=class_name))

            # Prevent further walking of children outside the block
            return chunks

        elif node.type == 'function_definition':
            func_name = self._get_node_name(node, source_bytes)
            full_name = f"{current_class}.{func_name}" if current_class else func_name

            chunk = SemanticChunk(
                name=full_name,
                node_type="method" if current_class else "function",
                content=node.text.decode('utf8'),
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parent_class=current_class
            )
            chunks.append(chunk)

            # Return immediately to NOT split nested functions inside.
            # We want the LLM to see the entire function in a single vector.
            return chunks

        else:
            # If not a class or function, keep looking deeper
            for child in node.children:
                chunks.extend(self._walk_tree(child, source_bytes, current_class))

        return chunks

    def get_semantic_chunks(self, code_content: str, language_hint: str = "py") -> List[Dict[str, Any]]:
        """
        Main entry point. Parses code and returns chunks ready
        to be injected with context and vectorized.
        """
        if not code_content.strip():
            return []

        # If the language is not Python (not yet supported in AST), we return the whole file
        # as a safe fallback.
        if language_hint not in ("py", "python"):
            logger.debug("ASTChunker.get_semantic_chunks.unsupported_language_fallback", language=language_hint)
            return [{
                "name": "module",
                "node_type": "file",
                "content": code_content,
                "start_line": 1,
                "end_line": len(code_content.splitlines()),
                "parent_class": ""
            }]

        source_bytes = bytes(code_content, "utf8")
        tree = self.parser.parse(source_bytes)

        # Walk tree from the root
        semantic_chunks = self._walk_tree(tree.root_node, source_bytes)

        # Convert dataclasses to standard dictionaries for the pipeline
        results = []
        for chunk in semantic_chunks:
            results.append({
                "symbol_name": chunk.name,
                "node_type": chunk.node_type,
                "raw_content": chunk.content,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line
            })

        return results
