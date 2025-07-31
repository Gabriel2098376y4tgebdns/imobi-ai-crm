"""
Endpoints para sistema de matching geográfico
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from services.matching.geo_matching import (
    executar_matching_automatico,
    buscar_leads_para_imovel,
    GeoMatchingEngine
)

router = APIRouter(prefix="/matching", tags=["Geo Matching"])

@router.post("/executar/{cliente_id}")
async def executar_matching(cliente_id: str) -> Dict[str, Any]:
    """
    Executar matching automático para encontrar imóveis compatíveis com leads ativos
    """
    try:
        resultado = executar_matching_automatico(cliente_id)
        return {
            "status": "success",
            "cliente_id": cliente_id,
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no matching: {str(e)}"
        )

@router.get("/buscar-imoveis-proximos/{cliente_id}")
async def buscar_imoveis_proximos(
    cliente_id: str,
    latitude: float = Query(..., description="Latitude do centro da busca"),
    longitude: float = Query(..., description="Longitude do centro da busca"),
    raio_km: int = Query(3, description="Raio de busca em quilômetros"),
    tipo_operacao: Optional[str] = Query(None, description="Tipo de operação: venda ou locacao"),
    tipo_imovel: Optional[str] = Query(None, description="Tipo de imóvel"),
    quartos_min: Optional[int] = Query(None, description="Número mínimo de quartos"),
    preco_max: Optional[float] = Query(None, description="Preço máximo (venda ou aluguel total)")
) -> Dict[str, Any]:
    """
    Buscar imóveis próximos a uma localização específica
    """
    try:
        engine = GeoMatchingEngine(cliente_id)
        
        # Preparar filtros
        filtros = {}
        if tipo_imovel:
            filtros['tipo_imovel'] = tipo_imovel
        if quartos_min:
            filtros['quartos_min'] = quartos_min
        
        if tipo_operacao == 'venda' and preco_max:
            filtros['preco_max'] = preco_max
        elif tipo_operacao == 'locacao' and preco_max:
            filtros['aluguel_max'] = preco_max
        
        imoveis = engine.buscar_imoveis_proximos(
            lat_centro=latitude,
            lng_centro=longitude,
            raio_km=raio_km,
            tipo_operacao=tipo_operacao,
            filtros_adicionais=filtros
        )
        
        return {
            "status": "success",
            "parametros_busca": {
                "latitude": latitude,
                "longitude": longitude,
                "raio_km": raio_km,
                "tipo_operacao": tipo_operacao,
                "filtros": filtros
            },
            "total_encontrados": len(imoveis),
            "imoveis": imoveis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca: {str(e)}"
        )

@router.get("/leads-para-imovel/{cliente_id}/{imovel_id}")
async def buscar_leads_compativel_imovel(
    cliente_id: str,
    imovel_id: str
) -> Dict[str, Any]:
    """
    Buscar leads compatíveis para um imóvel específico
    """
    try:
        leads = buscar_leads_para_imovel(cliente_id, imovel_id)
        
        return {
            "status": "success",
            "imovel_id": imovel_id,
            "total_leads_compativeis": len(leads),
            "leads": leads
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar leads: {str(e)}"
        )

@router.get("/estatisticas/{cliente_id}")
async def estatisticas_matching(cliente_id: str) -> Dict[str, Any]:
    """
    Estatísticas do sistema de matching
    """
    try:
        from core.database import get_db_session
        from sqlalchemy import text
        
        with get_db_session() as db:
            # Estatísticas de imóveis
            stats_imoveis = db.execute(text("""
                SELECT 
                    tipo_operacao,
                    COUNT(*) as total,
                    COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as com_coordenadas
                FROM imoveis_dual 
                WHERE cliente_id = :cliente_id AND ativo = true
                GROUP BY tipo_operacao
            """), {"cliente_id": cliente_id}).fetchall()
            
            # Estatísticas de leads
            stats_leads = db.execute(text("""
                SELECT 
                    CASE 
                        WHEN interesse_venda AND interesse_locacao THEN 'ambos'
                        WHEN interesse_venda THEN 'venda'
                        WHEN interesse_locacao THEN 'locacao'
                        ELSE 'indefinido'
                    END as tipo_interesse,
                    COUNT(*) as total,
                    COUNT(CASE WHEN latitude_centro IS NOT NULL AND longitude_centro IS NOT NULL THEN 1 END) as com_coordenadas,
                    COUNT(CASE WHEN etapa_crm IN ('visita_agendada', 'visita_realizada', 'proposta_enviada', 'atendimento', 'negociacao') THEN 1 END) as etapas_ativas
                FROM leads_crm 
                WHERE cliente_id = :cliente_id AND ativo = true
                GROUP BY tipo_interesse
            """), {"cliente_id": cliente_id}).fetchall()
            
            # Organizar resultados
            estatisticas_imoveis = {}
            for row in stats_imoveis:
                estatisticas_imoveis[row[0]] = {
                    "total": row[1],
                    "com_coordenadas": row[2],
                    "percentual_geolocalizados": round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0
                }
            
            estatisticas_leads = {}
            for row in stats_leads:
                estatisticas_leads[row[0]] = {
                    "total": row[1],
                    "com_coordenadas": row[2],
                    "etapas_ativas": row[3],
                    "percentual_geolocalizados": round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0
                }
            
            return {
                "status": "success",
                "cliente_id": cliente_id,
                "imoveis": estatisticas_imoveis,
                "leads": estatisticas_leads,
                "sistema_matching": {
                    "ativo": True,
                    "raio_padrao_km": 3,
                    "score_minimo": 50
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar estatísticas: {str(e)}"
        )

@router.post("/teste-matching")
async def teste_matching() -> Dict[str, Any]:
    """
    Teste do sistema de matching com dados de exemplo
    """
    try:
        # Executar matching para cliente teste
        resultado = executar_matching_automatico('teste_local')
        
        return {
            "status": "success",
            "message": "Teste de matching executado",
            "resultado": resultado
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )
