# Style Guide and Best Practices (NexusBrain MCP)

This document defines the coding standards, project structure, and best practices to be followed to ensure that NexusBrain MCP code remains clean, scalable, and robust.

---

## 1. Project Structure

The project follows a `src/`-based directory layout, which prevents import-related issues and ensures that the packaged code matches exactly what is tested.

```text
nexusbrain-mcp/
├── src/
│   └── nexusbrain/          # Main source code
│       ├── __init__.py
│       ├── main.py          # Entry point (MCP Server)
│       ├── cli/             # CLI command definitions
│       ├── core/            # Pure business logic (GraphRAG, Chunking)
│       ├── db/              # SurrealDB connections and repositories
│       ├── llm/             # LangChain / Ollama integration
│       └── tools/           # MCP tool definitions (@mcp.tool)
├── tests/                   # Unit and integration tests (pytest)
├── scripts/                 # Utility scripts (e.g., repository ingestion)
├── pyproject.toml           # Project configuration and dependencies
├── README.md
└── STYLE_GUIDE.md
```

---

## 2. Code Style and Formatting

**[Ruff](https://docs.astral.sh/ruff/)** is used as the unified tool for linting and formatting (replacing Black, Flake8, and isort).

* **Line length:** Maximum 88 characters.
* **Quotes:** Use double quotes `"` for strings, except when the string contains double quotes.
* **Imports:** Must be ordered alphabetically and separated into three logical blocks:
  1. Standard library (`os`, `sys`, `typing`).
  2. Third-party libraries (`mcp`, `langchain`, `surrealdb`).
  3. Local imports (`src.nexusbrain.db`).

---

## 3. Strict Type Hinting

The project requires **100% type coverage**. While Python is dynamically typed, NexusBrain enforces strict typing. `mypy` is used for static type validation.

**Incorrect:**

```python
def process_data(data, max_items=10):
    return [item.name for item in data[:max_items]]
```

**Correct:**

```python
from typing import Any

def process_data(data: list[Any], max_items: int = 10) -> list[str]:
    return [item.name for item in data[:max_items]]
```

* **Golden rule:** Every function, method, and class must have explicit input and return type annotations (`->`).

---

## 4. Documentation and Docstrings

The **Google Docstring Style** standard is used. All public functions, classes, and modules must include documentation.

**Expected Docstring Example:**

```python
async def analyze_blast_radius(file_path: str, depth: int = 2) -> list[dict[str, Any]]:
    """
    Analyzes the dependency graph in SurrealDB to identify affected files.

    Args:
        file_path (str): The relative path of the modified file.
        depth (int, optional): Search depth in the graph. Defaults to 2.

    Returns:
        list[dict[str, Any]]: List of affected nodes with their relationship type.

    Raises:
        NodeNotFoundError: If the specified file does not exist in the graph.
    """
```

---

## 5. Asynchronous Programming

Given that MCP operations and LLM/database calls are I/O-bound, **the entire core of the project must be asynchronous**.

* Use `async def` for any function that interacts with SurrealDB, Ollama, or the MCP client.
* **Never use blocking functions** (such as `time.sleep()` or `requests.get()`) within a coroutine. Use `asyncio.sleep()` or `httpx` instead.
* Prefer `async with` for resource management (database connections, file handles).

---

## 6. Error Handling and Logging

* **Do not use `print()`**. Use Python's standard `logging` module or libraries such as `loguru`. Print statements interfere with the `stdio` transport used by the MCP protocol.
* **Custom exceptions:** Create specific error classes in `src/nexusbrain/core/exceptions.py` instead of raising generic `Exception` instances.

**Example:**

```python
import logging
import surrealdb

logger = logging.getLogger(__name__)

async def connect_db():
    try:
        await surrealdb.connect()
    except ConnectionError as e:
        logger.error(f"Failed to connect to SurrealDB: {e}")
        raise DatabaseInitializationError("Could not initialize SurrealDB") from e
```

---

## 7. Dependency Management

* `pyproject.toml` serves as the single source of truth for dependencies.
* Modern dependency managers such as **Poetry** or **uv** are recommended for managing virtual environments and installing packages.
* Development dependencies (`pytest`, `ruff`, `mypy`) must be strictly separated from production dependencies.

---

## 8. MCP Tool Design

When creating a new tool exposed to the LLM using the `@mcp.tool()` decorator, adhere to the following guidelines:

1. Use a descriptive name in `snake_case`.
2. Write an exceptionally clear docstring, as **the LLM reads the docstring** to determine when and how to use the tool.
3. Use Pydantic models or strict type annotations to validate input parameters received from the LLM before processing.

**Example:**

```python
from mcp import server
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    query: str = Field(description="Natural language description of the code to search")
    limit: int = Field(default=5, ge=1, le=20)

@server.tool()
async def semantic_code_search(query: SearchQuery) -> list[dict[str, Any]]:
    """
    Performs a vector-based semantic search across indexed code chunks.

    This tool retrieves code snippets that are semantically similar to the
    provided natural language query, using local embeddings generated by Ollama.

    Args:
        query (SearchQuery): The search parameters including query text and result limit.

    Returns:
        list[dict[str, Any]]: List of matching code chunks with metadata and relevance scores.
    """
    # Implementation here
    pass
```

---

## 9. Testing Standards

* All new features and bug fixes must include corresponding unit or integration tests.
* Tests should be written using `pytest` and placed in the `tests/` directory, mirroring the source structure.
* Use `pytest-asyncio` for testing asynchronous functions.
* Mock external dependencies (e.g., Ollama, SurrealDB) using `unittest.mock` or `pytest-mock` to ensure tests are fast and deterministic.

---

## 10. Continuous Integration

* All pull requests must pass CI checks, including:
  - Type checking with `mypy`
  - Linting and formatting with `ruff`
  - Unit and integration tests with `pytest`
* Ensure local validation (`ruff check .`, `mypy src/`, `pytest`) before pushing changes.

---

*Adherence to this guide ensures consistency, maintainability, and reliability across the NexusBrain MCP codebase.*
