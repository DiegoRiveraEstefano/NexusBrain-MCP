"""
Centralizes tool response formats and error messages
to facilitate maintenance and consistency.
"""
from langchain_text_splitters import Language

# General
APP_NAME = "NexusBrain"
UNKNOWN_ID = "Unknown ID"
UNKNOWN_PATH = "Unknown path"
NO_TITLE = "No title"
NO_RATIONALE = "No rationale"
UNKNOWN_DATE = "Unknown date"

# Tool Generic Error Messages
TOOL_ERROR_TEMPLATE = "Internal error in tool '{tool_name}': {error}"

# record_decision tool
RECORD_DECISION_SUCCESS_TEMPLATE = "✅ **Decision successfully saved** to project memory (ID: `{record_id}`)."
RECORD_DECISION_TOPIC_TEMPLATE = "Topic: *{topic}*"
RECORD_DECISION_LINK_SUCCESS_TEMPLATE = "🔗 Successfully linked to code: `{related_code_id}`."
RECORD_DECISION_FAILURE = "Could not record decision in memory."

# search_memory tool
SEARCH_MEMORY_NO_RESULTS_TEMPLATE = "No previous decisions found in memory related to: '{keyword}'."
SEARCH_MEMORY_HEADER_TEMPLATE = "### 🧠 Project Memory for: '{keyword}'\n\nFound the following technical decisions in history:\n\n"
SEARCH_MEMORY_RESULT_ITEM_TEMPLATE = "**{index}. {topic}** *(Recorded: {created_at})*\n> {rationale}\n\n"

# analyze_blast_radius tool
BLAST_RADIUS_NO_DEPENDENTS_TEMPLATE = "Node `{node_id}` has no registered dependents. It is safe to modify."
BLAST_RADIUS_HEADER_TEMPLATE = "### 💥 Blast Radius Analysis for: `{node_id}`\n\nThe following components depend directly or indirectly on this code:\n\n"
BLAST_RADIUS_NO_AFFECTED_NODES_TEMPLATE = "Node `{node_id}` exists, but has no components depending on it."
BLAST_RADIUS_RESULT_ITEM_TEMPLATE = "{index}. 📄 **File:** `{file_path}` (ID: `{node_id}`)\n"
BLAST_RADIUS_FOOTER = "\n⚠️ *Consider reviewing these files if making structural changes.*"

# get_execution_flow tool
EXEC_FLOW_NO_DEPENDENCIES_TEMPLATE = "Node `{node_id}` has no registered outgoing dependencies (it is a leaf/pure function)."
EXEC_FLOW_HEADER_TEMPLATE = "### 🔄 Execution Flow and Dependencies of: `{node_id}`\n\nThis component imports or calls the following elements:\n\n"
EXEC_FLOW_NO_OUTGOING_TEMPLATE = "No outgoing dependencies found for `{node_id}`."
EXEC_FLOW_RESULT_ITEM_TEMPLATE = "- ➡️ Calls: `{file_path}` (ID: `{dep_id}`)\n"

# semantic_code_search tool
SEMANTIC_SEARCH_NO_RESULTS = "No relevant code chunks found for this query."
SEMANTIC_SEARCH_HEADER_TEMPLATE = "### Semantic Search Results for: '{query}'\n\n"
SEMANTIC_SEARCH_RESULT_ITEM_TEMPLATE = "**Result {index}** (File: `{file_path}`) | Similarity: {score:.3f}\n"
SEMANTIC_SEARCH_CODE_BLOCK_TEMPLATE = "```\n{content}\n```\n\n"

# Ingestion Script
INGEST_SUPPORTED_EXTENSIONS = {
    ".py": Language.PYTHON,
    ".ts": Language.TS,
    ".js": Language.JS,
    ".md": Language.MARKDOWN,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".c": Language.C,
    ".ex": Language.ELIXIR,
    ".sql": Language.SOL,
    ".html": Language.HTML,
    ".kt": Language.KOTLIN,
    ".h": Language.CPP,
}

# Ingestion Script UI Messages
INGEST_ERROR_PATH_NOT_FOUND_TEMPLATE = "[red]Error: Path '{path}' does not exist or is not a directory.[/red]"
INGEST_START_TEMPLATE = "\n[bold blue] Starting ingestion in:[/bold blue] {path}"
INGEST_FILES_FOUND_TEMPLATE = "Found [green]{count}[/green] supported files.\n"
INGEST_STEP_1_READING = "[yellow]1/3 Reading and chunking code..."
INGEST_STEP_1_DONE = "[green]1/3 Chunking completed![/green]"
INGEST_STEP_2_INSERTING_TEMPLATE = "[yellow]2/3 Generating Embeddings and inserting {count} nodes..."
INGEST_STEP_2_DONE_TEMPLATE = "[green]2/3 Inserted {count} vector nodes![/green]"
INGEST_STEP_3_GRAPH = "[yellow]3/3 Building Dependency Graph (GraphRAG)..."
INGEST_STEP_3_DONE_TEMPLATE = "[green]3/3 Created {count} relations (Edges)![/green]"
INGEST_COMPLETE = "\n[bold green]✅ Ingestion completed successfully. The Central Brain is ready.[/bold green]\n"
