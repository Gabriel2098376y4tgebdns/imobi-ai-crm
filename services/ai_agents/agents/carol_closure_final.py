"""
Agent Carol - Encerramento Educado (Versão Final)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from core.logger import logger


class CarolClosureAgent:
    """
    Carol - Encerramento profissional e educado
    Identifica desinteresse e encerra mantendo relacionamento
    """
    
    def __init__(self):
        pass
    
    def detect_disinterest(self, client_messages: List[str]) -> bool:
        """Detectar sinais de desinteresse"""
        
        recent_messages = ' '.join(client_messages[-2:]).lower()
        
        disinterest_signals = [
            'não tenho interesse',
            'não me interessa',
            'muito caro',
            'não é o que procuro',
            'não é o momento',
            'não quero',
            'sem interesse',
            'não preciso'
        ]
        
        return any(signal in recent_messages for signal in disinterest_signals)
    
    def create_closure_message(self, reason: str = "desinteresse") -> str:
        """Criar mensagem de encerramento educada"""
        
        if reason == "orcamento":
            return """Compreendo perfeitamente. 
Manteremos seu contato e caso surjam opções dentro do seu orçamento, entraremos em contato.
Obrigada pelo tempo dedicado."""
        
        elif reason == "timing":
            return """Entendo que não é o momento ideal.
Fico à disposição para quando for a hora certa.
Obrigada pelo contato."""
        
        else:  # desinteresse geral
            return """Sem problemas, compreendo.
Agradeço seu tempo e fico à disposição caso precise de ajuda no futuro.
Tenha um ótimo dia."""
    
    def create_future_contact_offer(self, client_profile: Dict) -> str:
        """Oferecer contato futuro"""
        
        return f"""Manteremos seu perfil cadastrado para {client_profile.get('tipo_imovel', 'imóveis')} na região de {', '.join(client_profile.get('cidades_interesse', []))}.
Caso surjam novas opções, entraremos em contato."""
    
    def update_lead_status(self, lead_id: str, closure_reason: str) -> Dict:
        """Atualizar status do lead como encerrado"""
        
        return {
            'lead_id': lead_id,
            'status': 'encerrado',
            'motivo_encerramento': closure_reason,
            'data_encerramento': datetime.now().isoformat(),
            'observacoes': f'Conversa encerrada pela Carol - Motivo: {closure_reason}',
            'disponivel_para_recontato': True,
            'proximo_contato_sugerido': (datetime.now() + timedelta(days=90)).isoformat(),
            'agent_responsavel': 'Carol'
        }
