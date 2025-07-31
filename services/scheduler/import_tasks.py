"""
Tasks do Celery para importação automática de XML
"""

from celery import current_task
from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.celery_app import celery_app
from core.logger import logger
from core.database import get_db_session
from models.imovel import ImportacaoLog
import uuid


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def import_client_xml(self, cliente_config: Dict[str, Any]):
    """
    Task para importar XML de um cliente específico
    """
    cliente_id = cliente_config.get('cliente_id', 'unknown')
    
    try:
        logger.info(f"[TASK] Iniciando importação XML: {cliente_id}")
        
        # Importar módulos necessários
        from services.xml_importer.importer import XMLImporter
        
        # Criar importador
        importer = XMLImporter(
            cliente_config['cliente_id'],
            cliente_config['xml_url'], 
            cliente_config['xml_mapping']
        )
        
        # Executar importação
        resultado = importer.import_imoveis()
        
        # Log de sucesso
        logger.info(f"[TASK] Importação concluída: {cliente_id} - {resultado['status']}")
        
        # Atualizar progresso da task
        current_task.update_state(
            state='SUCCESS',
            meta={
                'cliente_id': cliente_id,
                'resultado': resultado,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return resultado
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[TASK] Erro na importação {cliente_id}: {error_msg}")
        
        # Retry automático
        if self.request.retries < self.max_retries:
            retry_in = self.default_retry_delay * (self.request.retries + 1)
            logger.info(f"[TASK] Tentativa {self.request.retries + 1}/{self.max_retries} em {retry_in}s")
            
            raise self.retry(countdown=retry_in, exc=e)
        
        # Falha final
        current_task.update_state(
            state='FAILURE',
            meta={
                'cliente_id': cliente_id,
                'erro': error_msg,
                'retries': self.request.retries,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'status': 'erro',
            'cliente_id': cliente_id,
            'erro': error_msg,
            'retries': self.request.retries
        }


@celery_app.task(bind=True)
def import_all_clients_daily(self):
    """
    Task principal para importar todos os clientes ativos diariamente
    """
    try:
        logger.info("[SCHEDULER] Iniciando importação diária de todos os clientes")
        
        # Buscar configurações de clientes ativos
        clientes_configs = get_active_clients_configs()
        
        if not clientes_configs:
            logger.warning("[SCHEDULER] Nenhum cliente ativo encontrado")
            return {
                'status': 'aviso',
                'message': 'Nenhum cliente ativo encontrado',
                'timestamp': datetime.now().isoformat()
            }
        
        # Agendar importação para cada cliente
        task_results = []
        for config in clientes_configs:
            try:
                # Agendar task assíncrona
                task = import_client_xml.delay(config)
                
                task_results.append({
                    'cliente_id': config['cliente_id'],
                    'task_id': task.id,
                    'status': 'agendado',
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"[SCHEDULER] Task agendada: {config['cliente_id']} -> {task.id}")
                
            except Exception as e:
                logger.error(f"[SCHEDULER] Erro ao agendar {config['cliente_id']}: {e}")
                task_results.append({
                    'cliente_id': config['cliente_id'],
                    'status': 'erro_agendamento',
                    'erro': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Salvar log da execução do scheduler
        save_scheduler_log(task_results)
        
        resultado = {
            'status': 'sucesso',
            'total_clientes': len(clientes_configs),
            'tasks_agendadas': len([t for t in task_results if t['status'] == 'agendado']),
            'erros': len([t for t in task_results if t['status'] == 'erro_agendamento']),
            'tasks': task_results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"[SCHEDULER] Importação diária concluída: {resultado['tasks_agendadas']} tasks agendadas")
        return resultado
        
    except Exception as e:
        logger.error(f"[SCHEDULER] Erro crítico na importação diária: {e}")
        return {
            'status': 'erro_critico',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }


def get_active_clients_configs() -> List[Dict[str, Any]]:
    """
    Buscar configurações de todos os clientes ativos
    """
    try:
        # Por enquanto, usar configurações hardcoded
        # Em produção, buscar do banco de dados
        from config.examples.cliente_teste_local import TesteLocalXML
        
        configs = []
        
        # Cliente de teste
        teste_config = TesteLocalXML().get_config()
        if teste_config['ativo']:
            configs.append(teste_config)
        
        # TODO: Adicionar busca no banco de dados
        # with get_db_session() as db:
        #     clientes = db.query(ClienteConfig).filter(
        #         ClienteConfig.ativo == True
        #     ).all()
        #     for cliente in clientes:
        #         configs.append(cliente.get_config())
        
        logger.info(f"[CONFIG] Encontrados {len(configs)} clientes ativos")
        return configs
        
    except Exception as e:
        logger.error(f"[CONFIG] Erro ao buscar configurações: {e}")
        return []


def save_scheduler_log(task_results: List[Dict[str, Any]]):
    """
    Salvar log da execução do scheduler
    """
    try:
        # TODO: Implementar modelo de log do scheduler
        # Por enquanto, apenas log em arquivo
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'scheduler_execution',
            'results': task_results
        }
        
        logger.info(f"[SCHEDULER_LOG] {log_data}")
        
    except Exception as e:
        logger.error(f"[SCHEDULER_LOG] Erro ao salvar log: {e}")


@celery_app.task
def import_client_manual(cliente_id: str):
    """
    Task para importação manual de um cliente específico
    """
    try:
        logger.info(f"[MANUAL] Importação manual solicitada: {cliente_id}")
        
        # Buscar configuração do cliente
        configs = get_active_clients_configs()
        client_config = None
        
        for config in configs:
            if config['cliente_id'] == cliente_id:
                client_config = config
                break
        
        if not client_config:
            raise ValueError(f"Cliente {cliente_id} não encontrado ou inativo")
        
        # Executar importação
        task = import_client_xml.delay(client_config)
        
        return {
            'status': 'agendado',
            'cliente_id': cliente_id,
            'task_id': task.id,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[MANUAL] Erro na importação manual {cliente_id}: {e}")
        return {
            'status': 'erro',
            'cliente_id': cliente_id,
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }
