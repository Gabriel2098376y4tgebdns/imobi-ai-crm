"""
Processador de Mensagens
"""

import re
from typing import Dict, Any, List

class MessageProcessor:
    def __init__(self):
        self.intent_patterns = {
            "saudacao": [r"\b(oi|olá|ola|bom dia|boa tarde|boa noite)\b"],
            "interesse_imovel": [r"\b(apartamento|casa|imóvel|comprar|alugar)\b"],
            "preco": [r"\b(preço|valor|quanto)\b"],
            "agendamento": [r"\b(visita|agendar|conhecer)\b"],
            "despedida": [r"\b(tchau|obrigado|valeu)\b"]
        }
    
    async def process_message(self, message: str, session: Dict[str, Any], message_type: str = "text") -> Dict[str, Any]:
        intent_result = self._classify_intent(message)
        
        response_message = self._generate_response(
            intent_result['intent'], 
            session.get('contact_name', 'Cliente'),
            message
        )
        
        return {
            "response_message": response_message,
            "intent": intent_result['intent'],
            "confidence": intent_result['confidence'],
            "agent_used": "basic_processor",
            "quick_replies": self._get_quick_replies(intent_result['intent']),
            "delay_seconds": 1
        }
    
    def _classify_intent(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return {"intent": intent, "confidence": 0.8}
        
        return {"intent": "geral", "confidence": 0.5}
    
    def _generate_response(self, intent: str, contact_name: str, message: str) -> str:
        responses = {
            "saudacao": f"Olá {contact_name}! Sou a Carol, sua assistente imobiliária. Como posso ajudar?",
            "interesse_imovel": f"Perfeito {contact_name}! Vejo interesse em imóveis. É para compra ou locação?",
            "preco": f"{contact_name}, os preços variam. Que tipo de imóvel você procura?",
            "agendamento": f"Ótimo {contact_name}! Vou verificar horários. Qual período prefere?",
            "despedida": f"Foi um prazer {contact_name}! Qualquer dúvida, estarei aqui.",
            "geral": f"Entendi {contact_name}! Como assistente imobiliária, posso ajudar com imóveis e preços."
        }
        
        return responses.get(intent, responses["geral"])
    
    def _get_quick_replies(self, intent: str) -> List[str]:
        quick_replies = {
            "saudacao": ["🏠 Apartamentos", "�� Casas", "💰 Preços"],
            "interesse_imovel": ["💰 Compra", "🏠 Locação", "📍 Regiões"],
            "preco": ["🏠 Apartamento", "🏡 Casa", "📍 Regiões"],
            "agendamento": ["🌅 Manhã", "🌞 Tarde", "📅 Final de semana"],
            "geral": ["🏠 Ver imóveis", "💰 Preços", "📋 Garantias"]
        }
        
        return quick_replies.get(intent, quick_replies["geral"])
