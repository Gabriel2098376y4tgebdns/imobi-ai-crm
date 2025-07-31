"""
Template de configuração por cliente
"""

from typing import Dict, Any

class ClienteConfig:
    def __init__(self):
        self.nome = "NOME_DO_CLIENTE"
        self.crm_tipo = "vista"  # vista, kenlo, univens, octmob
    
    def get_crm_config(self) -> Dict[str, Any]:
        return {
            "tipo": self.crm_tipo,
            "api_url": "",
            "api_key": "",
            "webhook_url": "",
        }
    
    def get_whatsapp_config(self) -> Dict[str, Any]:
        return {
            "token": "",
            "phone_id": "",
            "webhook_verify_token": "",
        }
    
    def get_matching_rules(self) -> Dict[str, Any]:
        return {
            "tolerancia_preco": 0.1,  # 10%
            "raio_busca_km": 5,
            "tipos_imovel": ["apartamento", "casa"],
        }
