"""
Aplicação Principal - Railway Deploy
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime

# Importar módulos do sistema
from core.supabase_config import get_supabase_client
from services.message_processing.message_processor import MessageProcessor

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Imobiliário AI",
    description="Sistema de IA para atendimento imobiliário com N8N e Supabase",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar processador de mensagens
message_processor = MessageProcessor()

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema Imobiliário AI - Funcionando!",
        "status": "online",
        "version": "1.0.0",
        "database": "supabase",
        "ai": "openai",
        "platform": "railway"
    }

@app.get("/health/")
async def health_check():
    """Health check completo"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "disconnected",
        "ai_processor": "offline",
        "services": {}
    }
    
    # Testar Supabase
    try:
        client = get_supabase_client()
        if client:
            result = client.table('conversation_sessions').select('*').limit(1).execute()
            health_status["database"] = "connected"
            health_status["services"]["supabase"] = "ok"
        else:
            health_status["services"]["supabase"] = "client_error"
    except Exception as e:
        health_status["services"]["supabase"] = f"error: {str(e)}"
    
    # Testar processador de mensagens
    try:
        if message_processor:
            health_status["ai_processor"] = "online"
            health_status["services"]["message_processor"] = "ok"
    except Exception as e:
        health_status["services"]["message_processor"] = f"error: {str(e)}"
    
    return health_status

@app.get("/analytics/")
async def get_analytics():
    """Analytics básicas"""
    
    try:
        client = get_supabase_client()
        
        # Contar registros
        sessions = client.table('conversation_sessions').select('*', count='exact').execute()
        leads = client.table('leads').select('*', count='exact').execute()
        properties = client.table('properties').select('*', count='exact').execute()
        
        return {
            "success": True,
            "analytics": {
                "total_sessions": sessions.count,
                "total_leads": leads.count,
                "total_properties": properties.count,
                "active_sessions": len([s for s in sessions.data if s.get('active', False)]),
                "active_leads": len([l for l in leads.data if l.get('status') == 'active'])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/n8n")
async def n8n_webhook(payload: Dict[str, Any]):
    """Webhook principal para N8N"""
    
    try:
        # Extrair dados da mensagem
        message = payload.get('message', '')
        contact_name = payload.get('contact_name', 'Cliente')
        phone = payload.get('phone', '')
        chat_id = payload.get('chat_id', f'chat_{phone}')
        
        if not message or not phone:
            raise HTTPException(status_code=400, detail="Mensagem e telefone são obrigatórios")
        
        # Criar sessão
        session = {
            'id': chat_id,
            'contact_name': contact_name,
            'phone': phone,
            'chat_id': chat_id
        }
        
        # Processar mensagem
        result = await message_processor.process_message(message, session)
        
        # Salvar no Supabase
        try:
            client = get_supabase_client()
            session_data = {
                'phone': phone,
                'chat_id': chat_id,
                'contact_name': contact_name,
                'last_intent': result['intent'],
                'last_message': message,
                'conversation_stage': 'active',
                'collected_info': payload.get('collected_info', {}),
                'context_data': {
                    'source': 'n8n',
                    'platform': 'railway',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Verificar se sessão já existe
            existing = client.table('conversation_sessions').select('*').eq('chat_id', chat_id).execute()
            
            if existing.data:
                # Atualizar sessão existente
                client.table('conversation_sessions').update(session_data).eq('chat_id', chat_id).execute()
            else:
                # Criar nova sessão
                client.table('conversation_sessions').insert(session_data).execute()
            
            result['saved_to_database'] = True
            
        except Exception as db_error:
            result['saved_to_database'] = False
            result['database_error'] = str(db_error)
        
        return {
            "success": True,
            "input": payload,
            "output": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/test")
async def test_webhook(payload: Dict[str, Any]):
    """Webhook de teste"""
    return await n8n_webhook(payload)

@app.get("/leads/")
async def get_leads():
    """Listar leads"""
    
    try:
        client = get_supabase_client()
        result = client.table('leads').select('*').order('created_at', desc=True).limit(50).execute()
        
        return {
            "success": True,
            "leads": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/properties/")
async def get_properties():
    """Listar imóveis"""
    
    try:
        client = get_supabase_client()
        result = client.table('properties').select('*').eq('status', 'active').order('created_at', desc=True).limit(50).execute()
        
        return {
            "success": True,
            "properties": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/")
async def get_sessions():
    """Listar sessões ativas"""
    
    try:
        client = get_supabase_client()
        result = client.table('conversation_sessions').select('*').eq('active', True).order('updated_at', desc=True).limit(50).execute()
        
        return {
            "success": True,
            "sessions": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
