from src.core.interfaces.ast import IParser
from src.infrastructure.ast.parsers.python_parser import TreeSitterPythonParser
from src.infrastructure.ast.parsers.universal_parser import UniversalFallbackParser

class ParserFactory:
    """Factory that returns the appropriate parser based on the file extension."""

    @staticmethod
    def get_parser(extension: str) -> IParser:
        # In the future you can register more parsers here
        if extension.lower() in [".py"]:
            return TreeSitterPythonParser()
        
        # Universal fallback for any other extension or flat files
        return UniversalFallbackParser()
