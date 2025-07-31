#!/bin/bash
echo "🚀 Iniciando Celery Worker..."
source .venv/bin/activate
celery -A core.celery_app worker --loglevel=info --concurrency=4 --queues=default,imports
