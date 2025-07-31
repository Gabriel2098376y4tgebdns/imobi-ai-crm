"""
Endpoints para automação diária
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.automation.daily_automation import (
    executar_rotina_diaria,
    verificar_novos_imoveis_para_leads
)

router = APIRouter(prefix="/automation", tags=["Automation"])

@router.post("/rotina-diaria/{cliente_id}")
async def executar_rotina(cliente_id: str) -> Dict[str, Any]:
    """
    Executar rotina diária completa
    """
    try:
        resultado = executar_rotina_diaria(cliente_id)
        return {
            "status": "success",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na rotina: {str(e)}"
        )

@router.post("/verificar-novos-imoveis/{cliente_id}")
async def verificar_novos_imoveis(cliente_id: str) -> Dict[str, Any]:
    """
    Verificar novos imóveis para leads existentes
    """
    try:
        resultado = verificar_novos_imoveis_para_leads(cliente_id)
        return {
            "status": "success",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação: {str(e)}"
        )

@router.post("/teste-rotina")
async def teste_rotina_completa() -> Dict[str, Any]:
    """
    Teste da rotina diária completa
    """
    try:
        resultado = executar_rotina_diaria('teste_local')
        return {
            "status": "success",
            "message": "Rotina diária testada com sucesso",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )
