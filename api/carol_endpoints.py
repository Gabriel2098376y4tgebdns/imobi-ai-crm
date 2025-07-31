"""
Endpoints para Carol AI
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from services.ai_agents.agents.carol_ai import (
    enviar_mensagem_novos_imoveis,
    processar_resposta_lead,
    CarolAI
)

router = APIRouter(prefix="/carol", tags=["Carol AI"])

class MensagemNovoImovel(BaseModel):
    lead_data: Dict[str, Any]
    imoveis_matches: List[Dict[str, Any]]

class RespostaLead(BaseModel):
    telefone: str
    mensagem: str

@router.post("/enviar-novos-imoveis/{cliente_id}")
async def enviar_mensagem_imoveis(
    cliente_id: str,
    dados: MensagemNovoImovel
) -> Dict[str, Any]:
    """
    Enviar mensagem sobre novos imóveis para um lead
    """
    try:
        resultado = enviar_mensagem_novos_imoveis(
            cliente_id=cliente_id,
            lead_data=dados.lead_data,
            imoveis_matches=dados.imoveis_matches
        )
        
        return {
            "status": "success",
            "resultado": resultado
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

@router.post("/processar-resposta/{cliente_id}")
async def processar_resposta(
    cliente_id: str,
    dados: RespostaLead
) -> Dict[str, Any]:
    """
    Processar resposta do lead e gerar resposta da Carol
    """
    try:
        resultado = processar_resposta_lead(
            cliente_id=cliente_id,
            lead_telefone=dados.telefone,
            mensagem_recebida=dados.mensagem
        )
        
        return {
            "status": "success",
            "resultado": resultado
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar resposta: {str(e)}"
        )

@router.get("/garantias")
async def listar_garantias() -> Dict[str, Any]:
    """
    Listar tipos de garantia disponíveis
    """
    try:
        carol = CarolAI('teste_local')
        return {
            "status": "success",
            "garantias": carol.garantias_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar garantias: {str(e)}"
        )

@router.post("/responder-garantia/{cliente_id}")
async def responder_garantia(
    cliente_id: str,
    tipo_garantia: str
) -> Dict[str, Any]:
    """
    Responder dúvida sobre tipo de garantia
    """
    try:
        carol = CarolAI(cliente_id)
        resposta = carol.responder_duvida_garantia(tipo_garantia)
        
        return {
            "status": "success",
            "tipo_garantia": tipo_garantia,
            "resposta": resposta
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao responder garantia: {str(e)}"
        )

@router.post("/teste-carol")
async def teste_carol_completo() -> Dict[str, Any]:
    """
    Teste completo da Carol AI
    """
    try:
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
            },
            {
                'titulo': 'Casa 4 quartos Pinheiros',
                'tipo_imovel': 'casa',
                'quartos': 4,
                'bairro': 'Pinheiros',
                'cidade': 'São Paulo',
                'tipo_operacao': 'locacao',
                'valor_aluguel': 3500,
                'valor_condominio': 450,
                'valor_total_mensal': 3950,
                'distancia_km': 1.2,
                'score_compatibilidade': 78,
                'galeria_url': '/galeria/teste/456'
            }
        ]
        
        # Testar envio de mensagem
        resultado_envio = enviar_mensagem_novos_imoveis(
            cliente_id='teste_local',
            lead_data=lead_teste,
            imoveis_matches=imoveis_teste
        )
        
        # Testar resposta sobre garantia
        carol = CarolAI('teste_local')
        resposta_garantia = carol.responder_duvida_garantia('Seguro Fiança')
        
        # Testar processamento de resposta
        resultado_resposta = processar_resposta_lead(
            cliente_id='teste_local',
            lead_telefone='11999999999',
            mensagem_recebida='Gostaria de saber sobre seguro fiança'
        )
        
        return {
            "status": "success",
            "message": "Teste completo da Carol executado",
            "testes": {
                "envio_mensagem": resultado_envio,
                "resposta_garantia": resposta_garantia,
                "processamento_resposta": resultado_resposta
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )

@router.get("/status")
async def status_carol() -> Dict[str, Any]:
    """
    Status da Carol AI
    """
    import os
    
    openai_configurado = bool(os.getenv('OPENAI_API_KEY'))
    
    return {
        "status": "online",
        "carol_version": "1.0.0",
        "ia_disponivel": openai_configurado,
        "funcionalidades": {
            "mensagens_novos_imoveis": "✅ Ativo",
            "resposta_garantias": "✅ Ativo", 
            "followup_automatico": "✅ Ativo",
            "processamento_ia": "✅ Ativo" if openai_configurado else "⚠️ Configurar OPENAI_API_KEY"
        }
    }
