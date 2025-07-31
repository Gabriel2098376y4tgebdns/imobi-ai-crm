"""
Endpoints para integração com CRM
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from services.crm_integration.crm_connector import (
    sincronizar_crm_cliente,
    verificar_leads_prontos_matching
)

router = APIRouter(prefix="/crm", tags=["CRM Integration"])

@router.post("/sincronizar/{cliente_id}")
async def sincronizar_crm(
    cliente_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Sincronizar leads do CRM externo
    """
    try:
        # Executar sincronização em background
        background_tasks.add_task(sincronizar_crm_cliente, cliente_id)
        
        return {
            "status": "success",
            "message": "Sincronização CRM iniciada",
            "cliente_id": cliente_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na sincronização: {str(e)}"
        )

@router.post("/sincronizar-teste")
async def sincronizar_crm_teste() -> Dict[str, Any]:
    """
    Sincronizar CRM de teste (síncrono para demonstração)
    """
    try:
        resultado = sincronizar_crm_cliente('teste_local')
        return {
            "status": "success",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na sincronização: {str(e)}"
        )

@router.get("/leads-prontos/{cliente_id}")
async def leads_prontos_matching(cliente_id: str) -> Dict[str, Any]:
    """
    Verificar leads prontos para matching
    """
    try:
        resultado = verificar_leads_prontos_matching(cliente_id)
        return {
            "status": "success",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar leads: {str(e)}"
        )

@router.get("/estatisticas/{cliente_id}")
async def estatisticas_crm(cliente_id: str) -> Dict[str, Any]:
    """
    Estatísticas da integração CRM
    """
    try:
        from core.database import get_db_session
        from sqlalchemy import text
        
        with get_db_session() as db:
            # Estatísticas por etapa
            stats_etapas = db.execute(text("""
                SELECT 
                    etapa_crm,
                    COUNT(*) as total,
                    COUNT(CASE WHEN latitude_centro IS NOT NULL THEN 1 END) as com_coordenadas
                FROM leads_crm 
                WHERE cliente_id = :cliente_id AND ativo = true
                GROUP BY etapa_crm
                ORDER BY total DESC
            """), {"cliente_id": cliente_id}).fetchall()
            
            # Estatísticas por operação
            stats_operacao = db.execute(text("""
                SELECT 
                    operacao_principal,
                    COUNT(*) as total,
                    COUNT(CASE WHEN etapa_crm IN ('visita_agendada', 'visita_realizada', 'proposta_enviada', 'atendimento', 'negociacao') THEN 1 END) as prontos_matching
                FROM leads_crm 
                WHERE cliente_id = :cliente_id AND ativo = true
                GROUP BY operacao_principal
            """), {"cliente_id": cliente_id}).fetchall()
            
            # Organizar resultados
            etapas = {}
            for row in stats_etapas:
                etapas[row[0] or 'indefinido'] = {
                    "total": row[1],
                    "com_coordenadas": row[2],
                    "percentual_geolocalizados": round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0
                }
            
            operacoes = {}
            for row in stats_operacao:
                operacoes[row[0] or 'indefinido'] = {
                    "total": row[1],
                    "prontos_matching": row[2]
                }
            
            return {
                "status": "success",
                "cliente_id": cliente_id,
                "etapas": etapas,
                "operacoes": operacoes,
                "integracao_ativa": True
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar estatísticas: {str(e)}"
        )

@router.post("/teste-completo")
async def teste_integracao_completa() -> Dict[str, Any]:
    """
    Teste completo: CRM + Matching
    """
    try:
        # 1. Sincronizar CRM
        print("🔄 Sincronizando CRM...")
        resultado_crm = sincronizar_crm_cliente('teste_local')
        
        # 2. Executar matching
        print("🎯 Executando matching...")
        from services.matching.geo_matching import executar_matching_automatico
        resultado_matching = executar_matching_automatico('teste_local')
        
        return {
            "status": "success",
            "message": "Teste completo executado",
            "crm_sincronizacao": resultado_crm,
            "matching_resultado": resultado_matching
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )
