"""
Agent Carol - Agendamento de Visitas (Versão Final)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid
from core.logger import logger


class CarolSchedulingAgent:
    """
    Carol - Agendamento profissional de visitas
    Coleta: imóvel, data, horário
    """
    
    def __init__(self):
        pass
    
    def create_scheduling_request(self, property_interest: str) -> str:
        """Solicitar informações para agendamento"""
        
        message = """Perfeito. Para agendar a visita preciso de algumas informações:
1. Qual imóvel te interessou?
2. Que dia seria melhor para você?
3. Qual horário prefere (manhã ou tarde)?"""
        
        logger.info("Solicitação de agendamento criada")
        return message
    
    def parse_scheduling_info(self, client_message: str, available_properties: List[Dict]) -> Dict:
        """Extrair informações de agendamento da mensagem"""
        
        client_lower = client_message.lower()
        
        # Identificar imóvel
        selected_property = None
        for i, prop in enumerate(available_properties):
            if str(i + 1) in client_message or prop.get('codigo_imovel', '').lower() in client_lower:
                selected_property = prop
                break
        
        # Identificar preferência de período
        period_preference = None
        if any(word in client_lower for word in ['manhã', 'manha', '9', '10', '11']):
            period_preference = 'manha'
        elif any(word in client_lower for word in ['tarde', '14', '15', '16', '17']):
            period_preference = 'tarde'
        
        # Identificar dia da semana
        day_preference = None
        days_map = {
            'segunda': 'segunda-feira',
            'terça': 'terça-feira',
            'terca': 'terça-feira',
            'quarta': 'quarta-feira',
            'quinta': 'quinta-feira',
            'sexta': 'sexta-feira',
            'sabado': 'sábado',
            'sábado': 'sábado'
        }
        
        for day_key, day_value in days_map.items():
            if day_key in client_lower:
                day_preference = day_value
                break
        
        return {
            'selected_property': selected_property,
            'period_preference': period_preference,
            'day_preference': day_preference,
            'needs_clarification': not all([selected_property, period_preference])
        }
    
    def generate_time_slots(self, period: str = None, days_ahead: int = 7) -> List[str]:
        """Gerar opções de horários"""
        
        slots = []
        current_date = datetime.now()
        
        for day in range(1, days_ahead + 1):
            visit_date = current_date + timedelta(days=day)
            
            # Pular domingos
            if visit_date.weekday() == 6:
                continue
            
            day_name = visit_date.strftime("%A").replace('Monday', 'Segunda').replace('Tuesday', 'Terça').replace('Wednesday', 'Quarta').replace('Thursday', 'Quinta').replace('Friday', 'Sexta').replace('Saturday', 'Sábado')
            
            if not period or period == 'manha':
                for hour in [9, 10, 11]:
                    slot = f"{day_name}, {visit_date.strftime('%d/%m')} às {hour}h"
                    slots.append(slot)
            
            if not period or period == 'tarde':
                for hour in [14, 15, 16, 17]:
                    slot = f"{day_name}, {visit_date.strftime('%d/%m')} às {hour}h"
                    slots.append(slot)
        
        return slots[:8]  # Máximo 8 opções
    
    def create_confirmation_message(self, scheduling_data: Dict) -> str:
        """Criar mensagem de confirmação"""
        
        message = f"""Agendamento confirmado:

Imóvel: {scheduling_data.get('codigo_imovel')} - {scheduling_data.get('endereco_imovel')}
Data e horário: {scheduling_data.get('data_visita_formatted')}

Entrarei em contato um dia antes para confirmar.
Qualquer dúvida, estarei à disposição."""
        
        logger.info(f"Confirmação criada para: {scheduling_data.get('nome_cliente')}")
        return message
    
    def create_crm_record(self, lead_data: Dict, property_data: Dict, visit_datetime: str) -> Dict:
        """Criar registro no CRM"""
        
        agendamento_id = str(uuid.uuid4())
        
        return {
            'id': agendamento_id,
            'cliente_id': lead_data.get('cliente_id'),
            'lead_id': lead_data.get('id'),
            'nome_cliente': lead_data.get('nome'),
            'telefone_cliente': lead_data.get('telefone'),
            'imovel_id': property_data.get('id'),
            'codigo_imovel': property_data.get('codigo_imovel'),
            'endereco_imovel': property_data.get('endereco'),
            'data_visita': visit_datetime,
            'observacoes': 'Agendamento via WhatsApp - Carol',
            'status': 'agendado',
            'data_criacao': datetime.now().isoformat()
        }
