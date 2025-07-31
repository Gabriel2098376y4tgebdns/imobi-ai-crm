"""
Agent Carol - Atualizado com links de galeria
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from core.logger import logger
from typing import Dict, List, Any


class CarolContactAgentUpdated:
    """Carol com suporte a links de galeria de fotos"""
    
    def __init__(self, openai_api_key: str, base_url: str = "http://localhost:8000"):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.3
        )
        self.base_url = base_url
        
        self.agent = Agent(
            role="Corretora Imobiliária Sênior",
            goal="Fazer primeiro contato profissional incluindo links para visualização de fotos",
            backstory="""
            Você é a Carol, corretora experiente que sempre inclui links para que
            os clientes possam visualizar as fotos dos imóveis apresentados.
            
            PERSONALIDADE (mantém a mesma):
            - Profissional e direta
            - Não usa emojis nem gírias
            - Textos objetivos
            - Sempre inclui links de visualização
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_properties_presentation_with_photos(self, matched_properties: List[Dict], cliente_id: str) -> str:
        """Apresentar imóveis com links para galeria de fotos"""
        
        # Preparar dados dos imóveis com links
        properties_with_links = []
        for prop in matched_properties:
            gallery_link = f"{self.base_url}/galeria/{cliente_id}/{prop.get('id')}"
            
            properties_with_links.append({
                'titulo': prop.get('titulo'),
                'preco': f"R\$ {prop.get('preco', 0):,.2f}",
                'endereco': prop.get('endereco'),
                'quartos': prop.get('quartos'),
                'area': prop.get('area_total'),
                'galeria_link': gallery_link,
                'total_fotos': len(prop.get('fotos', []))
            })
        
        prompt = f"""
        Apresente os imóveis de forma profissional incluindo links para visualização.

        IMÓVEIS ENCONTRADOS ({len(properties_with_links)} opções):
        {self._format_properties_with_links(properties_with_links)}

        REGRAS CAROL:
        - Apresentar cada imóvel em 2-3 linhas
        - SEMPRE incluir o link "Ver fotos:" após cada imóvel
        - Mencionar quantidade de fotos disponíveis
        - Linguagem profissional
        - SEM emojis
        - Ao final perguntar: "Algum desses imóveis te interessou?"

        FORMATO EXEMPLO:
        1. [Título] - [Preço]
        [Endereço] - [Quartos] quartos, [Área] m²
        Ver fotos (X fotos): [link]

        FORMATO: Lista completa + pergunta final
        """
        
        try:
            from crewai import Task
            
            task = Task(
                description=prompt,
                agent=self.agent,
                expected_output="Apresentação dos imóveis com links de galeria"
            )
            
            message = task.execute()
            logger.info(f"Apresentação com fotos criada para {len(properties_with_links)} imóveis")
            return message.strip()
            
        except Exception as e:
            logger.error(f"Erro ao criar apresentação com fotos: {e}")
            return self._fallback_presentation_with_photos(properties_with_links)
    
    def _format_properties_with_links(self, properties: List[Dict]) -> str:
        """Formatar imóveis com links para o prompt"""
        formatted = []
        for i, prop in enumerate(properties, 1):
            formatted.append(f"""
            Imóvel {i}:
            - Título: {prop['titulo']}
            - Preço: {prop['preco']}
            - Endereço: {prop['endereco']}
            - Quartos: {prop['quartos']}
            - Área: {prop['area']} m²
            - Link galeria: {prop['galeria_link']}
            - Total fotos: {prop['total_fotos']}
            """)
        return "\n".join(formatted)
    
    def _fallback_presentation_with_photos(self, properties: List[Dict]) -> str:
        """Apresentação de fallback com links"""
        presentation = []
        
        for i, prop in enumerate(properties, 1):
            presentation.append(f"{i}. {prop['titulo']} - {prop['preco']}")
            presentation.append(f"{prop['endereco']} - {prop['quartos']} quartos, {prop['area']} m²")
            presentation.append(f"Ver fotos ({prop['total_fotos']} fotos): {prop['galeria_link']}")
            presentation.append("")  # Linha em branco
        
        presentation.append("Algum desses imóveis te interessou?")
        return "\n".join(presentation)
