"""
Modelo de dados para Leads
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"
    
    # Identificação
    id = Column(String(50), primary_key=True)
    cliente_id = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(200))
    
    # Preferências de imóvel
    tipo_imovel = Column(String(100))  # apartamento, casa, terreno
    categoria = Column(String(100))  # venda, locacao
    orcamento_min = Column(Float)
    orcamento_max = Column(Float)
    quartos_min = Column(Integer)
    quartos_max = Column(Integer)
    banheiros_min = Column(Integer)
    area_min = Column(Float)
    area_max = Column(Float)
    vagas_min = Column(Integer)
    
    # Localização
    cidades_interesse = Column(JSON)  # Lista de cidades
    bairros_interesse = Column(JSON)  # Lista de bairros
    regiao_preferida = Column(String(200))
    
    # Características desejadas
    caracteristicas_desejadas = Column(JSON)  # piscina, churrasqueira, etc
    observacoes = Column(Text)
    
    # Status e controle
    status = Column(String(50), default='ativo')  # ativo, atendido, inativo
    prioridade = Column(Integer, default=1)  # 1=baixa, 5=alta
    origem = Column(String(100))  # whatsapp, site, indicacao
    
    # Matching e IA
    perfil_embedding = Column(JSON)  # Vetor de embedding do perfil
    interesses_calculados = Column(JSON)  # Interesses calculados pela IA
    score_qualificacao = Column(Float)  # Score de qualificação (0-1)
    
    # Metadados
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    ultima_interacao = Column(DateTime)
    
    def __repr__(self):
        return f"<Lead(id={self.id}, nome={self.nome}, telefone={self.telefone})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'tipo_imovel': self.tipo_imovel,
            'categoria': self.categoria,
            'orcamento_min': self.orcamento_min,
            'orcamento_max': self.orcamento_max,
            'quartos_min': self.quartos_min,
            'quartos_max': self.quartos_max,
            'cidades_interesse': self.cidades_interesse,
            'bairros_interesse': self.bairros_interesse,
            'caracteristicas_desejadas': self.caracteristicas_desejadas,
            'status': self.status,
            'prioridade': self.prioridade,
            'score_qualificacao': self.score_qualificacao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class Matching(Base):
    __tablename__ = "matchings"
    
    # Identificação
    id = Column(String(50), primary_key=True)
    lead_id = Column(String(50), nullable=False, index=True)
    imovel_id = Column(String(50), nullable=False, index=True)
    cliente_id = Column(String(50), nullable=False, index=True)
    
    # Scores de matching
    score_geral = Column(Float, nullable=False)  # Score geral (0-1)
    score_preco = Column(Float)  # Score de compatibilidade de preço
    score_localizacao = Column(Float)  # Score de localização
    score_caracteristicas = Column(Float)  # Score de características
    score_ia = Column(Float)  # Score calculado pela IA
    
    # Detalhes do matching
    motivos_match = Column(JSON)  # Lista de motivos do match
    pontos_atencao = Column(JSON)  # Pontos que podem ser problemáticos
    
    # Status
    status = Column(String(50), default='novo')  # novo, enviado, visualizado, interessado, descartado
    enviado_whatsapp = Column(Boolean, default=False)
    data_envio = Column(DateTime)
    feedback_lead = Column(String(100))  # interessado, nao_interessado, mais_info
    
    # Metadados
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Matching(lead_id={self.lead_id}, imovel_id={self.imovel_id}, score={self.score_geral})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'imovel_id': self.imovel_id,
            'cliente_id': self.cliente_id,
            'score_geral': self.score_geral,
            'score_preco': self.score_preco,
            'score_localizacao': self.score_localizacao,
            'score_caracteristicas': self.score_caracteristicas,
            'score_ia': self.score_ia,
            'motivos_match': self.motivos_match,
            'pontos_atencao': self.pontos_atencao,
            'status': self.status,
            'enviado_whatsapp': self.enviado_whatsapp,
            'feedback_lead': self.feedback_lead,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
