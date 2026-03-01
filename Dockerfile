# ==========================================
# ETAPA 1: BUILDER (Compilación y Dependencias con UV)
# ==========================================
FROM python:3.13-slim AS builder

# 1. Traemos el binario de 'uv' directamente desde su imagen oficial (ultrarrápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Dependencias del sistema (build-essential sigue siendo útil para compilar tree-sitter si no hay wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear el entorno virtual con uv
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
# Aseguramos que los comandos de uv usen este venv por defecto
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /build

# 4. Instalar PyTorch CPU-only. uv pip es entre 10x y 100x más rápido que pip tradicional
RUN uv pip install --no-cache torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. Copiar archivos de configuración y código fuente
COPY pyproject.toml README.md ./
COPY src/ ./src/

# 6. Instalar el proyecto y sus dependencias
RUN uv pip install --no-cache .


# ==========================================
# ETAPA 2: FINAL (Entorno de Ejecución Ligero)
# ==========================================
FROM python:3.13-slim AS final

# 1. Variables de entorno base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HF_HOME="/app/data/hf_cache"

WORKDIR /app

# 2. Copiamos el entorno virtual compilado desde el builder
COPY --from=builder /opt/venv /opt/venv

# 3. Crear carpetas para la base de datos embebida y modelos, ajustando permisos
RUN mkdir -p /app/data/hf_cache /app/data/database /var/log && chmod -R 777 /app/data

# 4. Copiar únicamente el código fuente y scripts necesarios (sin bash scripts extra)
COPY src/ ./src/
COPY scripts/ ./scripts/

# 5. Variables de entorno de la aplicación.
# NOTA: En modo embebido, usamos file:// con ruta absoluta. User y Pass ya no son estrictamente necesarios.
ENV ENVIRONMENT="production" \
    LOG_LEVEL="INFO" \
    SURREAL_URL="file:///app/data/database" \
    SURREAL_NS="nexusbrain" \
    SURREAL_DB="graphrag" \
    EMBEDDING_SERVICE="huggingface" \
    EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# 6. Definir el punto de entrada.
# Como definiste [project.scripts] en tu pyproject.toml, puedes llamar al binario directamente.
CMD ["nexusbrain-mcp"]
