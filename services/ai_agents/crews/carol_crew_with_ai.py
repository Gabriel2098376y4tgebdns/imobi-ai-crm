"""
Carol Crew com OpenAI Real
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from core.logger import logger
from core.ai_config import ai_config
from typing import Dict, List, Any


class CarolCrewWithAI:
    """
    Sistema completo de agents da Carol com OpenAI real
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ai_enabled = ai_config.is_ai_enabled()
        
        if self.ai_enabled:
            openai_config = ai_config.get_openai_config()
            self.llm = ChatOpenAI(
                model=openai_config['model'],
                api_key=openai_config['api_key'],
                temperature=openai_config['temperature']
            )
            self._create_agents()
            logger.info("Carol Crew com OpenAI inicializada")
        else:
            logger.info("Carol Crew em modo fallback (sem OpenAI)")
    
    def _create_agents(self):
        """Criar agents com OpenAI"""
        
        self.contact_agent = Agent(
            role="Corretora de Primeiro Contato - Carol",
            goal="Fazer primeiro contato profissional e apresentar imóveis com links de galeria",
            backstory="""
            Você é a Carol, corretora com 36 anos e 15 anos de experiência.
            
            PERSONALIDADE ÚNICA:
            - Muito profissional, nunca usa gírias ou emojis
            - Textos curtos e diretos (máximo 4 linhas)
            - Sempre se apresenta como "Corretora Carol"
            - Menciona nome da imobiliária
            - SEMPRE inclui links de galeria de fotos
            
            COMPORTAMENTO ESPECÍFICO:
            - Analisa mensagens antes de responder
            - Confirma informações antes de prosseguir
            - Foca no que o cliente precisa
            - É direta ao ponto, sem rodeios
            
            EXEMPLO DE COMUNICAÇÃO:
            "Boa tarde [Nome], sou a Corretora Carol da [Imobiliária].
            Vi que você tem interesse em imóveis na região de [Região].
            Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
            Posso te mandar algumas opções?"
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.presentation_agent = Agent(
            role="Especialista em Apresentação - Carol",
            goal="Apresentar imóveis destacando pontos relevantes com links de galeria",
            backstory="""
            Você é a Carol, especialista em apresentar imóveis.
            
            ESPECIALIDADE:
            - Destaca características que fazem match
            - Menciona benefícios da localização
            - SEMPRE inclui links de galeria de fotos
            - Foca no que importa para o cliente
            - Mantém profissionalismo
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def execute_initial_contact(self, lead_data: Dict, imobiliaria_nome: str, region: str) -> str:
        """Executar primeiro contato com IA real"""
        
        if not self.ai_enabled:
            return self._fallback_initial_contact(lead_data['nome'], imobiliaria_nome, region)
        
        client_name = lead_data.get('nome', 'Cliente')
        property_type = lead_data.get('tipo_imovel', 'imóvel')
        
        task = Task(
            description=f"""
            Crie uma mensagem de primeiro contato para WhatsApp seguindo EXATAMENTE a personalidade da Carol.

            DADOS:
            - Cliente: {client_name}
            - Imobiliária: {imobiliaria_nome}
            - Região: {region}
            - Tipo: {property_type}

            ROTEIRO OBRIGATÓRIO:
            1. Se apresentar como Corretora Carol
            2. Mencionar imobiliária: {imobiliaria_nome}
            3. Referenciar interesse em {region}
            4. Informar novos produtos cadastrados
            5. Perguntar: "Posso te mandar algumas opções?"

            REGRAS CAROL (OBRIGATÓRIAS):
            - Máximo 4 linhas
            - SEM emojis
            - SEM gírias
            - Profissional para WhatsApp
            - Usar "Boa tarde" ou "Bom dia"
            """,
            agent=self.contact_agent,
            expected_output="Mensagem profissional de primeiro contato"
        )
        
        try:
            crew = Crew(agents=[self.contact_agent], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            logger.info(f"Primeiro contato com IA executado para {client_name}")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro no primeiro contato com IA: {e}")
            return self._fallback_initial_contact(client_name, imobiliaria_nome, region)
    
    def execute_properties_presentation(self, matched_properties: List[Dict], cliente_id: str) -> str:
        """Apresentar imóveis com IA real"""
        
        if not self.ai_enabled or not matched_properties:
            return self._fallback_presentation(matched_properties, cliente_id)
        
        # Preparar dados com links
        properties_info = []
        for i, prop in enumerate(matched_properties, 1):
            gallery_link = f"{self.base_url}/galeria/{cliente_id}/{prop.get('id')}"
            fotos = prop.get('fotos', [])
            total_fotos = len(fotos) if isinstance(fotos, list) else len(fotos.split(',')) if fotos else 0
            
            properties_info.append(f"""
            {i}. {prop.get('titulo')} - R\$ {prop.get('preco', 0):,.2f}
            {prop.get('endereco')} - {prop.get('quartos')} quartos, {prop.get('area_total')} m²
            Ver fotos ({total_fotos} fotos): {gallery_link}
            """)
        
        task = Task(
            description=f"""
            Apresente os imóveis de forma profissional incluindo OBRIGATORIAMENTE os links.

            IMÓVEIS ({len(matched_properties)} opções):
            {''.join(properties_info)}

            REGRAS CAROL (OBRIGATÓRIAS):
            - Apresentar cada imóvel em 2-3 linhas máximo
            - SEMPRE incluir link "Ver fotos:"
            - Mencionar quantidade de fotos
            - SEM emojis
            - Ao final: "Algum desses imóveis te interessou?"

            FORMATO OBRIGATÓRIO:
            [Número]. [Título] - [Preço]
            [Endereço] - [Quartos] quartos, [Área] m²
            Ver fotos ([X] fotos): [link]
            """,
            agent=self.presentation_agent,
            expected_output="Apresentação profissional com links de galeria"
        )
        
        try:
            crew = Crew(agents=[self.presentation_agent], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            logger.info(f"Apresentação com IA executada para {len(matched_properties)} imóveis")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro na apresentação com IA: {e}")
            return self._fallback_presentation(matched_properties, cliente_id)
    
    def _fallback_initial_contact(self, client_name: str, imobiliaria_nome: str, region: str) -> str:
        """Fallback sem IA"""
        return f"""Boa tarde {client_name}, sou a Corretora Carol da {imobiliaria_nome}.
Vi que você tem interesse em imóveis na região de {region}.
Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
Posso te mandar algumas opções?"""
    
    def _fallback_presentation(self, properties: List[Dict], cliente_id: str) -> str:
        """Fallback apresentação sem IA"""
        if not properties:
            return "No momento não temos imóveis disponíveis que atendam seu perfil."
        
        presentation = []
        for i, prop in enumerate(properties, 1):
            gallery_link = f"{self.base_url}/galeria/{cliente_id}/{prop.get('id')}"
            fotos = prop.get('fotos', [])
            total_fotos = len(fotos) if isinstance(fotos, list) else len(fotos.split(',')) if fotos else 0
            
            presentation.append(f"{i}. {prop.get('titulo')} - R\$ {prop.get('preco', 0):,.2f}")
            presentation.append(f"{prop.get('endereco')} - {prop.get('quartos')} quartos, {prop.get('area_total')} m²")
            presentation.append(f"Ver fotos ({total_fotos} fotos): {gallery_link}")
            presentation.append("")
        
        presentation.append("Algum desses imóveis te interessou?")
        return "\n".join(presentation)
