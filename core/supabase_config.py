"""
Configuração Supabase
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

class SupabaseConfig:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        
        # Criar clientes
        self.client = None
        self.admin_client = None
        
        try:
            from supabase import create_client
            if self.url and self.anon_key:
                self.client = create_client(self.url, self.anon_key)
            if self.url and self.service_key:
                self.admin_client = create_client(self.url, self.service_key)
        except ImportError:
            print("⚠️ Supabase não instalado")

# Instância global
supabase_config = SupabaseConfig()

def get_supabase_client():
    """Obter cliente Supabase"""
    return supabase_config.client

def get_admin_client():
    """Obter cliente admin"""
    return supabase_config.admin_client

def get_database_url():
    """Obter URL do banco"""
    return supabase_config.database_url
