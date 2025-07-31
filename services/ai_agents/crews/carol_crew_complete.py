"""
Carol Crew - Sistema Completo de Agents CrewAI
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from core.logger import logger
from typing import Dict, List, Any
import os


class CarolCrewComplete:
    """
    Sistema completo de agents da Carol usando CrewAI
    Orquestra todo o fluxo de conversação
    """
    
    def __init__(self, openai_api_key: str, base_url: str = "http://localhost:8000"):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.3
        )
        self.base_url = base_url
        
        # Criar todos os agents
        self._create_agents()
        
        logger.info("Carol Crew Complete inicializada com CrewAI")
    
    def _create_agents(self):
        """Criar todos os agents do sistema"""
        
        # Agent de Primeiro Contato
        self.contact_agent = Agent(
            role="Corretora de Primeiro Contato - Carol",
            goal="Fazer primeiro contato profissional e apresentar imóveis com links de galeria",
            backstory="""
            Você é a Carol, corretora com 36 anos e 15 anos de experiência.
            
            PERSONALIDADE:
            - Muito profissional, nunca usa gírias ou emojis
            - Textos curtos e diretos (máximo 4 linhas)
            - Sempre se apresenta como "Corretora Carol"
            - Menciona nome da imobiliária
            - SEMPRE inclui links de galeria de fotos
            
            COMPORTAMENTO:
            - Analisa mensagens antes de responder
            - Confirma informações antes de prosseguir
            - Foca no que o cliente precisa
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent de Apresentação
        self.presentation_agent = Agent(
            role="Especialista em Apresentação de Imóveis - Carol",
            goal="Apresentar imóveis de forma detalhada destacando pontos relevantes",
            backstory="""
            Você é a Carol, especialista em apresentar imóveis de forma atrativa.
            
            ESPECIALIDADE:
            - Destaca características que fazem match com o perfil
            - Menciona benefícios da localização
            - Foca no que realmente importa para o cliente
            - Sempre termina perguntando sobre interesse em visita
            - Mantém a mesma personalidade profissional
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent de Agendamento
        self.scheduling_agent = Agent(
            role="Especialista em Agendamento - Carol",
            goal="Agendar visitas coletando todas as informações necessárias",
            backstory="""
            Você é a Carol, especialista em agendamentos.
            
            FUNÇÃO:
            - Coleta informações de forma organizada
            - Confirma dados antes de finalizar
            - Oferece opções de horários
            - Esclarece dúvidas sobre o processo
            - Mantém profissionalismo
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent de Encerramento
        self.closure_agent = Agent(
            role="Especialista em Encerramento Profissional - Carol",
            goal="Encerrar conversas de forma educada quando não há interesse",
            backstory="""
            Você é a Carol, especialista em encerramento profissional.
            
            ESPECIALIDADE:
            - Identifica sinais de desinteresse
            - Encerra de forma educada e respeitosa
            - Sempre deixa porta aberta para futuro contato
            - Agradece o tempo do cliente
            - Mantém profissionalismo até o fim
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def execute_initial_contact(self, lead_data: Dict, imobiliaria_nome: str, region: str) -> str:
        """Executar primeiro contato usando CrewAI"""
        
        client_name = lead_data.get('nome', 'Cliente')
        property_type = lead_data.get('tipo_imovel', 'imóvel')
        
        task = Task(
            description=f"""
            Crie uma mensagem de primeiro contato para WhatsApp.

            DADOS:
            - Cliente: {client_name}
            - Imobiliária: {imobiliaria_nome}
            - Região: {region}
            - Tipo: {property_type}

            ROTEIRO:
            1. Se apresentar como Corretora Carol
            2. Mencionar imobiliária: {imobiliaria_nome}
            3. Referenciar interesse em {region}
            4. Informar novos produtos cadastrados
            5. Perguntar: "Posso te mandar algumas opções?"

            REGRAS CAROL:
            - Máximo 4 linhas
            - SEM emojis
            - SEM gírias
            - Profissional para WhatsApp
            """,
            agent=self.contact_agent,
            expected_output="Mensagem profissional de primeiro contato"
        )
        
        try:
            crew = Crew(agents=[self.contact_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info(f"Primeiro contato CrewAI executado para {client_name}")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro no primeiro contato CrewAI: {e}")
            return self._fallback_initial_contact(client_name, imobiliaria_nome, region)
    
    def execute_properties_presentation(self, matched_properties: List[Dict], cliente_id: str) -> str:
        """Apresentar imóveis usando CrewAI"""
        
        if not matched_properties:
            return "No momento não temos imóveis disponíveis que atendam seu perfil."
        
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
            Apresente os imóveis de forma profissional incluindo os links.

            IMÓVEIS ({len(matched_properties)} opções):
            {''.join(properties_info)}

            REGRAS CAROL:
            - Apresentar cada imóvel em 2-3 linhas
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
            crew = Crew(agents=[self.presentation_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info(f"Apresentação CrewAI executada para {len(matched_properties)} imóveis")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro na apresentação CrewAI: {e}")
            return self._fallback_presentation(properties_info)
    
    def execute_scheduling_request(self, client_interest: str) -> str:
        """Solicitar agendamento usando CrewAI"""
        
        task = Task(
            description=f"""
            O cliente demonstrou interesse: "{client_interest}"

            Crie mensagem para coletar dados de agendamento.

            REGRAS CAROL:
            - Confirmar interesse
            - Perguntar qual imóvel específico
            - Perguntar dia preferido
            - Perguntar horário preferido
            - Máximo 4 linhas
            - SEM emojis
            """,
            agent=self.scheduling_agent,
            expected_output="Mensagem para coleta de dados de agendamento"
        )
        
        try:
            crew = Crew(agents=[self.scheduling_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info("Solicitação de agendamento CrewAI executada")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro no agendamento CrewAI: {e}")
            return "Perfeito. Para agendar preciso saber qual imóvel te interessou, que dia seria melhor e qual horário você prefere."
    
    def execute_closure(self, client_message: str, reason: str = "desinteresse") -> str:
        """Executar encerramento usando CrewAI"""
        
        task = Task(
            description=f"""
            Crie mensagem de encerramento educada e profissional.

            RESPOSTA DO CLIENTE: "{client_message}"
            MOTIVO: {reason}

            REGRAS CAROL:
            - Agradecer o tempo do cliente
            - Ser respeitosa e compreensiva
            - Deixar porta aberta para futuro
            - SEM emojis
            - Máximo 3 linhas
            - Tom profissional mas caloroso
            """,
            agent=self.closure_agent,
            expected_output="Mensagem de encerramento profissional"
        )
        
        try:
            crew = Crew(agents=[self.closure_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            logger.info("Encerramento CrewAI executado")
            return str(result).strip()
            
        except Exception as e:
            logger.error(f"Erro no encerramento CrewAI: {e}")
            return "Compreendo perfeitamente. Agradeço seu tempo e fico à disposição caso precise de ajuda no futuro."
    
    def analyze_client_response(self, client_message: str) -> Dict[str, str]:
        """Analisar resposta do cliente usando CrewAI"""
        
        task = Task(
            description=f"""
            Analise a resposta do cliente: "{client_message}"

            Determine:
            1. Nível de interesse (high/medium/low)
            2. Próxima ação (send_properties/clarify/closure/schedule)
            3. Tipo de resposta (positive/negative/neutral)

            CRITÉRIOS:
            - Positivo: sim, pode, manda, ok, quero, interesse, gostei
            - Negativo: não, sem interesse, muito caro, não tenho
            - Agendamento: visita, agendar, quando, horário

            RESPONDA APENAS: nivel|acao|tipo
            Exemplo: high|send_properties|positive
            """,
            agent=self.contact_agent,
            expected_output="Análise estruturada: nivel|acao|tipo"
        )
        
        try:
            crew = Crew(agents=[self.contact_agent], tasks=[task], verbose=True)
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
        
        # Fallback simples
        return self._simple_analysis(client_message)
    
    def _fallback_initial_contact(self, client_name: str, imobiliaria_nome: str, region: str) -> str:
        """Fallback para primeiro contato"""
        return f"""Boa tarde {client_name}, sou a Corretora Carol da {imobiliaria_nome}.
Vi que você tem interesse em imóveis na região de {region}.
Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
Posso te mandar algumas opções?"""
    
    def _fallback_presentation(self, properties_info: List[str]) -> str:
        """Fallback para apresentação"""
        presentation = ''.join(properties_info)
        presentation += "\nAlgum desses imóveis te interessou?"
        return presentation
    
    def _simple_analysis(self, client_message: str) -> Dict[str, str]:
        """Análise simples de fallback"""
        client_lower = client_message.lower()
        
        if any(word in client_lower for word in ['sim', 'pode', 'manda', 'ok', 'quero', 'interesse']):
            return {'interest_level': 'high', 'next_action': 'send_properties', 'response_type': 'positive'}
        elif any(word in client_lower for word in ['não', 'nao', 'sem interesse', 'muito caro']):
            return {'interest_level': 'low', 'next_action': 'closure', 'response_type': 'negative'}
        elif any(word in client_lower for word in ['visita', 'agendar', 'quando', 'horário']):
            return {'interest_level': 'high', 'next_action': 'schedule', 'response_type': 'positive'}
        else:
            return {'interest_level': 'medium', 'next_action': 'clarify', 'response_type': 'neutral'}
