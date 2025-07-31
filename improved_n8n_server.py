"""
Servidor N8N Melhorado - Versão Estável
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from datetime import datetime
import re
import uuid
import uvicorn

app = FastAPI(title="Improved N8N Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulação de sessões em memória
sessions = {}

def classify_intent(message: str) -> Dict[str, Any]:
    """Classificar intenção básica"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde']):
        return {"intent": "saudacao", "confidence": 0.9}
    elif any(word in message_lower for word in ['apartamento', 'casa', 'imovel', 'comprar', 'alugar']):
        return {"intent": "interesse_imovel", "confidence": 0.8}
    elif any(word in message_lower for word in ['preço', 'valor', 'quanto', 'custa']):
        return {"intent": "preco", "confidence": 0.8}
    elif any(word in message_lower for word in ['visita', 'agendar', 'conhecer', 'ver']):
        return {"intent": "agendamento", "confidence": 0.8}
    elif any(word in message_lower for word in ['garantia', 'fiador', 'seguro']):
        return {"intent": "garantia", "confidence": 0.8}
    elif any(word in message_lower for word in ['tchau', 'obrigado', 'valeu']):
        return {"intent": "despedida", "confidence": 0.9}
    else:
        return {"intent": "geral", "confidence": 0.5}

def generate_response(intent: str, message: str, contact_name: str) -> Dict[str, Any]:
    """Gerar resposta baseada na intenção"""
    
    responses = {
        "saudacao": {
            "message": f"Olá {contact_name}! 😊 Sou a Carol, sua assistente imobiliária virtual.\n\nComo posso ajudar você hoje?",
            "quick_replies": ["🏠 Apartamentos", "🏡 Casas", "💰 Preços", "📋 Garantias"]
        },
        "interesse_imovel": {
            "message": f"Perfeito {contact_name}! Vejo que você tem interesse em imóveis.\n\nPara te ajudar melhor:\n• É para compra ou locação?\n• Quantos quartos?\n• Qual região?",
            "quick_replies": ["💰 Compra", "🏠 Locação", "📍 Regiões", "💬 Falar com consultor"]
        },
        "preco": {
            "message": f"{contact_name}, os preços variam conforme localização e características.\n\nPara valores precisos, preciso saber:\n• Tipo de imóvel\n• Região\n• Número de quartos",
            "quick_replies": ["🏠 Apartamento", "🏡 Casa", "📍 Regiões", "💬 Consultor"]
        },
        "agendamento": {
            "message": f"Ótimo {contact_name}! Vou verificar horários disponíveis.\n\nQual período prefere?\n• Manhã (9h-12h)\n• Tarde (14h-17h)\n• Final de semana",
            "quick_replies": ["🌅 Manhã", "🌞 Tarde", "📅 Final de semana", "📞 Ligar"]
        },
        "garantia": {
            "message": f"{contact_name}, temos várias opções de garantia:\n\n🔒 Seguro Fiança\n👥 Fiador\n💰 Título de Capitalização\n💳 Crédito Pago\n\nQual te interessa mais?",
            "quick_replies": ["🔒 Seguro Fiança", "👥 Fiador", "💰 Capitalização", "💳 Crédito"]
        },
        "despedida": {
            "message": f"Foi um prazer ajudar você {contact_name}! 😊\n\nQualquer dúvida, estarei aqui.\n\n*Carol - Assistente Imobiliária*",
            "quick_replies": []
        },
        "geral": {
            "message": f"Entendi {contact_name}! Como assistente imobiliária, posso ajudar com:\n\n🏠 Busca de imóveis\n💰 Informações de preços\n📋 Tipos de garantia\n📅 Agendamento de visitas",
            "quick_replies": ["🏠 Ver imóveis", "💰 Preços", "📋 Garantias", "💬 Consultor"]
        }
    }
    
    return responses.get(intent, responses["geral"])

@app.get("/health/")
async def health_check():
    return {
        "status": "healthy",
        "service": "improved-n8n-server",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }

@app.get("/n8n/status")
async def n8n_status():
    return {
        "status": "active",
        "service": "improved_n8n_integration",
        "endpoints": {
            "incoming_webhook": "/n8n/webhook/n8n/incoming",
            "test_webhook": "/n8n/webhook/n8n/test",
            "health_check": "/n8n/webhook/n8n/health"
        },
        "active_sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/n8n/webhook/n8n/incoming")
async def webhook_incoming(payload: Dict[str, Any]):
    """Webhook principal melhorado"""
    
    # Validar payload
    required_fields = ['phone', 'message', 'chat_id']
    for field in required_fields:
        if field not in payload:
            raise HTTPException(status_code=400, detail=f"Campo '{field}' obrigatório")
    
    phone = payload['phone']
    message = payload['message']
    chat_id = payload['chat_id']
    contact_name = payload.get('contact_name', 'Cliente')
    
    # Gerenciar sessão
    session_key = f"{phone}_{chat_id}"
    if session_key not in sessions:
        sessions[session_key] = {
            "id": str(uuid.uuid4()),
            "phone": phone,
            "chat_id": chat_id,
            "contact_name": contact_name,
            "created_at": datetime.now(),
            "messages": []
        }
    
    session = sessions[session_key]
    session["messages"].append({
        "message": message,
        "timestamp": datetime.now(),
        "type": "user"
    })
    
    # Classificar intenção
    intent_result = classify_intent(message)
    
    # Gerar resposta
    response_data = generate_response(
        intent_result["intent"], 
        message, 
        contact_name
    )
    
    # Salvar resposta na sessão
    session["messages"].append({
        "message": response_data["message"],
        "timestamp": datetime.now(),
        "type": "bot",
        "intent": intent_result["intent"]
    })
    
    return {
        "success": True,
        "session_id": session["id"],
        "phone": phone,
        "chat_id": chat_id,
        "response_data": {
            "message": response_data["message"],
            "message_type": "text",
            "quick_replies": response_data["quick_replies"],
            "attachments": [],
            "delay_seconds": 1
        },
        "metadata": {
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "agent_used": "carol_improved",
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/n8n/webhook/n8n/health")
async def webhook_health():
    return {
        "status": "healthy",
        "service": "improved_webhook",
        "active_sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/n8n/webhook/n8n/test")
async def webhook_test(test_data: Dict[str, Any] = None):
    """Teste melhorado do webhook"""
    
    default_test = {
        "phone": "5511999999999",
        "message": "Olá, gostaria de saber sobre apartamentos",
        "chat_id": "test_improved",
        "contact_name": "Cliente Teste"
    }
    
    test_payload = {**default_test, **(test_data or {})}
    response = await webhook_incoming(test_payload)
    
    return {
        "test_status": "success",
        "test_payload": test_payload,
        "response": response
    }

@app.get("/n8n/analytics/conversations")
async def get_analytics():
    """Analytics básico"""
    
    total_sessions = len(sessions)
    total_messages = sum(len(s["messages"]) for s in sessions.values())
    
    return {
        "success": True,
        "analytics": {
            "overview": {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "average_messages_per_session": round(total_messages / max(total_sessions, 1), 2)
            },
            "sessions": list(sessions.keys())
        },
        "generated_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Iniciando servidor N8N melhorado...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
