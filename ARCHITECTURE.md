# System Architecture (NexusBrain MCP)

This document describes the high-level architecture, core modules, data flow, and design decisions behind NexusBrain MCP.

---

## 1. System Overview

NexusBrain operates as a local "Central Brain" (middleware) between an AI assistant (such as Claude Desktop or Cursor) and your local code repository. It leverages the **Model Context Protocol (MCP)** standard to expose cognitive tools based on a **GraphRAG** (Retrieval-Augmented Generation with Graphs) architecture.

The system is organized into three primary logical layers following a **Clean Architecture / Hexagonal Architecture** approach:
1. **Presentation Layer (MCP & CLI):** Handles HTTP/SSE communication with the AI client and interactive CLI commands using `Rich`/`Click`.
2. **Core Layer (Domain & Services):** Contains pure business logic, interfaces (Ports), and orchestration logic (Ingestion, Search, Memory).
3. **Infrastructure Layer (Adapters):** Concrete implementations for database (SurrealDB), LLM integrations (LangChain/Ollama), and AST Parsing (TreeSitter/Regex Fallbacks).

---

## 2. Package Structure (`src/`)

The application follows a strictly decoupled, modular architecture:

### `core/` (Domain Logic & Interfaces)
The heart of the application. It has zero dependencies on external frameworks like FastMCP or CLI tools.
* **`interfaces/`**: Abstract Base Classes (Contracts/Ports) like `IGraphRepository`, `IEmbeddingProvider`, `IParser`.
* **`services/`**: Application Use Cases orchestrating logic (`IngestionService`, `SearchService`, `MemoryService`).
* **`settings.py`**: Environment variable management (using Pydantic Settings).

### `infrastructure/` (Adapters & External Integrations)
Implements the interfaces defined in the Core.
* **`db/`**: Handles exclusive communication with SurrealDB (`SurrealGraphRepository`, `SurrealMemoryRepository`).
* **`llm/`**: Encapsulates interactions with local models via LangChain, implementing Strategy/Factory patterns (`OllamaProvider`, `HuggingFaceProvider`).
* **`ast/`**: Parsing logic (`TreeSitterPythonParser` and a `UniversalFallbackParser` using Regex for polyglot support).

### `presentation/` (Entrypoints)
How external actors interact with the application.
* **`mcp/`**: Exposes the FastMCP server over HTTP/SSE (`server.py`, `routes.py`).
* **`cli/`**: Interactive command-line interface (`cli_tool.py`) for ingestion, visualization, and flow simulation.

---

## 3. Primary Data Flows

### Flow A: Code Ingestion (CLI Process)
This process runs before the AI can answer questions and is executed via the `nexusbrain-cli ingest` command.

1. **Scan:** `IngestionService` locates relevant project files.
2. **Process:** `ParserFactory` determines whether to use AST (Tree-Sitter) or a Regex fallback to extract relationships and split logical chunks.
3. **Vectorize:** Chunks are sent to the `EmbeddingFactory` (Ollama/HuggingFace) to generate dense semantic vectors.
4. **Persist:** The `SurrealGraphRepository` stores chunks as **Nodes** (`code_chunk`) and maps *imports* to create **Edges** (`DEPENDS_ON`).

### Flow B: MCP Tool Execution (AI Interaction via SSE)
When a user asks a question via the client (e.g., Claude Desktop):

1. **Request:** The AI client decides to call the `analyze_blast_radius` tool over the HTTP/SSE connection.
2. **Routing:** `presentation/mcp/routes.py` receives the request and instantiates the `SearchService`.
3. **Execution:** The `SearchService` uses the `SurrealGraphRepository` to execute a SurrealQL graph traversal query (`<-DEPENDS_ON<-`).
4. **Response:** The result is formatted as compact Markdown and returned to the AI.

---

## 4. Data Model (SurrealDB)

This project leverages SurrealDB's multi-model capabilities. Instead of classic relational tables, it uses a graph and vector-oriented schema.

* **Nodes (Primary Tables/Classes):**
  * `code_chunk`: Stores code content, file path, and its embedding vector.
  * `decision_log`: Stores architectural annotations made by the AI or the user.
* **Edges (Relationships):**
  * `DEPENDS_ON`: Relates a `code_chunk` to another (e.g., Function A calls Function B).
  * `MODIFIES`: Relates a `code_chunk` to a database schema or global state.
  * `RELATED_TO`: Relates a `decision_log` to a specific `code_chunk`.

---

## 5. Key Dependencies

The following libraries form the foundation of the architecture, as defined in `pyproject.toml` (or equivalent):

* **[mcp](https://github.com/modelcontextprotocol/python-sdk):** Official Anthropic SDK for building context servers.
* **[surrealdb](https://github.com/surrealdb/surrealdb.py):** Official async SDK for interacting with the multi-model database.
* **[langchain-core](https://python.langchain.com/) & [langchain-ollama](https://python.langchain.com/docs/integrations/providers/ollama/):** For prompt orchestration, text splitting, and communication with local embedding models.
* **[pydantic](https://docs.pydantic.dev/):** Strict validation of input data for MCP tools and model serialization.
* **[pytest](https://docs.pytest.org/) & [pytest-asyncio](https://pytest-asyncio.readthedocs.io/):** Primary framework for unit and integration testing.
