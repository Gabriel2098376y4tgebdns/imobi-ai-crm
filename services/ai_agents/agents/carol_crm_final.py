"""
Agent Carol - CRM e Follow-up (Versão Final)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from core.logger import logger


class CarolCRMAgent:
    """
    Carol - Gestão de CRM e relacionamento
    Registra interações e planeja follow-ups
    """
    
    def __init__(self):
        pass
    
    def create_interaction_record(self, lead_data: Dict, conversation_summary: str, outcome: str) -> Dict:
        """Criar registro de interação"""
        
        return {
            'lead_id': lead_data.get('id'),
            'cliente_id': lead_data.get('cliente_id'),
            'nome_cliente': lead_data.get('nome'),
            'telefone': lead_data.get('telefone'),
            'data_interacao': datetime.now().isoformat(),
            'tipo_interacao': 'whatsapp_carol',
            'resumo_conversa': conversation_summary,
            'resultado': outcome,
            'proximo_followup': self._calculate_next_followup(outcome),
            'status_lead': self._determine_lead_status(outcome),
            'agent_responsavel': 'Carol',
            'observacoes': f"Conversa conduzida pela Corretora Carol"
        }
    
    def create_followup_message(self, days_since_contact: int, last_interaction: str) -> str:
        """Criar mensagem de follow-up"""
        
        if days_since_contact <= 3:
            return "Olá, como está? Gostaria de saber se ainda tem interesse nos imóveis que apresentei."
        elif days_since_contact <= 7:
            return "Boa tarde. Retomando nosso contato sobre os imóveis. Posso ajudar com alguma informação adicional?"
        else:
            return "Olá, tudo bem? Temos novos imóveis que podem te interessar. Gostaria de conhecer as opções?"
    
    def analyze_conversation_outcome(self, messages: List[str]) -> Dict:
        """Analisar resultado da conversa"""
        
        last_messages = ' '.join(messages[-3:]).lower()
        
        if any(word in last_messages for word in ['agendou', 'visita', 'confirmado']):
            return {
                'status': 'agendou_visita',
                'resumo': 'Cliente agendou visita',
                'nivel_interesse': 5,
                'proxima_acao': 'confirmar_visita'
            }
        elif any(word in last_messages for word in ['interesse', 'gostei', 'quero']):
            return {
                'status': 'interessado',
                'resumo': 'Cliente demonstrou interesse',
                'nivel_interesse': 4,
                'proxima_acao': 'acompanhar_decisao'
            }
        elif any(word in last_messages for word in ['pensar', 'depois', 'mais tarde']):
            return {
                'status': 'precisa_pensar',
                'resumo': 'Cliente precisa pensar',
                'nivel_interesse': 3,
                'proxima_acao': 'followup_em_7_dias'
            }
        else:
            return {
                'status': 'sem_interesse',
                'resumo': 'Cliente sem interesse aparente',
                'nivel_interesse': 1,
                'proxima_acao': 'followup_em_30_dias'
            }
    
    def _calculate_next_followup(self, outcome: str) -> str:
        """Calcular próximo follow-up"""
        
        followup_days = {
            'agendou_visita': 1,
            'interessado': 3,
            'precisa_pensar': 7,
            'sem_interesse': 30
        }
        
        days = followup_days.get(outcome, 7)
        next_date = datetime.now() + timedelta(days=days)
        
        return next_date.isoformat()
    
    def _determine_lead_status(self, outcome: str) -> str:
        """Determinar status do lead"""
        
        status_map = {
            'agendou_visita': 'quente',
            'interessado': 'morno',
            'precisa_pensar': 'frio',
            'sem_interesse': 'perdido'
        }
        
        return status_map.get(outcome, 'morno')
