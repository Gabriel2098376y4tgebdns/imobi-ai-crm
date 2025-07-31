"""
Modelo de dados para Clientes
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class Cliente(Base):
    __tablename__ = "clientes"
    
    # Identificação
    id = Column(String(50), primary_key=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200))
    telefone = Column(String(20))
    
    # Configurações XML
    xml_url = Column(String(500), nullable=False)
    xml_mapping_config = Column(JSON)
    
    # Configurações de importação
    importacao_ativa = Column(Boolean, default=True)
    frequencia_importacao = Column(String(50), default='diaria')
    horario_importacao = Column(String(10), default='08:00')
    
    # Configurações WhatsApp
    whatsapp_ativo = Column(Boolean, default=False)
    whatsapp_token = Column(String(500))
    whatsapp_numero = Column(String(20))
    
    # Configurações IA
    ia_ativa = Column(Boolean, default=True)
    prompt_personalizado = Column(Text)
    score_minimo_match = Column(Float, default=0.5)
    
    # Status
    status = Column(String(50), default='ativo')
    plano = Column(String(50), default='basico')
    
    # Metadados
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    ultima_importacao = Column(DateTime)
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nome={self.nome})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'xml_url': self.xml_url,
            'importacao_ativa': self.importacao_ativa,
            'frequencia_importacao': self.frequencia_importacao,
            'whatsapp_ativo': self.whatsapp_ativo,
            'ia_ativa': self.ia_ativa,
            'status': self.status,
            'plano': self.plano,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultima_importacao': self.ultima_importacao.isoformat() if self.ultima_importacao else None
        }
