"""
Endpoints específicos para integração N8N
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from services.session_management.session_manager import SessionManager

router = APIRouter(prefix="/n8n", tags=["N8N Integration"])

session_manager = SessionManager()

@router.get("/status")
async def n8n_integration_status():
    """Status da integração N8N"""
    return {
        "status": "active",
        "service": "n8n_integration",
        "endpoints": {
            "incoming_webhook": "/webhook/n8n/incoming",
            "test_webhook": "/webhook/n8n/test",
            "session_info": "/n8n/session/{session_id}",
            "conversation_history": "/n8n/conversation/{phone}"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/session/{session_id}")
async def get_session_info(session_id: str) -> Dict[str, Any]:
    """Obter informações da sessão"""
    
    session = await session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou expirada"
        )
    
    return {
        "success": True,
        "session": session
    }

@router.get("/conversation/{phone}")
async def get_conversation_history(phone: str, limit: int = 10) -> Dict[str, Any]:
    """Obter histórico de conversas de um telefone"""
    
    from core.database import get_db_session
    from services.session_management.session_manager import ConversationSession
    
    with get_db_session() as db:
        sessions = db.query(ConversationSession).filter_by(
            phone=phone
        ).order_by(ConversationSession.updated_at.desc()).limit(limit).all()
        
        history = [session.to_dict() for session in sessions]
    
    return {
        "success": True,
        "phone": phone,
        "total_sessions": len(history),
        "history": history
    }

@router.post("/session/{session_id}/end")
async def end_session(session_id: str) -> Dict[str, Any]:
    """Finalizar sessão manualmente"""
    
    success = await session_manager.end_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )
    
    return {
        "success": True,
        "message": "Sessão finalizada",
        "session_id": session_id
    }

@router.post("/cleanup-sessions")
async def cleanup_expired_sessions() -> Dict[str, Any]:
    """Limpar sessões expiradas"""
    
    cleaned_count = await session_manager.cleanup_expired_sessions()
    
    return {
        "success": True,
        "cleaned_sessions": cleaned_count,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/simulate-conversation")
async def simulate_conversation(conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simular uma conversa completa para teste"""
    
    phone = conversation_data.get("phone", "5511999999999")
    messages = conversation_data.get("messages", [
        "Olá, gostaria de saber sobre apartamentos",
        "Para compra, 3 quartos",
        "Vila Madalena",
        "Até 500 mil"
    ])
    
    chat_id = f"test_chat_{datetime.now().timestamp()}"
    responses = []
    
    for i, message in enumerate(messages):
        try:
            from services.webhook.n8n_webhook import process_incoming_message
            
            response = await process_incoming_message(
                phone=phone,
                message=message,
                chat_id=chat_id,
                contact_name="Cliente Teste",
                message_type="text"
            )
            
            responses.append({
                "step": i + 1,
                "user_message": message,
                "bot_response": response["response_data"]["message"],
                "intent": response["metadata"]["intent"],
                "confidence": response["metadata"]["confidence"]
            })
            
        except Exception as e:
            responses.append({
                "step": i + 1,
                "user_message": message,
                "error": str(e)
            })
    
    return {
        "success": True,
        "simulation": {
            "phone": phone,
            "chat_id": chat_id,
            "total_messages": len(messages),
            "responses": responses
        }
    }

@router.get("/analytics/conversations")
async def get_conversation_analytics() -> Dict[str, Any]:
    """Analytics das conversas"""
    
    from core.database import get_db_session
    from services.session_management.session_manager import ConversationSession
    from sqlalchemy import func, text
    
    with get_db_session() as db:
        total_sessions = db.query(ConversationSession).count()
        active_sessions = db.query(ConversationSession).filter_by(active=True).count()
        
        stages = db.query(
            ConversationSession.conversation_stage,
            func.count(ConversationSession.id)
        ).group_by(ConversationSession.conversation_stage).all()
        
        intents = db.query(
            ConversationSession.last_intent,
            func.count(ConversationSession.id)
        ).filter(
            ConversationSession.last_intent.isnot(None)
        ).group_by(ConversationSession.last_intent).all()
        
        try:
            daily_sessions = db.execute(text("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM conversation_sessions 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)).fetchall()
        except:
            daily_sessions = []
    
    return {
        "success": True,
        "analytics": {
            "overview": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completion_rate": round((total_sessions - active_sessions) / max(total_sessions, 1) * 100, 2)
            },
            "conversation_stages": [{"stage": stage, "count": count} for stage, count in stages],
            "common_intents": [{"intent": intent, "count": count} for intent, count in intents],
            "daily_activity": [{"date": str(date), "sessions": count} for date, count in daily_sessions]
        },
        "generated_at": datetime.now().isoformat()
    }

# Incluir webhook diretamente aqui
from services.webhook.n8n_webhook import router as webhook_router
router.include_router(webhook_router, prefix="")
