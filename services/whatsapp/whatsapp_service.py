"""
Serviço de WhatsApp para envio de mensagens
"""

import os
import requests
from typing import Dict, Any, Optional
from core.logger import logger


class WhatsAppService:
    """Serviço para envio de mensagens via WhatsApp"""
    
    def __init__(self):
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_ID')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
        
        self.enabled = bool(self.whatsapp_token and self.whatsapp_phone_id)
        
        if self.enabled:
            logger.info("WhatsApp Business API configurado")
        else:
            logger.warning("WhatsApp não configurado. Usando modo simulação.")
    
    def send_message(self, to_number: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Enviar mensagem via WhatsApp"""
        
        if not self.enabled:
            return self._simulate_send(to_number, message)
        
        # Formatar número (remover caracteres especiais)
        formatted_number = self._format_phone_number(to_number)
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Mensagem WhatsApp enviada para {formatted_number}")
            return {
                'status': 'success',
                'message_id': result.get('messages', [{}])[0].get('id'),
                'to': formatted_number,
                'message': message
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'to': formatted_number,
                'message': message
            }
    
    def send_property_gallery(self, to_number: str, property_data: Dict, gallery_url: str) -> Dict[str, Any]:
        """Enviar apresentação de imóvel com galeria"""
        
        message = f"""🏠 {property_data.get('titulo')}
📍 {property_data.get('endereco')}
💰 R\$ {property_data.get('preco', 0):,.2f}

✨ Características:
• {property_data.get('quartos')} quartos
• {property_data.get('banheiros')} banheiros
• {property_data.get('area_total')} m²
• {property_data.get('vagas_garagem')} vagas

Ver todas as fotos: {gallery_url}

Gostaria de agendar uma visita?"""
        
        return self.send_message(to_number, message)
    
    def _format_phone_number(self, phone: str) -> str:
        """Formatar número de telefone para WhatsApp"""
        # Remover caracteres especiais
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se necessário (Brasil = 55)
        if len(clean_phone) == 11 and clean_phone.startswith('11'):
            clean_phone = '55' + clean_phone
        elif len(clean_phone) == 10:
            clean_phone = '5511' + clean_phone
        
        return clean_phone
    
    def _simulate_send(self, to_number: str, message: str) -> Dict[str, Any]:
        """Simular envio de mensagem (modo desenvolvimento)"""
        
        logger.info(f"[SIMULAÇÃO] WhatsApp para {to_number}: {message[:50]}...")
        
        return {
            'status': 'simulated',
            'message_id': f'sim_{hash(message) % 10000}',
            'to': to_number,
            'message': message,
            'note': 'Mensagem simulada - Configure WHATSAPP_TOKEN para envio real'
        }
    
    def is_enabled(self) -> bool:
        """Verificar se WhatsApp está habilitado"""
        return self.enabled


# Instância global
whatsapp_service = WhatsAppService()
