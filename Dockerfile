# Usamos Python 3.13 slim como base
FROM python:3.13-slim

# Evita que Python escriba archivos .pyc y asegura que la salida no use buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# NUEVO: Directorio donde Hugging Face guardará los modelos descargados.
# Al estar dentro de /app/data, el modelo se guardará en tu volumen de Docker
# y no se tendrá que volver a descargar si apagas el contenedor.
ENV HF_HOME="/app/data/hf_cache"

# 1. Instalar dependencias del sistema requeridas para instalar SurrealDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar el binario de SurrealDB
RUN curl -sSf https://install.surrealdb.com | sh

# 3. Configurar el directorio de trabajo
WORKDIR /app

# 4. Crear carpetas para la DB y la caché de Hugging Face, ajustando permisos
RUN mkdir -p /app/data/hf_cache /var/log && chmod -R 777 /app/data

# 5. Copiar los archivos del proyecto
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# 6. NUEVO: Instalar PyTorch en su versión CPU-only ANTES de tu aplicación.
# Esto es vital para mantener la imagen de Docker ligera (ahorra ~2GB).
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 7. Instalar la aplicación Python (NexusBrain) y sus dependencias
RUN pip install --no-cache-dir .


# 8. Copiar y dar permisos al entrypoint (Enrutador MCP / Ingesta)
COPY infraestructure/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 9. Variables de entorno por defecto
ENV ENVIRONMENT="production"
ENV LOG_LEVEL="INFO"
ENV SURREAL_URL="file://data/database"
ENV SURREAL_USER="root"
ENV SURREAL_PASS="root"
ENV SURREAL_NS="nexusbrain"
ENV SURREAL_DB="graphrag"


ENV EMBEDDING_SERVICE="huggingface"
ENV EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# 10. Definir el punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
#CMD ["python", "src/main.py"]
