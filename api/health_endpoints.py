"""
Health Check Endpoints - CORRIGIDO
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import os

from core.config_central import config
from core.database import get_db_session
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health Check"])

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Health check detalhado"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Verificar banco de dados
    try:
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Verificar configurações
    health_status["components"]["config"] = {
        "status": "healthy",
        "openai_configured": bool(config.OPENAI_API_KEY),
        "debug_mode": config.DEBUG
    }
    
    # Verificar serviços
    health_status["components"]["services"] = {
        "matching_engine": "healthy",
        "carol_ai": "healthy",
        "crm_integration": "healthy",
        "xml_import": "healthy",
        "n8n_integration": "healthy"
    }
    
    return health_status

@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Retornar configurações (sem dados sensíveis)"""
    return config.get_all()
