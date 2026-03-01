"""
Hybrid Semantic Extraction Module.
Uses Regex for global dependencies (infallible) and AST for calls and logic (precision).
"""

from typing import Any, Dict, List

from tree_sitter import Language, Parser
import tree_sitter_python as tspython

from src.core.parsers import UniversalDependencyDetector
from src.core.logging import get_logger

logger = get_logger(__name__)

class ASTExtractor:
    def __init__(self):
        self.py_language = Language(tspython.language())
        self.parser = Parser()
        self.parser.language = self.py_language

        # We only search for function calls (Calls) with AST
        self.py_query = self.py_language.query("""
            (call function: (identifier) @call.direct)
            (call function: (attribute attribute: (identifier) @call.method))
        """)

    def get_relationships(self, code_content: str, language_hint: str = "py") -> Dict[str, List[str]]:
        if not code_content.strip():
            return {"imports": [], "calls": []}

        # 🛡️ 1. IMPORTS: We use the infallible Regex engine
        imports = UniversalDependencyDetector.extract_imports(code_content)
        calls_set = set()

        # 🧠 2. CALLS: We use AST to extract real execution flows
        if language_hint in ("py", "python"):
            try:
                source_bytes = bytes(code_content, "utf8")
                tree = self.parser.parse(source_bytes)

                # Universal compatibility with any Tree-sitter version
                if hasattr(self.py_query, "matches"):
                    matches = self.py_query.matches(tree.root_node)
                    for pattern_index, captures in matches:
                        for capture_name, nodes in captures.items():
                            if not isinstance(nodes, list):
                                nodes = [nodes]
                            for node in nodes:
                                text = node.text.decode('utf8') if isinstance(node.text, bytes) else node.text
                                # Filter generic Python built-in methods
                                if text not in ("print", "len", "str", "int", "list", "dict", "set", "Exception", "super"):
                                    calls_set.add(text)
                else:
                    captures = getattr(self.py_query, "captures", lambda x: [])(tree.root_node)
                    for node, capture_name in captures:
                        text = node.text.decode('utf8') if isinstance(node.text, bytes) else node.text
                        if text not in ("print", "len", "str", "int", "list", "dict", "set", "Exception", "super"):
                            calls_set.add(text)
            except Exception as e:
                logger.debug("ASTExtractor.get_relationships.ast_error", error=str(e))

        return {
            "imports": imports,
            "calls": sorted(list(calls_set))
        }
