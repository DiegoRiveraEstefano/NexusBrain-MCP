from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod


class IParser(ABC):
    """
    Base contract for any parser (AST or Fallback).
    Must be able to split code into semantic chunks and extract relations.
    """

    @abstractmethod
    def parse(
        self, content: str, extension: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
        """
        Processes source code.

        Args:
            content (str): Source code to process.
            extension (str): File extension (e.g. '.py', '.txt').

        Returns:
            Tuple:
                - List of dictionaries (Chunks). Ex: [{"symbol_name": "...", "raw_content": "...", ...}]
                - Dictionary with relations. Ex: {"imports": [...], "calls": [...]}
        """
        pass
