"""
Webhook Receiver para N8N
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional
from datetime import datetime
import json
import uuid

from services.message_processing.message_processor import MessageProcessor
from services.session_management.session_manager import SessionManager
from core.logger import logger

router = APIRouter(prefix="/webhook", tags=["N8N Webhook"])

# Instâncias globais
message_processor = MessageProcessor()
session_manager = SessionManager()

@router.post("/n8n/incoming")
async def receive_n8n_message(request: Request) -> Dict[str, Any]:
    """
    Receber mensagem do N8N e processar
    
    Payload esperado do N8N:
    {
        "phone": "5511999999999",
        "message": "Olá, gostaria de saber sobre apartamentos",
        "message_type": "text",
        "timestamp": "2025-07-30T15:30:00Z",
        "contact_name": "João Silva",
        "chat_id": "whatsapp_chat_123"
    }
    """
    try:
        # Receber payload do N8N
        payload = await request.json()
        
        # Validar payload
        required_fields = ['phone', 'message', 'chat_id']
        for field in required_fields:
            if field not in payload:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo obrigatório '{field}' não encontrado"
                )
        
        # Extrair dados
        phone = payload['phone']
        message = payload['message']
        chat_id = payload['chat_id']
        contact_name = payload.get('contact_name', 'Cliente')
        message_type = payload.get('message_type', 'text')
        
        logger.info(f"📥 Mensagem recebida do N8N - Phone: {phone}, Message: {message[:50]}...")
        
        # Processar mensagem
        response = await process_incoming_message(
            phone=phone,
            message=message,
            chat_id=chat_id,
            contact_name=contact_name,
            message_type=message_type
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook N8N: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

async def process_incoming_message(
    phone: str,
    message: str,
    chat_id: str,
    contact_name: str,
    message_type: str
) -> Dict[str, Any]:
    """
    Processar mensagem recebida e gerar resposta
    """
    
    # 1. Gerenciar sessão
    session = await session_manager.get_or_create_session(
        phone=phone,
        chat_id=chat_id,
        contact_name=contact_name
    )
    
    # 2. Processar mensagem
    processing_result = await message_processor.process_message(
        message=message,
        session=session,
        message_type=message_type
    )
    
    # 3. Atualizar sessão
    await session_manager.update_session(
        session_id=session['id'],
        last_message=message,
        context_update=processing_result.get('context_update', {})
    )
    
    # 4. Formatar resposta para N8N
    response = {
        "success": True,
        "session_id": session['id'],
        "phone": phone,
        "chat_id": chat_id,
        "response_data": {
            "message": processing_result['response_message'],
            "message_type": "text",
            "quick_replies": processing_result.get('quick_replies', []),
            "attachments": processing_result.get('attachments', []),
            "delay_seconds": processing_result.get('delay_seconds', 0)
        },
        "metadata": {
            "intent": processing_result.get('intent', 'unknown'),
            "confidence": processing_result.get('confidence', 0.0),
            "agent_used": processing_result.get('agent_used', 'carol_general'),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    logger.info(f"✅ Resposta gerada para {phone}: {processing_result['response_message'][:50]}...")
    
    return response

@router.get("/n8n/health")
async def webhook_health():
    """Health check para o webhook"""
    return {
        "status": "healthy",
        "service": "n8n_webhook",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/n8n/test")
async def test_webhook(test_data: Dict[str, Any]):
    """Endpoint para testar o webhook"""
    
    # Dados de teste padrão
    default_test = {
        "phone": "5511999999999",
        "message": "Olá, gostaria de saber sobre apartamentos para venda",
        "chat_id": "test_chat_123",
        "contact_name": "Cliente Teste",
        "message_type": "text"
    }
    
    # Usar dados fornecidos ou padrão
    test_payload = {**default_test, **test_data}
    
    # Processar como mensagem normal
    response = await process_incoming_message(**test_payload)
    
    return {
        "test_status": "success",
        "test_payload": test_payload,
        "response": response
    }
