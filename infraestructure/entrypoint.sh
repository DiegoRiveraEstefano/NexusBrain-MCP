#!/bin/bash
# Evita que el script continúe si hay un error crítico
set -e

echo "🟢 1. Arrancando SurrealDB en segundo plano..."
# Encendemos SurrealDB apuntando a la carpeta /app/data para que sea persistente.
# El símbolo '&' al final es crucial: lanza el proceso en background para no bloquear el script.
surreal start \
    --log ${LOG_LEVEL:-info} \
    --user ${SURREAL_USER:-root} \
    --pass ${SURREAL_PASS:-root} \
    --bind 0.0.0.0:8000 \
    rocksdb:/app/data/mydatabase.db &

echo "⏳ 2. Esperando a que SurrealDB levante el socket WS..."
# Le damos 3 segundos a la base de datos para que esté lista para recibir conexiones
sleep 3

echo "🚀 3. Iniciando NexusBrain MCP..."
# 'exec "$@"' toma cualquier comando que le pases al contenedor (ya sea el CMD por defecto
# o un comando de la CLI) y lo ejecuta en el proceso principal.
exec "$@"
