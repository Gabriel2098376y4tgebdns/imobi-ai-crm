"""
Configurações da aplicação
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    database_url: str = "postgresql://imobi_user:imobi_pass@localhost:5432/imobi_ai"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = "your_openai_api_key_here"
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.3
    
    # WhatsApp
    whatsapp_token: str = "your_whatsapp_token_here"
    whatsapp_phone_id: str = "your_phone_id_here"
    whatsapp_verify_token: str = "your_verify_token_here"
    
    # Application
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Permitir campos extras


@lru_cache()
def get_settings():
    return Settings()
