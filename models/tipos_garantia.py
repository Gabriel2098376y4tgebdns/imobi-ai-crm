"""
Modelo de Tipos de Garantia para Locação
"""

from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from models.base import Base
import uuid


class TipoGarantia(Base):
    __tablename__ = "tipos_garantia"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False, unique=True)
    descricao_curta = Column(String(255))
    descricao_completa = Column(Text)
    como_funciona = Column(Text)
    
    # DOCUMENTAÇÃO NECESSÁRIA
    documentos_necessarios = Column(ARRAY(String))
    tempo_aprovacao = Column(String(50))
    custo_aproximado = Column(String(100))
    
    # CARACTERÍSTICAS
    renda_minima_exigida = Column(String(100))
    observacoes_importantes = Column(Text)
    vantagens = Column(ARRAY(String))
    desvantagens = Column(ARRAY(String))
    
    # CONTROLE
    ativo = Column(Boolean, default=True)
    ordem_apresentacao = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'nome': self.nome,
            'descricao_curta': self.descricao_curta,
            'descricao_completa': self.descricao_completa,
            'como_funciona': self.como_funciona,
            'documentos_necessarios': self.documentos_necessarios or [],
            'tempo_aprovacao': self.tempo_aprovacao,
            'custo_aproximado': self.custo_aproximado,
            'renda_minima_exigida': self.renda_minima_exigida,
            'vantagens': self.vantagens or [],
            'desvantagens': self.desvantagens or []
        }
