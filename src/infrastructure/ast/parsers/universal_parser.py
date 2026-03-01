from typing import List, Dict, Any, Tuple
from src.core.interfaces.ast import IParser
from src.core.parsers import UniversalDependencyDetector

class UniversalFallbackParser(IParser):
    """
    Universal parser acting as a fallback when no AST is available for the language.
    Uses the universal Regex-based dependency detector and splits text into basic blocks.
    """

    def parse(self, content: str, extension: str) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
        # 1. Relation Extraction (Universal / Regex)
        imports = UniversalDependencyDetector.extract_imports(content)
        relations = {
            "imports": imports,
            "calls": [] # Without advanced AST we do not easily extract local calls
        }

        # 2. Basic Chunking (Fallback)
        # Could be replaced by Langchain's RecursiveCharacterTextSplitter
        # For now we roughly split it if it's too long, or send the whole file.
        lines = content.splitlines()
        chunks = []
        
        # Simple chunking strategy: If > 150 lines, split into blocks of 100.
        MAX_LINES = 100
        if len(lines) > 150:
            for i in range(0, len(lines), MAX_LINES):
                chunk_content = "\n".join(lines[i:i + MAX_LINES])
                chunks.append({
                    "symbol_name": f"chunk_{i // MAX_LINES + 1}",
                    "node_type": "text_block",
                    "raw_content": chunk_content,
                    "start_line": i + 1,
                    "end_line": min(i + MAX_LINES, len(lines))
                })
        else:
            chunks.append({
                "symbol_name": "module",
                "node_type": "file",
                "raw_content": content,
                "start_line": 1,
                "end_line": len(lines)
            })

        return chunks, relations
