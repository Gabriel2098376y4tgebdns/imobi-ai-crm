"""
Carol AI - Agente Inteligente para Contatos Automáticos
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from core.database import get_db_session
from models.lead_crm_integrado import LeadCRMIntegrado
from models.tipos_garantia import TipoGarantia


class CarolAI:
    """
    Carol - Agente de IA especializado em imóveis
    """
    
    def __init__(self, cliente_id: str):
        self.cliente_id = cliente_id
        self.openai_client = None
        
        # Configurar OpenAI se disponível
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Base de conhecimento sobre garantias
        self.garantias_info = self._carregar_garantias()
    
    def _carregar_garantias(self) -> Dict[str, Any]:
        """Carregar informações sobre garantias"""
        with get_db_session() as db:
            garantias = db.query(TipoGarantia).filter_by(ativo=True).all()
            return {g.nome: g.to_dict() for g in garantias}
    
    def criar_mensagem_novo_imovel(
        self, 
        lead_data: Dict[str, Any], 
        imoveis_matches: List[Dict[str, Any]],
        imobiliaria_nome: str = "Nossa Imobiliária"
    ) -> str:
        """
        Criar mensagem personalizada para novos imóveis
        """
        
        if self.openai_client:
            return self._criar_mensagem_com_ia(lead_data, imoveis_matches, imobiliaria_nome)
        else:
            return self._criar_mensagem_template(lead_data, imoveis_matches, imobiliaria_nome)
    
    def _criar_mensagem_com_ia(
        self, 
        lead_data: Dict[str, Any], 
        imoveis_matches: List[Dict[str, Any]],
        imobiliaria_nome: str
    ) -> str:
        """
        Criar mensagem usando IA (OpenAI)
        """
        
        # Preparar contexto para a IA
        contexto = self._preparar_contexto_ia(lead_data, imoveis_matches, imobiliaria_nome)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é a Carol, uma corretora de imóveis experiente e amigável. 
                        
CARACTERÍSTICAS DA CAROL:
- 36 anos, 15 anos de experiência no mercado imobiliário
- Comunicação natural e profissional
- Foca em resolver necessidades do cliente
- Conhece bem o mercado de São Paulo
- Especialista em vendas e locação

INSTRUÇÕES PARA MENSAGENS:
1. Use linguagem natural e amigável
2. Seja direta e objetiva
3. Destaque os pontos fortes dos imóveis
4. Inclua valores e características principais
5. Termine sempre perguntando sobre interesse em visita
6. Use emojis moderadamente (máximo 3 por mensagem)
7. Mantenha tom profissional mas caloroso
8. Não use linguagem muito formal ou robótica

FORMATO DA MENSAGEM:
- Cumprimento personalizado
- Referência ao interesse do cliente
- Apresentação dos imóveis (máximo 3)
- Call to action para visita
- Assinatura da Carol"""
                    },
                    {
                        "role": "user",
                        "content": contexto
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            mensagem = response.choices[0].message.content.strip()
            return mensagem
            
        except Exception as e:
            print(f"❌ Erro ao gerar mensagem com IA: {e}")
            return self._criar_mensagem_template(lead_data, imoveis_matches, imobiliaria_nome)
    
    def _preparar_contexto_ia(
        self, 
        lead_data: Dict[str, Any], 
        imoveis_matches: List[Dict[str, Any]],
        imobiliaria_nome: str
    ) -> str:
        """
        Preparar contexto para a IA
        """
        
        # Informações do lead
        nome = lead_data.get('nome', 'Cliente')
        operacao = lead_data.get('operacao_principal', 'indefinido')
        etapa = lead_data.get('etapa_crm', 'atendimento')
        
        # Determinar tipo de interesse
        if operacao == 'venda':
            tipo_interesse = 'compra de imóvel'
        elif operacao == 'locacao':
            tipo_interesse = 'locação de imóvel'
        else:
            tipo_interesse = 'imóvel (compra ou locação)'
        
        # Preparar informações dos imóveis
        imoveis_info = []
        for i, imovel in enumerate(imoveis_matches[:3], 1):  # Máximo 3 imóveis
            info = f"\nIMÓVEL {i}:"
            info += f"\n- Título: {imovel.get('titulo')}"
            info += f"\n- Tipo: {imovel.get('tipo_imovel')} com {imovel.get('quartos')} quartos"
            info += f"\n- Localização: {imovel.get('bairro')}, {imovel.get('cidade')}"
            info += f"\n- Distância: {imovel.get('distancia_km', 0):.1f}km do local preferido"
            info += f"\n- Score de compatibilidade: {imovel.get('score_compatibilidade', 0):.0f}%"
            
            if imovel.get('tipo_operacao') == 'venda':
                preco = imovel.get('preco_venda', 0)
                info += f"\n- Preço: R\$ {preco:,.2f}".replace(',', '.')
            else:
                aluguel = imovel.get('valor_aluguel', 0)
                condominio = imovel.get('valor_condominio', 0)
                total = imovel.get('valor_total_mensal', 0)
                info += f"\n- Aluguel: R\$ {aluguel:,.2f}/mês".replace(',', '.')
                if condominio > 0:
                    info += f"\n- Condomínio: R\$ {condominio:,.2f}/mês".replace(',', '.')
                info += f"\n- Total mensal: R\$ {total:,.2f}".replace(',', '.')
            
            info += f"\n- Link da galeria: {imovel.get('galeria_url', '#')}"
            imoveis_info.append(info)
        
        contexto = f"""SITUAÇÃO:
Entraram novos imóveis no portfólio da {imobiliaria_nome} que fazem match com o perfil do cliente.

INFORMAÇÕES DO CLIENTE:
- Nome: {nome}
- Interesse: {tipo_interesse}
- Etapa atual: {etapa}
- Bairros de interesse: {', '.join(lead_data.get('bairros_interesse', []))}

IMÓVEIS ENCONTRADOS ({len(imoveis_matches)} matches):
{''.join(imoveis_info)}

TAREFA:
Crie uma mensagem da Carol informando sobre esses novos imóveis que entraram no portfólio.
A mensagem deve:
1. Ser personalizada para o {nome}
2. Mencionar que são novos imóveis que chegaram
3. Apresentar os imóveis de forma atrativa
4. Perguntar se o cliente gostaria de agendar visitas
5. Manter tom profissional mas amigável

Limite: máximo 300 palavras."""
        
        return contexto
    
    def _criar_mensagem_template(
        self, 
        lead_data: Dict[str, Any], 
        imoveis_matches: List[Dict[str, Any]],
        imobiliaria_nome: str
    ) -> str:
        """
        Criar mensagem usando template (fallback)
        """
        
        nome = lead_data.get('nome', 'Cliente')
        operacao = lead_data.get('operacao_principal', 'indefinido')
        
        # Determinar saudação baseada na operação
        if operacao == 'venda':
            interesse_texto = "para compra"
        elif operacao == 'locacao':
            interesse_texto = "para locação"
        else:
            interesse_texto = "que podem te interessar"
        
        # Início da mensagem
        mensagem = f"Boa tarde {nome}! Sou a Carol da {imobiliaria_nome}. 😊\n\n"
        mensagem += f"Entraram alguns imóveis novos no nosso portfólio {interesse_texto} "
        mensagem += f"na região que você busca.\n\n"
        
        # Apresentar imóveis (máximo 3)
        for i, imovel in enumerate(imoveis_matches[:3], 1):
            mensagem += f"🏠 *OPÇÃO {i}:*\n"
            mensagem += f"📍 {imovel.get('titulo')}\n"
            mensagem += f"📌 {imovel.get('bairro')} - {imovel.get('quartos')} quartos\n"
            
            if imovel.get('tipo_operacao') == 'venda':
                preco = imovel.get('preco_venda', 0)
                mensagem += f"💰 R\$ {preco:,.2f}\n".replace(',', '.')
            else:
                total = imovel.get('valor_total_mensal', 0)
                mensagem += f"💰 R\$ {total:,.2f}/mês (total)\n".replace(',', '.')
            
            mensagem += f"📸 Ver fotos: {imovel.get('galeria_url', '#')}\n\n"
        
        # Finalização
        if len(imoveis_matches) > 3:
            mensagem += f"E mais {len(imoveis_matches) - 3} opções disponíveis!\n\n"
        
        mensagem += "Gostaria de agendar uma visita para conhecer algum deles? 🗓️\n\n"
        mensagem += "Estou aqui para ajudar!\n"
        mensagem += "*Carol - Corretora*"
        
        return mensagem
    
    def responder_duvida_garantia(self, tipo_garantia: str) -> str:
        """
        Responder dúvidas sobre tipos de garantia
        """
        
        tipo_garantia_clean = tipo_garantia.lower().strip()
        
        # Buscar garantia na base de conhecimento
        garantia_encontrada = None
        for nome, info in self.garantias_info.items():
            if tipo_garantia_clean in nome.lower():
                garantia_encontrada = info
                break
        
        if not garantia_encontrada:
            return self._resposta_garantia_generica()
        
        if self.openai_client:
            return self._responder_garantia_com_ia(garantia_encontrada)
        else:
            return self._responder_garantia_template(garantia_encontrada)
    
    def _responder_garantia_com_ia(self, garantia_info: Dict[str, Any]) -> str:
        """
        Responder sobre garantia usando IA
        """
        
        contexto = f"""INFORMAÇÕES SOBRE {garantia_info['nome']}:

DESCRIÇÃO: {garantia_info['descricao_completa']}

COMO FUNCIONA: {garantia_info['como_funciona']}

DOCUMENTOS NECESSÁRIOS:
{chr(10).join(['- ' + doc for doc in garantia_info.get('documentos_necessarios', [])])}

TEMPO DE APROVAÇÃO: {garantia_info.get('tempo_aprovacao', 'Não informado')}

CUSTO: {garantia_info.get('custo_aproximado', 'Não informado')}

RENDA MÍNIMA: {garantia_info.get('renda_minima_exigida', 'Não informado')}

VANTAGENS:
{chr(10).join(['- ' + vant for vant in garantia_info.get('vantagens', [])])}

DESVANTAGENS:
{chr(10).join(['- ' + desv for desv in garantia_info.get('desvantagens', [])])}

TAREFA: Explique essa garantia de forma clara e amigável, como a Carol faria."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é a Carol, corretora experiente. Explique tipos de garantia de forma:
                        - Clara e didática
                        - Amigável mas profissional  
                        - Destacando prós e contras
                        - Terminando perguntando se quer agendar visita"""
                    },
                    {
                        "role": "user",
                        "content": contexto
                    }
                ],
                max_tokens=400,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Erro ao responder garantia com IA: {e}")
            return self._responder_garantia_template(garantia_info)
    
    def _responder_garantia_template(self, garantia_info: Dict[str, Any]) -> str:
        """
        Responder sobre garantia usando template
        """
        
        resposta = f"📋 *{garantia_info['nome']}*\n\n"
        resposta += f"{garantia_info['descricao_completa']}\n\n"
        resposta += f"🔧 *Como funciona:*\n{garantia_info['como_funciona']}\n\n"
        
        if garantia_info.get('documentos_necessarios'):
            resposta += f"📄 *Documentos necessários:*\n"
            for doc in garantia_info['documentos_necessarios']:
                resposta += f"• {doc}\n"
            resposta += "\n"
        
        resposta += f"⏱️ *Tempo de aprovação:* {garantia_info.get('tempo_aprovacao', 'Consultar')}\n"
        resposta += f"💰 *Custo:* {garantia_info.get('custo_aproximado', 'Consultar')}\n\n"
        
        resposta += "Gostaria de agendar uma visita para conhecer o imóvel? 😊\n\n"
        resposta += "*Carol - Corretora*"
        
        return resposta
    
    def _resposta_garantia_generica(self) -> str:
        """
        Resposta genérica sobre garantias
        """
        
        resposta = "📋 *Tipos de Garantia Disponíveis:*\n\n"
        
        for nome, info in self.garantias_info.items():
            resposta += f"🔸 *{nome}*\n"
            resposta += f"   {info.get('descricao_curta', '')}\n\n"
        
        resposta += "Qual tipo de garantia você gostaria de saber mais detalhes?\n\n"
        resposta += "*Carol - Corretora*"
        
        return resposta
    
    def criar_mensagem_followup(
        self, 
        lead_data: Dict[str, Any], 
        contexto_anterior: str = ""
    ) -> str:
        """
        Criar mensagem de follow-up
        """
        
        nome = lead_data.get('nome', 'Cliente')
        etapa = lead_data.get('etapa_crm', 'atendimento')
        
        if etapa == 'visita_agendada':
            return f"Oi {nome}! Lembrete da sua visita agendada. Está confirmada? 😊"
        elif etapa == 'visita_realizada':
            return f"Oi {nome}! Como foi a visita? Ficou alguma dúvida sobre o imóvel? 🏠"
        elif etapa == 'proposta_enviada':
            return f"Oi {nome}! Conseguiu analisar a proposta? Posso esclarecer alguma dúvida? 📋"
        else:
            return f"Oi {nome}! Como posso ajudar você hoje? 😊"


# FUNÇÕES UTILITÁRIAS

def enviar_mensagem_novos_imoveis(
    cliente_id: str,
    lead_data: Dict[str, Any],
    imoveis_matches: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Enviar mensagem sobre novos imóveis para um lead
    """
    
    carol = CarolAI(cliente_id)
    
    # Criar mensagem personalizada
    mensagem = carol.criar_mensagem_novo_imovel(
        lead_data=lead_data,
        imoveis_matches=imoveis_matches,
        imobiliaria_nome="Imobiliária Teste"
    )
    
    # Aqui seria integrado com WhatsApp Business API
    # Por enquanto, apenas simular o envio
    
    resultado = {
        "lead_id": lead_data.get('id'),
        "lead_nome": lead_data.get('nome'),
        "telefone": lead_data.get('telefone'),
        "mensagem_enviada": mensagem,
        "imoveis_apresentados": len(imoveis_matches),
        "timestamp": datetime.now().isoformat(),
        "status_envio": "simulado",  # Em produção seria "enviado" ou "erro"
        "canal": "whatsapp"
    }
    
    print(f"📱 Mensagem enviada para {lead_data.get('nome')} ({lead_data.get('telefone')})")
    print(f"📝 Mensagem: {mensagem[:100]}...")
    
    return resultado


def processar_resposta_lead(
    cliente_id: str,
    lead_telefone: str,
    mensagem_recebida: str
) -> Dict[str, Any]:
    """
    Processar resposta do lead e gerar resposta da Carol
    """
    
    carol = CarolAI(cliente_id)
    
    # Buscar lead no banco
    with get_db_session() as db:
        lead = db.query(LeadCRMIntegrado).filter_by(
            cliente_id=cliente_id,
            telefone=lead_telefone
        ).first()
        
        if not lead:
            return {"erro": "Lead não encontrado"}
        
        lead_data = lead.to_dict()
    
    # Detectar tipo de pergunta
    mensagem_lower = mensagem_recebida.lower()
    
    resposta = ""
    tipo_resposta = "geral"
    
    # Verificar se é pergunta sobre garantia
    palavras_garantia = ['garantia', 'fiador', 'seguro', 'fiança', 'capitalização', 'credito']
    if any(palavra in mensagem_lower for palavra in palavras_garantia):
        # Detectar tipo específico de garantia
        if 'fiador' in mensagem_lower:
            resposta = carol.responder_duvida_garantia('Fiador')
            tipo_resposta = "garantia_fiador"
        elif 'seguro' in mensagem_lower or 'fiança' in mensagem_lower:
            resposta = carol.responder_duvida_garantia('Seguro Fiança')
            tipo_resposta = "garantia_seguro"
        elif 'capitalização' in mensagem_lower:
            resposta = carol.responder_duvida_garantia('Título de Capitalização')
            tipo_resposta = "garantia_capitalizacao"
        elif 'credito' in mensagem_lower:
            resposta = carol.responder_duvida_garantia('Crédito Pago')
            tipo_resposta = "garantia_credito"
        else:
            resposta = carol._resposta_garantia_generica()
            tipo_resposta = "garantia_geral"
    
    # Verificar se é interesse em visita
    elif any(palavra in mensagem_lower for palavra in ['visita', 'agendar', 'conhecer', 'ver']):
        resposta = f"Perfeito {lead_data.get('nome')}! Vou verificar a agenda e te passo os horários disponíveis. Qual período prefere: manhã ou tarde? 📅"
        tipo_resposta = "agendamento"
    
    # Resposta genérica
    else:
        resposta = carol.criar_mensagem_followup(lead_data, mensagem_recebida)
        tipo_resposta = "followup"
    
    return {
        "lead_id": str(lead.id),
        "lead_nome": lead.nome,
        "mensagem_recebida": mensagem_recebida,
        "resposta_carol": resposta,
        "tipo_resposta": tipo_resposta,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Teste da Carol
    carol = CarolAI('teste_local')
    
    # Dados de teste
    lead_teste = {
        'id': 'test-123',
        'nome': 'João Silva',
        'telefone': '11999999999',
        'operacao_principal': 'venda',
        'etapa_crm': 'atendimento',
        'bairros_interesse': ['Vila Madalena', 'Pinheiros']
    }
    
    imoveis_teste = [
        {
            'titulo': 'Apartamento 3 quartos Vila Madalena',
            'tipo_imovel': 'apartamento',
            'quartos': 3,
            'bairro': 'Vila Madalena',
            'cidade': 'São Paulo',
            'tipo_operacao': 'venda',
            'preco_venda': 450000,
            'distancia_km': 0.8,
            'score_compatibilidade': 85,
            'galeria_url': '/galeria/teste/123'
        }
    ]
    
    # Testar criação de mensagem
    mensagem = carol.criar_mensagem_novo_imovel(lead_teste, imoveis_teste)
    print("Mensagem gerada:")
    print(mensagem)
