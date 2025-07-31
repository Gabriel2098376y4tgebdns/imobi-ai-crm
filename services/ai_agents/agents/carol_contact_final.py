"""
Agent Carol - Primeiro Contato (Versão Final com Fotos)
"""

from typing import Dict, List, Any
from core.logger import logger


class CarolContactAgent:
    """
    Corretora Carol - Primeiro contato profissional com links de galeria
    
    PERSONALIDADE:
    - 36 anos, 15 anos de experiência
    - Muito profissional, não usa gírias
    - Textos curtos e diretos
    - Não usa emojis
    - Analisa mensagens antes de responder
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def create_initial_contact(self, lead_data: Dict, imobiliaria_nome: str, region: str) -> str:
        """Criar mensagem de primeiro contato"""
        
        client_name = lead_data.get('nome', 'Cliente')
        
        message = f"""Boa tarde {client_name}, sou a Corretora Carol da {imobiliaria_nome}.
Vi que você tem interesse em imóveis na região de {region}.
Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
Posso te mandar algumas opções?"""
        
        logger.info(f"Mensagem inicial criada para {client_name}")
        return message
    
    def create_properties_presentation(self, matched_properties: List[Dict], cliente_id: str) -> str:
        """Apresentar imóveis com links de galeria"""
        
        if not matched_properties:
            return "No momento não temos imóveis disponíveis que atendam seu perfil."
        
        presentation = []
        
        for i, prop in enumerate(matched_properties, 1):
            # Criar link da galeria
            gallery_link = f"{self.base_url}/galeria/{cliente_id}/{prop.get('id')}"
            
            # Contar fotos
            fotos = prop.get('fotos', [])
            total_fotos = len(fotos) if isinstance(fotos, list) else len(fotos.split(',')) if fotos else 0
            
            # Formatação do imóvel
            presentation.append(f"{i}. {prop.get('titulo')} - R\$ {prop.get('preco', 0):,.2f}")
            presentation.append(f"{prop.get('endereco')} - {prop.get('quartos')} quartos, {prop.get('area_total')} m²")
            presentation.append(f"Ver fotos ({total_fotos} fotos): {gallery_link}")
            presentation.append("")  # Linha em branco
        
        presentation.append("Algum desses imóveis te interessou?")
        
        logger.info(f"Apresentação criada para {len(matched_properties)} imóveis com fotos")
        return "\n".join(presentation)
    
    def analyze_client_response(self, client_message: str) -> Dict[str, Any]:
        """Analisar resposta do cliente"""
        
        client_lower = client_message.lower()
        
        # Palavras de interesse positivo
        positive_words = ['sim', 'pode', 'manda', 'ok', 'quero', 'interesse', 'gostei']
        
        # Palavras de desinteresse
        negative_words = ['não', 'nao', 'sem interesse', 'muito caro', 'não tenho']
        
        has_positive = any(word in client_lower for word in positive_words)
        has_negative = any(word in client_lower for word in negative_words)
        
        if has_positive and not has_negative:
            return {
                'interest_level': 'high',
                'next_action': 'send_properties',
                'response_type': 'positive'
            }
        elif has_negative:
            return {
                'interest_level': 'low',
                'next_action': 'closure',
                'response_type': 'negative'
            }
        else:
            return {
                'interest_level': 'unclear',
                'next_action': 'clarify',
                'response_type': 'neutral'
            }
