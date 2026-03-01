import re


class UniversalDependencyDetector:
    """Detects dependencies and specific symbols using multilingual patterns."""

    @classmethod
    def extract_imports(cls, content: str) -> list[str]:
        imports = set()

        # 1. Python: from X import Y, Z
        # Captures the module and specific classes/functions
        for match in re.finditer(r"from\s+([a-zA-Z0-9_.]+)\s+import\s+([^;\n\\]+)", content):
            module = match.group(1)
            symbols = match.group(2).split(",")
            for sym in symbols:
                sym = sym.strip().split(" ")[0]  # Clean alias like 'as X'
                if sym and sym != "*":
                    imports.add(f"{module}.{sym}")  # Ex: src.db.client.DatabaseClient
            imports.add(module)

        # 2. Python/Java/Go: import X
        for match in re.finditer(r"^[ \t]*import\s+([a-zA-Z0-9_.]+)", content, re.MULTILINE):
            imports.add(match.group(1))

        # 3. JS/TS: import { X, Y } from 'module'
        for match in re.finditer(r'import\s+(.*?)\s+from\s+["\']([^"\']+)["\']', content):
            symbols = match.group(1).replace("{", "").replace("}", "").split(",")
            module = match.group(2)
            for sym in symbols:
                sym = sym.strip().split(" ")[0]
                if sym and sym != "*":
                    imports.add(f"{module}.{sym}")
            imports.add(module)

        # 4. C/C++, C#, Rust, Node generic
        for match in re.finditer(
            r'(?:require\(|#include\s+|using\s+)["\']?([^"\';\s\)]+)["\']?', content
        ):
            imports.add(match.group(1))

        return sorted(list(imports))
