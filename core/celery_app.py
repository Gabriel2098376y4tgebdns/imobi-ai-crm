"""
Configuração do Celery para tasks assíncronas
"""

from celery import Celery
from celery.schedules import crontab
from core.config import get_settings
from core.logger import logger

settings = get_settings()

# Configurar Celery
celery_app = Celery(
    "imobi_ai_crm",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        'services.scheduler.tasks',
        'services.scheduler.import_tasks'
    ]
)

# Configurações do Celery
celery_app.conf.update(
    # Timezone
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # Serialização
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Configurações de retry
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configurações de resultado
    result_expires=3600,  # 1 hora
    
    # Configurações de roteamento
    task_routes={
        'services.scheduler.tasks.*': {'queue': 'default'},
        'services.scheduler.import_tasks.*': {'queue': 'imports'},
    },
    
    # Beat schedule (tarefas periódicas)
    beat_schedule={
        # Importação diária às 8h da manhã
        'importacao-diaria-8h': {
            'task': 'services.scheduler.import_tasks.import_all_clients_daily',
            'schedule': crontab(hour=8, minute=0),  # 8:00 AM todos os dias
            'options': {'queue': 'imports'}
        },
        
        # Limpeza de logs antigos (semanal)
        'limpeza-logs-semanal': {
            'task': 'services.scheduler.tasks.cleanup_old_logs',
            'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Segunda-feira 2:00 AM
            'options': {'queue': 'default'}
        },
        
        # Health check dos clientes (a cada 6 horas)
        'health-check-clientes': {
            'task': 'services.scheduler.tasks.health_check_clients',
            'schedule': crontab(minute=0, hour='*/6'),  # A cada 6 horas
            'options': {'queue': 'default'}
        }
    }
)

# Configurar logging para Celery
@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')

logger.info("Celery configurado com sucesso")
