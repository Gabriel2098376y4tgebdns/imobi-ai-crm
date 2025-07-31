"""
Configuração de IA e OpenAI
"""

import os
from typing import Optional
from core.logger import logger


class AIConfig:
    """Configuração centralizada de IA"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
        
        # Validar configuração
        self._validate_config()
    
    def _validate_config(self):
        """Validar configuração de IA"""
        if not self.openai_api_key or self.openai_api_key == 'your_openai_api_key_here':
            logger.warning("OpenAI API Key não configurada. Usando modo fallback.")
            self.ai_enabled = False
        else:
            logger.info("OpenAI configurada com sucesso")
            self.ai_enabled = True
    
    def get_openai_config(self) -> dict:
        """Obter configuração OpenAI"""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'temperature': self.openai_temperature,
            'enabled': self.ai_enabled
        }
    
    def is_ai_enabled(self) -> bool:
        """Verificar se IA está habilitada"""
        return self.ai_enabled


# Instância global
ai_config = AIConfig()
