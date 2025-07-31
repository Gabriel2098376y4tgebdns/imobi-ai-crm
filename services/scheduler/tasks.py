"""
Tasks de manutenção e monitoramento do sistema
"""

from celery import current_task
from datetime import datetime, timedelta
from typing import Dict, List
from core.celery_app import celery_app
from core.logger import logger
from core.database import get_db_session


@celery_app.task
def cleanup_old_logs():
    """
    Limpeza de logs antigos (> 30 dias)
    """
    try:
        logger.info("[CLEANUP] Iniciando limpeza de logs antigos")
        
        # Data limite (30 dias atrás)
        data_limite = datetime.now() - timedelta(days=30)
        
        with get_db_session() as db:
            from models.imovel import ImportacaoLog
            
            # Contar logs antigos
            logs_antigos = db.query(ImportacaoLog).filter(
                ImportacaoLog.data_importacao < data_limite
            ).count()
            
            if logs_antigos > 0:
                # Remover logs antigos
                db.query(ImportacaoLog).filter(
                    ImportacaoLog.data_importacao < data_limite
                ).delete()
                
                logger.info(f"[CLEANUP] Removidos {logs_antigos} logs antigos")
            else:
                logger.info("[CLEANUP] Nenhum log antigo encontrado")
            
            return {
                'status': 'sucesso',
                'logs_removidos': logs_antigos,
                'data_limite': data_limite.isoformat(),
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"[CLEANUP] Erro na limpeza: {e}")
        return {
            'status': 'erro',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task
def health_check_clients():
    """
    Verificar saúde dos XMLs dos clientes
    """
    try:
        logger.info("[HEALTH] Iniciando health check dos clientes")
        
        from services.scheduler.import_tasks import get_active_clients_configs
        from services.xml_importer.parser import XMLParser
        
        clientes_configs = get_active_clients_configs()
        resultados = []
        
        for config in clientes_configs:
            try:
                cliente_id = config['cliente_id']
                xml_url = config['xml_url']
                
                # Testar acesso ao XML
                parser = XMLParser(config['xml_mapping'])
                xml_content = parser.fetch_xml(xml_url, timeout=10)
                
                # Parse básico para verificar estrutura
                imoveis = parser.parse_xml(xml_content)
                
                resultados.append({
                    'cliente_id': cliente_id,
                    'status': 'ok',
                    'xml_size': len(xml_content),
                    'imoveis_encontrados': len(imoveis),
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"[HEALTH] {cliente_id}: OK - {len(imoveis)} imóveis")
                
            except Exception as e:
                resultados.append({
                    'cliente_id': config.get('cliente_id', 'unknown'),
                    'status': 'erro',
                    'erro': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.error(f"[HEALTH] {config.get('cliente_id', 'unknown')}: ERRO - {e}")
        
        # Resumo
        total = len(resultados)
        ok = len([r for r in resultados if r['status'] == 'ok'])
        erros = total - ok
        
        resultado_final = {
            'status': 'sucesso',
            'total_clientes': total,
            'clientes_ok': ok,
            'clientes_erro': erros,
            'detalhes': resultados,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"[HEALTH] Health check concluído: {ok}/{total} clientes OK")
        return resultado_final
        
    except Exception as e:
        logger.error(f"[HEALTH] Erro no health check: {e}")
        return {
            'status': 'erro_critico',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task
def generate_daily_report():
    """
    Gerar relatório diário de importações
    """
    try:
        logger.info("[REPORT] Gerando relatório diário")
        
        # Data de hoje
        hoje = datetime.now().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        fim_dia = datetime.combine(hoje, datetime.max.time())
        
        with get_db_session() as db:
            from models.imovel import ImportacaoLog, Imovel
            from sqlalchemy import func
            
            # Buscar logs de importação do dia
            logs_hoje = db.query(ImportacaoLog).filter(
                ImportacaoLog.data_importacao >= inicio_dia,
                ImportacaoLog.data_importacao <= fim_dia
            ).all()
            
            # Estatísticas de imóveis por cliente
            stats_imoveis = db.query(
                Imovel.cliente_id,
                func.count(Imovel.id).label('total'),
                func.count(Imovel.id).filter(Imovel.status == 'ativo').label('ativos')
            ).group_by(Imovel.cliente_id).all()
            
            # Compilar relatório
            relatorio = {
                'data': hoje.isoformat(),
                'importacoes_hoje': len(logs_hoje),
                'importacoes_sucesso': len([l for l in logs_hoje if l.status == 'sucesso']),
                'importacoes_erro': len([l for l in logs_hoje if l.status == 'erro']),
                'clientes_stats': [
                    {
                        'cliente_id': stat.cliente_id,
                        'total_imoveis': stat.total,
                        'imoveis_ativos': stat.ativos
                    }
                    for stat in stats_imoveis
                ],
                'detalhes_importacoes': [
                    {
                        'cliente_id': log.cliente_id,
                        'status': log.status,
                        'total_imoveis': log.total_imoveis,
                        'novos': log.imoveis_novos,
                        'atualizados': log.imoveis_atualizados,
                        'removidos': log.imoveis_removidos,
                        'tempo_execucao': log.tempo_execucao,
                        'timestamp': log.data_importacao.isoformat()
                    }
                    for log in logs_hoje
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"[REPORT] Relatório gerado: {len(logs_hoje)} importações hoje")
            return relatorio
            
    except Exception as e:
        logger.error(f"[REPORT] Erro ao gerar relatório: {e}")
        return {
            'status': 'erro',
            'erro': str(e),
            'timestamp': datetime.now().isoformat()
        }
