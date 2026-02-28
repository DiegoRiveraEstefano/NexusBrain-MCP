# NexusBrain MCP

**The Local "Central Brain" for Your AI. GraphRAG-Based Codebase Navigation and Persistent Memory Using SurrealDB and the Model Context Protocol (MCP).**

NexusBrain is an MCP server written in Python that empowers AI assistants (such as Claude Desktop or Cursor) with a deep understanding of your software architecture. Instead of flooding the context window with thousands of lines of code, NexusBrain combines **Vector Search (Semantic)** and **Knowledge Graphs (Dependencies)** to enable surgical code navigation and maintain a historical record of technical decisions.

---

## Key Features

* **Native GraphRAG:** Goes beyond finding similar code (Vectors) to understanding how components interconnect (Graphs).
* **100% Local and Private:** Your data and code never leave your machine. Local models via Ollama or HuggingFace are used for embedding generation.
* **Infinite Memory:** Eliminate the need to re-explain your project architecture in every new chat. NexusBrain maintains a persistent decision log.
* **Token Optimization:** By providing the AI with tools to navigate the dependency graph, token consumption is significantly reduced, and hallucinations are minimized.
* **Multi-Model Database:** Powered by **SurrealDB**, handling documents, graphs, and vectors in a single platform without complex migrations.

---

## System Architecture

NexusBrain is built following **Clean Architecture** principles and operates in two primary phases:

1.  **Ingestion Phase (CLI Tool):** A sophisticated pipeline using `Tree-sitter` (AST parsing) or universal Regex fallbacks reads source code, splits it into logical chunks, generates local embeddings, and maps relationships (`IMPORTS`, `CALLS`) within SurrealDB.
2.  **Interaction Phase (MCP Server):** The server exposes tools to the AI via **HTTP/SSE**. When context is required, the AI queries NexusBrain, which leverages its Services and Repositories to return precise code fragments and impact analysis.

---

## Technology Stack

* **Language:** Python 3.13+
* **Protocol:** Model Context Protocol (`mcp[cli]`) via SSE transport
* **AI Orchestration:** LangChain (HuggingFace / Ollama)
* **Code Parsing:** Tree-sitter
* **Database:** SurrealDB (Vector + Graph)
* **CLI Engine:** Rich & Click
* **Architecture:** Clean Architecture (Ports & Adapters)

---

## Available MCP Tools

Once connected, your AI assistant will have access to the following cognitive capabilities:

### Memory and Context
* `record_decision`: Stores architectural decisions, complex bug resolutions, or business rules with associated tags.
* `search_memory`: Searches the project's historical record to recall context from past decisions.

### Code Navigation (GraphRAG)
* `semantic_code_search`: Searches for code fragments by concept or meaning (e.g., "password reset logic"), rather than exact keyword matching.
* `analyze_blast_radius`: Given a file or function, traverses the graph to identify which other components would be affected by a change.
* `get_execution_flow`: Displays the call tree for a specific function to clarify its internal dependencies.

---

## Installation and Quickstart

### 1. Prerequisites
* [Docker](https://docs.docker.com/get-docker/) and Docker Compose
* [Ollama](https://ollama.com/) installed locally (if using local embedding models)

### 2. Start the Infrastructure
Clone the repository and launch SurrealDB alongside the MCP server:

```bash
git clone https://github.com/your-username/nexusbrain-mcp.git
cd nexusbrain-mcp
docker-compose up -d
```

### 3. Configure Your AI Client
Add NexusBrain as an MCP server in your AI client configuration using SSE.

**For Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "nexusbrain": {
      "command": "nexusbrain-mcp",
      "env": {
        "SURREAL_URL": "ws://localhost:8000/rpc",
        "EMBEDDING_SERVICE": "huggingface"
      }
    }
  }
}
```

**For Cursor or other MCP-compatible editors:**
Refer to the editor's documentation for adding a custom MCP server. The server exposes an SSE endpoint on port 8080.

### 4. Initialize Your Codebase
Run the ingestion CLI tool to index your project:

```bash
# Activate your virtual environment first
nexusbrain-cli ingest ./your-project-source
```

To view the generated graph:
```bash
nexusbrain-cli view-graph
```

To simulate AI reasoning:
```bash
nexusbrain-cli simulate
```

---

## Usage Example

Once configured, you can interact with your AI assistant using natural language:

> **User:** "I need to modify the authentication flow. What files would be impacted?"
>
> **AI (using NexusBrain):** *Calls `analyze_blast_radius` with `auth/login.py`*
>
> **NexusBrain Response:** Returns a list of dependent modules: `auth/session.py`, `api/middleware.py`, `utils/token_validator.py`.
>
> **AI:** "Modifying the authentication flow will affect the following components: [list]. Would you like me to review any of these files?"

---

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Type Checking and Linting
```bash
mypy src/
ruff check src/ tests/
ruff format src/ tests/
```

### Building the Docker Image
```bash
docker build -t nexusbrain-mcp .
```

---

## Contributing

Contributions are welcome! Please refer to the [Contribution Guide](CONTRIBUTING.md) and [Style Guide](STYLE_GUIDE.md) before submitting pull requests.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*NexusBrain MCP is designed to augment, not replace, developer judgment. Always review AI-suggested changes in the context of your specific architecture.*
