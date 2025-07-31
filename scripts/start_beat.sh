#!/bin/bash
echo "⏰ Iniciando Celery Beat (Scheduler)..."
source .venv/bin/activate
celery -A core.celery_app beat --loglevel=info
