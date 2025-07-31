"""
Agent Carol - Corretora de Primeiro Contato
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from core.logger import logger
from typing import Dict, List, Any
from datetime import datetime


class CarolContactAgent:
    """
    Corretora Carol - 36 anos, 15 anos de experiência
    Profissional, direta, sem gírias, textos curtos, sem emojis
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.3  # Baixa temperatura para respostas mais consistentes
        )
        
        self.agent = Agent(
            role="Corretora Imobiliária Sênior",
            goal="Fazer primeiro contato profissional e agendar visitas de imóveis",
            backstory="""
            Você é a Carol, uma corretora imobiliária com 36 anos e 15 anos de experiência no mercado.
            
            PERSONALIDADE:
            - Muito profissional e experiente
            - Comunicação direta e objetiva
            - Não usa gírias ou linguagem informal
            - Não usa emojis
            - Textos curtos e diretos
            - Analisa bem as mensagens antes de responder
            - Linguagem profissional adaptada para WhatsApp
            
            COMPORTAMENTO:
            - Sempre se apresenta como "Corretora Carol"
            - Menciona o nome da imobiliária
            - É direta ao ponto
            - Foca no que o cliente precisa
            - Confirma informações antes de prosseguir
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_initial_contact(self, lead_data: Dict, matched_properties: List, imobiliaria_nome: str) -> str:
        """Criar mensagem de primeiro contato"""
        
        client_name = lead_data.get('nome', 'Cliente')
        region = ', '.join(lead_data.get('cidades_interesse', ['região de interesse']))
        property_type = lead_data.get('tipo_imovel', 'imóvel')
        
        prompt = f"""
        Crie uma mensagem de primeiro contato para WhatsApp seguindo EXATAMENTE este roteiro:

        DADOS:
        - Cliente: {client_name}
        - Imobiliária: {imobiliaria_nome}
        - Região de interesse: {region}
        - Tipo de imóvel: {property_type}
        - Quantidade de matches encontrados: {len(matched_properties)}

        ROTEIRO OBRIGATÓRIO:
        1. Se apresentar como Corretora Carol
        2. Mencionar o nome da imobiliária: {imobiliaria_nome}
        3. Dizer que a pessoa entrou em contato interessada em imóveis na região {region}
        4. Informar que acabamos de cadastrar novos produtos que se enquadram no que ela busca
        5. Perguntar: "Posso te mandar algumas opções?"

        REGRAS CAROL:
        - Linguagem profissional mas adequada para WhatsApp
        - Textos curtos e diretos
        - SEM emojis
        - SEM gírias
        - SEM "olá" ou cumprimentos informais
        - Máximo 4 linhas

        FORMATO: Apenas a mensagem, sem aspas ou formatação extra.
        """
        
        try:
            from crewai import Task
            
            task = Task(
                description=prompt,
                agent=self.agent,
                expected_output="Mensagem de primeiro contato profissional"
            )
            
            message = task.execute()
            logger.info(f"Mensagem inicial criada para {client_name}")
            return message.strip()
            
        except Exception as e:
            logger.error(f"Erro ao criar mensagem inicial: {e}")
            return self._fallback_initial_message(client_name, imobiliaria_nome, region)
    
    def create_properties_presentation(self, matched_properties: List[Dict]) -> str:
        """Apresentar todos os imóveis que deram match"""
        
        prompt = f"""
        Apresente os imóveis de forma profissional e objetiva para WhatsApp.

        IMÓVEIS ENCONTRADOS ({len(matched_properties)} opções):
        {self._format_properties_for_prompt(matched_properties)}

        REGRAS CAROL:
        - Apresentar TODOS os imóveis de forma objetiva
        - Uma linha por imóvel com informações principais
        - Linguagem profissional
        - SEM emojis
        - Ao final perguntar: "Algum desses imóveis te interessou?"

        FORMATO: Lista dos imóveis + pergunta final
        """
        
        try:
            from crewai import Task
            
            task = Task(
                description=prompt,
                agent=self.agent,
                expected_output="Apresentação objetiva dos imóveis"
            )
            
            message = task.execute()
            logger.info(f"Apresentação de {len(matched_properties)} imóveis criada")
            return message.strip()
            
        except Exception as e:
            logger.error(f"Erro ao criar apresentação: {e}")
            return self._fallback_properties_presentation(matched_properties)
    
    def create_scheduling_message(self, client_response: str) -> str:
        """Criar mensagem para agendamento de visita"""
        
        prompt = f"""
        O cliente respondeu: "{client_response}"

        Se o cliente demonstrou interesse, crie uma mensagem para agendar visita seguindo:

        REGRAS CAROL:
        - Confirmar interesse
        - Perguntar dia, horário e qual imóvel específico
        - Ser direta e objetiva
        - SEM emojis
        - Máximo 3 linhas

        Se não ficou claro o interesse, peça esclarecimento.

        FORMATO: Apenas a mensagem de agendamento
        """
        
        try:
            from crewai import Task
            
            task = Task(
                description=prompt,
                agent=self.agent,
                expected_output="Mensagem de agendamento"
            )
            
            message = task.execute()
            logger.info("Mensagem de agendamento criada")
            return message.strip()
            
        except Exception as e:
            logger.error(f"Erro ao criar mensagem de agendamento: {e}")
            return "Perfeito. Para agendar a visita preciso saber qual imóvel te interessou, que dia e horário seria melhor para você."
    
    def _format_properties_for_prompt(self, properties: List[Dict]) -> str:
        """Formatar imóveis para o prompt"""
        formatted = []
        for i, prop in enumerate(properties, 1):
            formatted.append(f"""
            Imóvel {i}:
            - Título: {prop.get('titulo')}
            - Tipo: {prop.get('tipo')}
            - Preço: R\$ {prop.get('preco', 0):,.2f}
            - Endereço: {prop.get('endereco')}
            - Quartos: {prop.get('quartos')}
            - Área: {prop.get('area_total')} m²
            """)
        return "\n".join(formatted)
    
    def _fallback_initial_message(self, client_name: str, imobiliaria_nome: str, region: str) -> str:
        """Mensagem de fallback para primeiro contato"""
        return f"""Boa tarde {client_name}, sou a Corretora Carol da {imobiliaria_nome}.
Vi que você tem interesse em imóveis na região de {region}.
Acabamos de cadastrar alguns produtos que se enquadram no seu perfil.
Posso te mandar algumas opções?"""
    
    def _fallback_properties_presentation(self, properties: List[Dict]) -> str:
        """Apresentação de fallback dos imóveis"""
        presentation = []
        for i, prop in enumerate(properties, 1):
            presentation.append(f"{i}. {prop.get('titulo')} - R\$ {prop.get('preco', 0):,.2f} - {prop.get('endereco')}")
        
        presentation.append("\nAlgum desses imóveis te interessou?")
        return "\n".join(presentation)
