# AGENTS.md

## Overview for AI Assistants

This document provides guidance for AI agents (Claude, Cursor, GitHub Copilot, etc.) interacting with the **NexusBrain MCP** codebase. It outlines architectural context, development patterns, and best practices to ensure high-quality, consistent contributions.

---

## Primary Objectives When Assisting

1. **Preserve Architecture**: Respect the modular separation (`core/`, `llm/`, `db/`, `tools/`).
2. **Maintain Async-First Design**: All I/O-bound operations must be asynchronous.
3. **Enforce Type Safety**: 100% type hint coverage is required; use `mypy`-compatible annotations.
4. **Optimize for MCP**: Tools exposed via `@mcp.tool()` must have clear, LLM-readable docstrings.
5. **Prioritize Locality**: Never suggest solutions that require external API calls unless explicitly requested.

---

## Codebase Navigation Guide

### Key Directories
| Path | Purpose | Agent Guidance |
|------|---------|---------------|
| `src/presentation/mcp/` | MCP server entrypoint and routes | Use SSE transport. Tools delegate logic to `services/`. |
| `src/presentation/cli/` | Command Line Interface | Only UI/Console logic (Rich/Click). No business logic here. |
| `src/core/services/` | Domain logic (Use Cases) | Put core business rules here. Orchestrates Repositories and Providers. |
| `src/core/interfaces/` | Abstract Contracts (Ports) | Define `ABC` classes for DB, LLM, Parsers. Enforce dependency inversion. |
| `src/infrastructure/` | Concrete Implementations (Adapters) | SurrealDB logic, HuggingFace/Ollama bindings, TreeSitter/Fallback parsers. |
| `tests/` | Unit and integration tests | Mirror source structure; use `pytest-asyncio` for async tests |

### Critical Files
- `pyproject.toml`: Single source of truth for dependencies and tooling configuration.
- `src/nexusbrain/core/config.py`: Pydantic-based settings; use `Settings` class for configuration access.
- `src/nexusbrain/core/exceptions.py`: Custom exception hierarchy; prefer specific exceptions over generic ones.

---

## Architectural Patterns

### Async/Await Convention
```python
# Preferred
async def fetch_code_chunk(chunk_id: str) -> CodeChunk | None:
    async with get_db_client() as client:
        return await client.select(chunk_id)

# Avoid
def fetch_code_chunk(chunk_id: str):  # Missing async
    return get_db_client().select(chunk_id)  # Blocking call
```

### Repository Pattern for Data Access
```python
# Use repositories to abstract database queries
class CodeRepository:
    async def find_by_semantic_similarity(
        self,
        query_vector: list[float],
        limit: int = 5
    ) -> list[CodeChunk]:
        # SurrealQL query logic encapsulated here
        pass

# Avoid raw queries in tools
@server.tool()
async def search_code(query: str):
    # Don't write SurrealQL directly in tool functions
    result = await db.query("SELECT * FROM code_chunk WHERE ...")
```

### Tool Design for MCP
```python
from pydantic import BaseModel, Field

class BlastRadiusRequest(BaseModel):
    file_path: str = Field(description="Relative path to the source file")
    max_depth: int = Field(default=2, ge=1, le=5, description="Graph traversal depth")

@server.tool()
async def analyze_blast_radius(request: BlastRadiusRequest) -> list[dict[str, Any]]:
    """
    Analyzes the dependency graph to identify components affected by changes to a file.

    This tool traverses the DEPENDS_ON relationships in SurrealDB to compute
    the transitive closure of dependencies up to the specified depth.

    Args:
        request (BlastRadiusRequest): Parameters for the analysis.

    Returns:
        list[dict[str, Any]]: Affected components with relationship metadata.

    Note:
        Results are cached for 5 minutes to reduce database load.
    """
    # Implementation
    pass
```

> **Key**: The docstring is read by the LLM at runtime. Be explicit about purpose, parameters, return values, and side effects.

---

## Testing Expectations

### Test Structure
```python
# tests/tools/test_search.py
import pytest
from unittest.mock import AsyncMock, patch

from src.presentation.mcp.routes import semantic_code_search

@pytest.mark.asyncio
async def test_semantic_search_returns_ranked_results():
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.semantic_search.return_value = [
        {"id": "chunk_1", "score": 0.92, "content": "..."}
    ]

    # Act
    results = await semantic_code_search("authentication logic", limit=3, _mock_repo=mock_repo)

    # Assert
    assert len(results) == 1
    assert results[0]["score"] > 0.9
```

### Guidelines
- Use `pytest-asyncio` for all async tests.
- Mock external dependencies (Ollama, SurrealDB) to ensure fast, deterministic tests.
- Test both success and error paths (e.g., `NodeNotFoundError`).
- Include integration tests for critical flows (ingestion, tool execution).

---

## Common Anti-Patterns to Avoid

| Pattern | Why Avoid | Preferred Alternative |
|---------|-----------|---------------------|
| Coupling logic to CLI/MCP | Violates Clean Architecture | Put logic in `core/services/` and inject interfaces |
| Hardcoding external tools | Violates Strategy/Factory patterns | Use `infrastructure/factory.py` to instantiate interfaces |
| Generic `Exception` raises | Obscures error handling logic | Define specific exceptions in `core/exceptions.py` |
| Direct SurrealQL in tools | Couples tools to database schema | Use repository methods with clear interfaces |
| Overly broad tool docstrings | Confuses LLM about tool purpose | Be concise, specific, and example-driven |

---

## Debugging and Diagnostics

### Enable Verbose Logging
```bash
# Set environment variable for development
export LOG_LEVEL=DEBUG
```
*Note: Since the server now uses SSE (Server-Sent Events) over HTTP, standard `stdout` printing and regular logging are completely safe and will not corrupt the MCP protocol.*

### Common Issues
| Symptom | Likely Cause | Diagnostic Step |
|---------|-------------|----------------|
| Tool not visible to AI | Missing `@server.tool()` decorator or docstring | Check `main.py` tool registration |
| Async timeout | Blocking call in coroutine | Review stack trace for `time.sleep`, `requests` |
| Embedding mismatch | Ollama model not loaded | Verify `ollama pull nomic-embed-text` |
| Graph query returns empty | Ingestion not completed | Run `python -m src.presentation.cli.cli_tool ingest` and check `view-graph` command |

### SurrealDB Inspection
```bash
# Connect to local instance
surreal sql --endpoint ws://localhost:8000 --ns nexus --db brain

# Useful queries
SELECT count() FROM code_chunk;              # Check ingestion status
SELECT ->DEPENDS_ON FROM code_chunk WHERE file_path = "auth/login.py";  # Inspect dependencies
```

---

## Environment and Dependencies

### Required Services
- **SurrealDB**: Running on `ws://localhost:8000` (default)
- **Ollama**: Running on `http://localhost:11434` with `nomic-embed-text` model pulled
- **Python 3.11+**: With virtual environment managed via `poetry` or `uv`

### Dependency Groups (`pyproject.toml`)
```toml
[tool.poetry.dependencies]
# Production dependencies
mcp = "^1.0.0"
surrealdb = "^0.5.0"
langchain-core = "^0.3.0"
pydantic = "^2.0.0"

[tool.poetry.group.dev.dependencies]
# Development dependencies
pytest = "^8.0.0"
pytest-asyncio = "^0.24.0"
ruff = "^0.4.0"
mypy = "^1.10.0"
```

> **Agent Note**: Never suggest adding production dependencies without explicit user approval. For dev-only tools, propose addition to `[group.dev]`.

---

## Contribution Workflow Reminder

1. **Check for existing Issue**: Ensure work aligns with an open ticket.
2. **Create feature branch**: Follow naming convention `feat/123-short-description`.
3. **Implement atomically**: One logical change per commit.
4. **Validate locally**: Run `ruff check .`, `mypy src/`, `pytest` before pushing.
5. **Update documentation**: Modify docstrings, `README.md`, or `STYLE_GUIDE.md` as needed.
6. **Submit PR**: Include clear description, test results, and reference the Issue.

---

## When to Ask for Clarification

Request human input when:
- Architectural decisions affect multiple modules (e.g., changing the data model).
- A proposed solution conflicts with the async-first or local-only principles.
- Tool behavior requires trade-offs between token usage and response completeness.
- Uncertainty exists about the intended scope of an Issue or feature request.

---

## Reference Documents

- [STYLE_GUIDE.md](STYLE_GUIDE.md): Coding standards, formatting, and type hinting rules.
- [CONTRIBUTING.md](CONTRIBUTING.md): Branching strategy, commit conventions, and PR process.
- [ARCHITECTURE.md](ARCHITECTURE.md): High-level system design and data flow diagrams.
- `pyproject.toml`: Authoritative dependency and tooling configuration.

---

*This document is maintained for AI agent reference. Human contributors should prioritize the official style and contribution guides for authoritative guidance.*
