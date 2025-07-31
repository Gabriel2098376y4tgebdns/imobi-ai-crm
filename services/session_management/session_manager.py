"""
Gerenciador de Sessões de Conversa
"""

import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON

from models.base import Base
from core.database import get_db_session

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, index=True)
    chat_id = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255))
    
    # Estado da conversa
    conversation_stage = Column(String(50), default='initial')
    last_intent = Column(String(50))
    last_message = Column(Text)
    
    # Informações coletadas
    collected_info = Column(JSON, default=dict)
    context_data = Column(JSON, default=dict)
    
    # Controle
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)  # Sessão expira em 24h
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'phone': self.phone,
            'chat_id': self.chat_id,
            'contact_name': self.contact_name,
            'conversation_stage': self.conversation_stage,
            'last_intent': self.last_intent,
            'last_message': self.last_message,
            'collected_info': self.collected_info or {},
            'context_data': self.context_data or {},
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SessionManager:
    """Gerenciador de sessões de conversa"""
    
    def __init__(self):
        self.session_timeout_hours = 24
    
    async def get_or_create_session(
        self, 
        phone: str, 
        chat_id: str, 
        contact_name: str
    ) -> Dict[str, Any]:
        """Obter sessão existente ou criar nova"""
        
        with get_db_session() as db:
            # Buscar sessão ativa existente
            session = db.query(ConversationSession).filter_by(
                phone=phone,
                chat_id=chat_id,
                active=True
            ).first()
            
            # Se não existe ou expirou, criar nova
            if not session or self._is_expired(session):
                if session:
                    session.active = False  # Desativar sessão expirada
                
                session = ConversationSession(
                    phone=phone,
                    chat_id=chat_id,
                    contact_name=contact_name,
                    expires_at=datetime.utcnow() + timedelta(hours=self.session_timeout_hours)
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            
            return session.to_dict()
    
    async def update_session(
        self, 
        session_id: str, 
        last_message: str = None,
        context_update: Dict[str, Any] = None,
        conversation_stage: str = None,
        last_intent: str = None
    ) -> bool:
        """Atualizar sessão existente"""
        
        with get_db_session() as db:
            session = db.query(ConversationSession).filter_by(
                id=session_id,
                active=True
            ).first()
            
            if not session:
                return False
            
            # Atualizar campos
            if last_message:
                session.last_message = last_message
            
            if conversation_stage:
                session.conversation_stage = conversation_stage
            
            if last_intent:
                session.last_intent = last_intent
            
            if context_update:
                # Merge context data
                current_context = session.context_data or {}
                current_context.update(context_update)
                session.context_data = current_context
                
                # Merge collected info se presente
                if 'collected_info' in context_update:
                    current_info = session.collected_info or {}
                    current_info.update(context_update['collected_info'])
                    session.collected_info = current_info
            
            # Estender expiração
            session.expires_at = datetime.utcnow() + timedelta(hours=self.session_timeout_hours)
            session.updated_at = datetime.utcnow()
            
            db.commit()
            return True
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obter sessão por ID"""
        
        with get_db_session() as db:
            session = db.query(ConversationSession).filter_by(
                id=session_id,
                active=True
            ).first()
            
            if session and not self._is_expired(session):
                return session.to_dict()
            
            return None
    
    async def end_session(self, session_id: str) -> bool:
        """Finalizar sessão"""
        
        with get_db_session() as db:
            session = db.query(ConversationSession).filter_by(
                id=session_id
            ).first()
            
            if session:
                session.active = False
                session.conversation_stage = 'finished'
                db.commit()
                return True
            
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Limpar sessões expiradas"""
        
        with get_db_session() as db:
            expired_sessions = db.query(ConversationSession).filter(
                ConversationSession.expires_at < datetime.utcnow(),
                ConversationSession.active == True
            ).all()
            
            count = len(expired_sessions)
            
            for session in expired_sessions:
                session.active = False
            
            db.commit()
            return count
    
    def _is_expired(self, session: ConversationSession) -> bool:
        """Verificar se sessão está expirada"""
        if not session.expires_at:
            return False
        return datetime.utcnow() > session.expires_at

# Criar tabela na inicialização
def create_session_table():
    """Criar tabela de sessões"""
    from core.database import engine
    ConversationSession.metadata.create_all(bind=engine)
