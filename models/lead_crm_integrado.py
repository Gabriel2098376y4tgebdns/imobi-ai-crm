"""
Lead integrado com CRM externo
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from models.base import Base
from datetime import datetime
import uuid


class LeadCRMIntegrado(Base):
    __tablename__ = "leads_crm"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(String(255), nullable=False, index=True)
    
    # IDENTIFICAÇÃO DO LEAD
    crm_lead_id = Column(String(255), index=True)  # ID no CRM externo
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), index=True)
    email = Column(String(255))
    
    # TIPO DE INTERESSE (PODE SER AMBOS)
    interesse_venda = Column(Boolean, default=False, index=True)
    interesse_locacao = Column(Boolean, default=False, index=True)
    operacao_principal = Column(String(10))  # 'venda', 'locacao' ou 'ambos'
    
    # STATUS NO CRM (INTEGRAÇÃO)
    status_crm = Column(String(100), index=True)  # Status atual no CRM
    etapa_crm = Column(String(100), index=True)  # Etapa do funil no CRM
    
    # ETAPAS IMPORTANTES PARA MATCHING
    # 'novo', 'qualificado', 'visita_agendada', 'visita_realizada', 
    # 'proposta_enviada', 'negociacao', 'fechado', 'perdido'
    
    # CRITÉRIOS DE BUSCA GEOGRÁFICA
    cidades_interesse = Column(ARRAY(String))
    bairros_interesse = Column(ARRAY(String))
    latitude_centro = Column(Float, index=True)  # Centro da busca
    longitude_centro = Column(Float, index=True)
    raio_busca_km = Column(Integer, default=3)
    
    # CRITÉRIOS DO IMÓVEL
    tipo_imovel = Column(String(50), index=True)  # apartamento, casa, comercial
    quartos_min = Column(Integer, default=0)
    quartos_max = Column(Integer)
    banheiros_min = Column(Integer, default=0)
    vagas_min = Column(Integer, default=0)
    area_min = Column(Float)
    area_max = Column(Float)
    
    # CRITÉRIOS FINANCEIROS - VENDA
    orcamento_min_venda = Column(Float)
    orcamento_max_venda = Column(Float)
    aceita_financiamento = Column(Boolean, default=True)
    valor_entrada_disponivel = Column(Float)
    
    # CRITÉRIOS FINANCEIROS - LOCAÇÃO
    orcamento_max_aluguel = Column(Float)
    orcamento_max_total_mensal = Column(Float)
    
    # PREFERÊNCIAS LOCAÇÃO
    aceita_pets_necessario = Column(Boolean, default=False)
    mobiliado_preferencia = Column(String(20), default='indiferente')  # 'sim', 'nao', 'indiferente'
    
    # CONTROLE DE CONTATOS
    ultimo_contato = Column(DateTime)
    proximo_contato = Column(DateTime)
    total_contatos = Column(Integer, default=0)
    
    # IMÓVEIS APRESENTADOS (HISTÓRICO)
    imoveis_apresentados = Column(JSON)  # Lista de IDs de imóveis já apresentados
    imoveis_visitados = Column(JSON)  # Lista de imóveis visitados
    imoveis_interesse = Column(JSON)  # Lista de imóveis com interesse
    
    # OBSERVAÇÕES E NOTAS
    observacoes = Column(Text)
    notas_crm = Column(Text)  # Notas vindas do CRM
    
    # METADADOS
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_ultima_sincronizacao_crm = Column(DateTime)
    ativo = Column(Boolean, default=True, index=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'cliente_id': self.cliente_id,
            'crm_lead_id': self.crm_lead_id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'interesse_venda': self.interesse_venda,
            'interesse_locacao': self.interesse_locacao,
            'operacao_principal': self.operacao_principal,
            'status_crm': self.status_crm,
            'etapa_crm': self.etapa_crm,
            'cidades_interesse': self.cidades_interesse,
            'bairros_interesse': self.bairros_interesse,
            'latitude_centro': self.latitude_centro,
            'longitude_centro': self.longitude_centro,
            'tipo_imovel': self.tipo_imovel,
            'quartos_min': self.quartos_min,
            'quartos_max': self.quartos_max,
            'orcamento_max_venda': self.orcamento_max_venda,
            'orcamento_max_total_mensal': self.orcamento_max_total_mensal,
            'imoveis_apresentados': self.imoveis_apresentados or [],
            'ultimo_contato': self.ultimo_contato.isoformat() if self.ultimo_contato else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def get_etapas_para_matching(self):
        """Retorna as etapas do CRM que devem receber matching automático"""
        etapas_ativas = [
            'visita_agendada',
            'visita_realizada', 
            'proposta_enviada',
            'atendimento',
            'negociacao'
        ]
        return self.etapa_crm in etapas_ativas
