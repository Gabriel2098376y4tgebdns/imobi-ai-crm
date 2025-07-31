"""
Configuração Centralizada do Sistema
"""

import os
from typing import Dict, Any

class Config:
    """Configuração centralizada"""
    
    # DATABASE
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://imobi_user:imobi_pass@localhost:5432/imobi_ai')
    
    # OPENAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # WHATSAPP
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
    WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')
    
    # SISTEMA
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # MATCHING
    DEFAULT_RADIUS_KM = int(os.getenv('DEFAULT_RADIUS_KM', '3'))
    MIN_SCORE_THRESHOLD = int(os.getenv('MIN_SCORE_THRESHOLD', '60'))
    
    # AUTOMAÇÃO
    XML_IMPORT_HOUR = os.getenv('XML_IMPORT_HOUR', '08:00')
    ENABLE_AUTO_MATCHING = os.getenv('ENABLE_AUTO_MATCHING', 'True').lower() == 'true'
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Retornar todas as configurações"""
        return {
            'database_url': cls.DATABASE_URL,
            'openai_configured': bool(cls.OPENAI_API_KEY),
            'whatsapp_configured': bool(cls.WHATSAPP_TOKEN),
            'debug': cls.DEBUG,
            'log_level': cls.LOG_LEVEL,
            'default_radius_km': cls.DEFAULT_RADIUS_KM,
            'min_score_threshold': cls.MIN_SCORE_THRESHOLD,
            'xml_import_hour': cls.XML_IMPORT_HOUR,
            'auto_matching_enabled': cls.ENABLE_AUTO_MATCHING
        }

# Instância global
config = Config()
