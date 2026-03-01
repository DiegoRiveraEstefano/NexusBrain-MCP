"""
Contains all SurrealQL queries and schema definitions
to keep repositories clean and centralize DB logic.
"""

SCHEMA_DEFINITION_TEMPLATE = """
-- 1. Node Table: Code Chunks
DEFINE TABLE code_chunk SCHEMALESS;
DEFINE FIELD file_path ON code_chunk TYPE string;
DEFINE FIELD content ON code_chunk TYPE string;
DEFINE FIELD embedding ON code_chunk TYPE array<float>;

-- Vector Index (HNSW) for ultra-fast semantic searches (SurrealDB 3.x Syntax)
DEFINE INDEX idx_embedding ON code_chunk FIELDS embedding HNSW DIMENSION {embedding_dimensions} DIST COSINE TYPE F32;

-- 2. Node Table: Memory and Decisions
DEFINE TABLE decision_log SCHEMALESS;
DEFINE FIELD topic ON decision_log TYPE string;
DEFINE FIELD rationale ON decision_log TYPE string;
DEFINE FIELD created_at ON decision_log TYPE datetime DEFAULT time::now();

-- 3. Edges (Graph Relations)
DEFINE TABLE DEPENDS_ON TYPE RELATION FROM code_chunk TO code_chunk;
DEFINE TABLE MODIFIES TYPE RELATION FROM code_chunk TO code_chunk;
DEFINE TABLE RELATED_TO TYPE RELATION FROM decision_log TO code_chunk;
"""

# From src/db/repositories/graph_rag.py
SEARCH_SIMILAR_CODE_QUERY = """
SELECT
    id,
    file_path,
    content,
    vector::similarity::cosine(embedding, $query_vector) AS similarity_score
FROM code_chunk
ORDER BY similarity_score DESC
LIMIT $limit;
"""

ANALYZE_BLAST_RADIUS_QUERY_TEMPLATE = """
SELECT
    id,
    file_path,
    <-DEPENDS_ON<-code_chunk AS affected_by
FROM {node_id}
FETCH affected_by;
"""

GET_DEPENDENCIES_QUERY_TEMPLATE = """
SELECT
    ->DEPENDS_ON->code_chunk AS dependencies
FROM {node_id}
FETCH dependencies;
"""

# From src/db/repositories/memory.py
RECORD_DECISION_QUERY = """
CREATE decision_log SET
    topic = $topic,
    rationale = $rationale;
"""

RELATE_DECISION_TO_CODE_TEMPLATE = "RELATE {log_id}->RELATED_TO->{related_code_id};"

SEARCH_MEMORY_QUERY = """
SELECT *
FROM decision_log
WHERE topic CONTAINS $keyword
   OR rationale CONTAINS $keyword
ORDER BY created_at DESC;
"""

# Ingestion Script Queries
INGEST_CREATE_CODE_CHUNK_QUERY = """
CREATE code_chunk SET
    file_path = $file_path,
    content = $content,
    embedding = $embedding;
"""
INGEST_SELECT_ALL_CHUNKS_QUERY = "SELECT id, content, file_path FROM code_chunk;"
INGEST_RELATE_CHUNKS_TEMPLATE = "RELATE {source_id}->DEPENDS_ON->{target_id};"
