"""
Serviço de Agendamentos CRM
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
from core.logger import logger
from core.database import get_db_session
from models.agendamento import Agendamento
from models.lead import Lead
from models.imovel import Imovel


class AgendamentoService:
    """Serviço completo de agendamentos"""
    
    def __init__(self):
        pass
    
    def create_agendamento(self, agendamento_data: Dict) -> Dict[str, Any]:
        """Criar novo agendamento"""
        
        try:
            with get_db_session() as db:
                agendamento_id = str(uuid.uuid4())
                
                # Criar agendamento
                new_agendamento = Agendamento(
                    id=agendamento_id,
                    cliente_id=agendamento_data.get('cliente_id'),
                    lead_id=agendamento_data.get('lead_id'),
                    nome_cliente=agendamento_data.get('nome_cliente'),
                    telefone_cliente=agendamento_data.get('telefone_cliente'),
                    imovel_id=agendamento_data.get('imovel_id'),
                    codigo_imovel=agendamento_data.get('codigo_imovel'),
                    endereco_imovel=agendamento_data.get('endereco_imovel'),
                    data_visita=datetime.fromisoformat(agendamento_data.get('data_visita')),
                    observacoes=agendamento_data.get('observacoes', ''),
                    status='agendado'
                )
                
                db.add(new_agendamento)
                db.commit()
                
                logger.info(f"Agendamento criado: {agendamento_id}")
                return {
                    'status': 'success',
                    'agendamento_id': agendamento_id,
                    'message': 'Agendamento criado com sucesso'
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {e}")
            return {'status': 'error', 'message': str(e)}


# Instância global
agendamento_service = AgendamentoService()
