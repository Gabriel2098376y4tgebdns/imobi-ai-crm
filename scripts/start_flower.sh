#!/bin/bash
echo "🌸 Iniciando Flower (Monitoramento)..."
source .venv/bin/activate
celery -A core.celery_app flower --port=5555 --basic_auth=admin:imobi2025
