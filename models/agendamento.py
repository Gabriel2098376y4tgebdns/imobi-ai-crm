"""
Modelo de Agendamento de Visitas
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()


class Agendamento(Base):
    __tablename__ = "agendamentos"
    
    # Identificação
    id = Column(String(50), primary_key=True)
    cliente_id = Column(String(50), nullable=False)
    lead_id = Column(String(50), nullable=False)
    
    # Dados do cliente
    nome_cliente = Column(String(200), nullable=False)
    telefone_cliente = Column(String(20))
    
    # Dados do imóvel
    imovel_id = Column(String(50), nullable=False)
    codigo_imovel = Column(String(50))
    endereco_imovel = Column(String(500))
    
    # Agendamento
    data_visita = Column(DateTime, nullable=False)
    observacoes = Column(Text)
    
    # Status
    status = Column(String(50), default='agendado')  # agendado, confirmado, realizado, cancelado
    
    # Metadados
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Agendamento(id={self.id}, cliente={self.nome_cliente})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'lead_id': self.lead_id,
            'nome_cliente': self.nome_cliente,
            'telefone_cliente': self.telefone_cliente,
            'imovel_id': self.imovel_id,
            'codigo_imovel': self.codigo_imovel,
            'endereco_imovel': self.endereco_imovel,
            'data_visita': self.data_visita.isoformat() if self.data_visita else None,
            'observacoes': self.observacoes,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
