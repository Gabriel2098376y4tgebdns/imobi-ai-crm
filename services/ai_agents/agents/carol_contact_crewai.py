"""
Agent Carol - Primeiro Contato (CrewAI Completo)
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from core.logger import logger
from typing import Dict, List, Any


class CarolContactAgentCrewAI:
    """
    Corretora Carol - CrewAI completo com IA avançada
    
    PERSONALIDADE:
    - 36 anos, 15 anos de experiência
    - Muito profissional, não usa gírias
    - Textos curtos e diretos
    - Não usa emojis
    - Analisa mensagens antes de responder
    """
    
    def __init__(self, openai_api_key: str, base_url: str = "http://localhost:8000"):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.3
        )
        self.base_url = base_url
        
        # Agent CrewAI
        self.agent = Agent(
            role="Corretora Imobiliária Sênior - Carol",
            goal="Fazer primeiro contato profissional e apresentar imóveis com links de galeria",
            backstory="""
            Você é a Carol, uma corretora imobiliária com 36 anos e 15 anos de experiência no mercado.
            
            PERSONALIDADE ÚNICA:
            - Muito profissional e experiente
            - Comunicação direta e objetiva
            - NUNCA usa gírias, "olá" ou linguagem informal
            - NUNCA usa emojis
            - Textos curtos e diretos (máximo 4 linhas por mensagem)
            - Analisa bem as mensagens antes de responder
            - Linguagem profissional adaptada para WhatsApp
            - SEMPRE inclui links de galeria de fotos
            
            COMPORTAMENTO ESPECÍFICO:
            - Sempre se apresenta como "Corretora Carol"
            - Menciona o nome da imobiliária
            - É direta ao ponto, sem rodeios
            - Foca no que o cliente precisa
            - Confirma informações antes de prosseguir
            - SEMPRE inclui links para visualização de fotos dos imóveis
            
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
    
    def create_initial_contact(self, lead_data: Dict, imobiliaria_nome: str, region: str) -> str:
        """Criar mensagem de primeiro contato usando CrewAI"""
        
        client_name = lead_data.get('nome', 'Cliente')
        property_type = lead_data.get('tipo_imovel', 'imóvel')
        
        task = Task(
            description=f"""
            Crie uma mensagem de primeiro contato para WhatsApp seguindo EXATAMENTE a personalidade da Carol.

            DADOS:
            - Cliente: {client_name}
            - Imobiliária: {imobiliaria_nome}
            - Região de interesse: {region}
            - Tipo de imóvel: {property_type}

            ROTEIRO OBRIGATÓRIO:
            1. Se apresentar como Corretora Carol
            2. Mencionar o nome da imobiliária: {imobiliaria_nome}
            3. Dizer que a pessoa entrou em contato interessada em imóveis na região {region}
            4. Informar que acabamos de cadastrar novos produtos que se enquadram no que ela busca
            5. Perguntar: "Posso te mandar algumas opções?"

            REGRAS CAROL (OBRIGATÓRIAS):
            - Linguagem profissional mas adequada para WhatsApp
            - Textos curtos e diretos (máximo 4 linhas)
            - SEM emojis
            - SEM gírias
            - SEM "olá" ou cumprimentos informais
            - Usar "Boa tarde" ou "Bom dia"

            FORMATO: Apenas a mensagem, sem aspas ou formatação extra.
            """,
            agent=self.agent,
            expected_output="Mensagem de primeiro contato profissional seguindo exatamente a personalidade da Carol"
        )
        
        try:
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info(f"Mensagem inicial CrewAI criada para {client_name}")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro no CrewAI primeiro contato: {e}")
            return self._fallback_initial_message(client_name, imobiliaria_nome, region)
    
    def create_properties_presentation(self, matched_properties: List[Dict], cliente_id: str) -> str:
        """Apresentar imóveis com links de galeria usando CrewAI"""
        
        if not matched_properties:
            return "No momento não temos imóveis disponíveis que atendam seu perfil."
        
        # Preparar dados dos imóveis com links
        properties_data = []
        for i, prop in enumerate(matched_properties, 1):
            gallery_link = f"{self.base_url}/galeria/{cliente_id}/{prop.get('id')}"
            fotos = prop.get('fotos', [])
            total_fotos = len(fotos) if isinstance(fotos, list) else len(fotos.split(',')) if fotos else 0
            
            properties_data.append({
                'numero': i,
                'titulo': prop.get('titulo'),
                'preco': f"R\$ {prop.get('preco', 0):,.2f}",
                'endereco': prop.get('endereco'),
                'quartos': prop.get('quartos'),
                'area': prop.get('area_total'),
                'galeria_link': gallery_link,
                'total_fotos': total_fotos
            })
        
        task = Task(
            description=f"""
            Apresente os imóveis de forma profissional incluindo OBRIGATORIAMENTE os links para visualização.

            IMÓVEIS ENCONTRADOS ({len(properties_data)} opções):
            {self._format_properties_for_crewai(properties_data)}

            REGRAS CAROL (OBRIGATÓRIAS):
            - Apresentar cada imóvel em 2-3 linhas máximo
            - SEMPRE incluir o link "Ver fotos:" após cada imóvel
            - Mencionar quantidade de fotos disponíveis
            - Linguagem profissional
            - SEM emojis
            - Ao final perguntar: "Algum desses imóveis te interessou?"

            FORMATO OBRIGATÓRIO PARA CADA IMÓVEL:
            1. [Título] - [Preço]
            [Endereço] - [Quartos] quartos, [Área] m²
            Ver fotos ([X] fotos): [link]

            IMPORTANTE: SEMPRE incluir os links de galeria!
            """,
            agent=self.agent,
            expected_output="Apresentação profissional dos imóveis com links de galeria obrigatórios"
        )
        
        try:
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info(f"Apresentação CrewAI criada para {len(properties_data)} imóveis")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro na apresentação CrewAI: {e}")
            return self._fallback_presentation_with_photos(properties_data)
    
    def analyze_client_response(self, client_message: str) -> Dict[str, Any]:
        """Analisar resposta do cliente usando CrewAI"""
        
        task = Task(
            description=f"""
            Analise a resposta do cliente e determine o nível de interesse.

            RESPOSTA DO CLIENTE: "{client_message}"

            Determine:
            1. Nível de interesse (high/medium/low)
            2. Próxima ação (send_properties/clarify/closure)
            3. Tipo de resposta (positive/negative/neutral)

            CRITÉRIOS:
            - Palavras positivas: sim, pode, manda, ok, quero, interesse, gostei
            - Palavras negativas: não, sem interesse, muito caro, não tenho
            - Respostas vagas: talvez, depois, vou pensar

            FORMATO: Responda apenas com: INTERESSE_LEVEL|NEXT_ACTION|RESPONSE_TYPE
            Exemplo: high|send_properties|positive
            """,
            agent=self.agent,
            expected_output="Análise estruturada da resposta do cliente"
        )
        
        try:
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
            result = str(crew.kickoff()).strip()
            
            # Parse do resultado
            parts = result.split('|')
            if len(parts) >= 3:
                return {
                    'interest_level': parts[0].strip(),
                    'next_action': parts[1].strip(),
                    'response_type': parts[2].strip()
                }
            
        except Exception as e:
            logger.error(f"Erro na análise CrewAI: {e}")
        
        # Fallback para análise simples
        return self._simple_analysis(client_message)
    
    def _format_properties_for_crewai(self, properties: List[Dict]) -> str:
        """Formatar imóveis para o CrewAI"""
        formatted = []
        for prop in properties:
            formatted.append(f"""
            Imóvel {prop['numero']}:
            - Título: {prop['titulo']}
            - Preço: {prop['preco']}
            - Endereço: {prop['endereco']}
            - Quartos: {prop['quartos']}
            - Área: {prop['area']} m²
            - Link galeria: {prop['galeria_link']}
            - Total fotos: {prop['total_fotos']}
            """)
        return "\n".join(formatted)
    
    def _fallback_initial_message(self, client_name: str, imobiliaria_nome: str, region: str) -> str:
        """Mensagem de fallback"""
        return f"""Boa tarde {client_name}, sou a Corretora Carol da {imobiliaria_nome}.
Vi que você tem interesse em imóveis na região de {region}.
Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
Posso te mandar algumas opções?"""
    
    def _fallback_presentation_with_photos(self, properties: List[Dict]) -> str:
        """Apresentação de fallback com fotos"""
        presentation = []
        
        for prop in properties:
            presentation.append(f"{prop['numero']}. {prop['titulo']} - {prop['preco']}")
            presentation.append(f"{prop['endereco']} - {prop['quartos']} quartos, {prop['area']} m²")
            presentation.append(f"Ver fotos ({prop['total_fotos']} fotos): {prop['galeria_link']}")
            presentation.append("")
        
        presentation.append("Algum desses imóveis te interessou?")
        return "\n".join(presentation)
    
    def _simple_analysis(self, client_message: str) -> Dict[str, Any]:
        """Análise simples de fallback"""
        client_lower = client_message.lower()
        
        positive_words = ['sim', 'pode', 'manda', 'ok', 'quero', 'interesse', 'gostei']
        negative_words = ['não', 'nao', 'sem interesse', 'muito caro', 'não tenho']
        
        has_positive = any(word in client_lower for word in positive_words)
        has_negative = any(word in client_lower for word in negative_words)
        
        if has_positive and not has_negative:
            return {'interest_level': 'high', 'next_action': 'send_properties', 'response_type': 'positive'}
        elif has_negative:
            return {'interest_level': 'low', 'next_action': 'closure', 'response_type': 'negative'}
        else:
            return {'interest_level': 'medium', 'next_action': 'clarify', 'response_type': 'neutral'}
