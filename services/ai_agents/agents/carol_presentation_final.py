"""
Agent Carol - Apresentação Detalhada (Versão Final)
"""

from typing import Dict, List, Any
from core.logger import logger


class CarolPresentationAgent:
    """
    Carol - Apresentação detalhada de imóveis específicos
    Foca no imóvel que o cliente demonstrou interesse
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def create_detailed_presentation(self, property_data: Dict, cliente_id: str) -> str:
        """Criar apresentação detalhada de um imóvel específico"""
        
        # Link da galeria
        gallery_link = f"{self.base_url}/galeria/{cliente_id}/{property_data.get('id')}"
        
        # Contar fotos
        fotos = property_data.get('fotos', [])
        total_fotos = len(fotos) if isinstance(fotos, list) else len(fotos.split(',')) if fotos else 0
        
        presentation = f"""{property_data.get('titulo')}
Localização: {property_data.get('endereco')}, {property_data.get('bairro')}
Valor: R\$ {property_data.get('preco', 0):,.2f}

Características:
• {property_data.get('quartos')} quartos
• {property_data.get('banheiros')} banheiros
• {property_data.get('area_total')} m²
• {property_data.get('vagas_garagem')} vagas de garagem

{property_data.get('descricao', '')}

Ver todas as fotos ({total_fotos} fotos): {gallery_link}

Gostaria de agendar uma visita para conhecer pessoalmente?"""
        
        logger.info(f"Apresentação detalhada criada para imóvel: {property_data.get('codigo_imovel')}")
        return presentation
    
    def identify_interested_property(self, client_message: str, available_properties: List[Dict]) -> Dict:
        """Identificar qual imóvel o cliente tem interesse"""
        
        client_lower = client_message.lower()
        
        # Procurar por números (1, 2, 3, primeiro, segundo, etc.)
        for i, prop in enumerate(available_properties):
            if str(i + 1) in client_message or prop.get('codigo_imovel', '').lower() in client_lower:
                return {
                    'found': True,
                    'property': prop,
                    'index': i + 1
                }
        
        # Se não encontrou número específico, assumir interesse geral
        if any(word in client_lower for word in ['sim', 'interesse', 'gostei', 'quero']):
            return {
                'found': False,
                'property': None,
                'needs_clarification': True
            }
        
        return {
            'found': False,
            'property': None,
            'needs_clarification': False
        }
