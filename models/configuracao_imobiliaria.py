"""
Configuração da Imobiliária - Módulos Ativos
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base
from datetime import datetime
import uuid


class ConfiguracaoImobiliaria(Base):
    __tablename__ = "configuracao_imobiliaria"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(String(255), unique=True, nullable=False, index=True)
    nome_imobiliaria = Column(String(255), nullable=False)
    
    # MÓDULOS ATIVOS
    vendas_ativo = Column(Boolean, default=True, nullable=False)
    locacao_ativo = Column(Boolean, default=False, nullable=False)
    
    # CONFIGURAÇÕES DE BUSCA
    raio_busca_km = Column(Integer, default=3, nullable=False)
    auto_matching_ativo = Column(Boolean, default=True, nullable=False)
    
    # CONFIGURAÇÕES DE CONTATO
    telefone_whatsapp = Column(String(20))
    template_apresentacao = Column(Text)
    
    # INTEGRAÇÃO CRM
    crm_url = Column(String(500))  # URL da API do CRM
    crm_token = Column(String(255))  # Token de acesso
    crm_ativo = Column(Boolean, default=False)
    
    # CONFIGURAÇÕES XML
    xml_url_vendas = Column(String(500))  # URL XML vendas
    xml_url_locacao = Column(String(500))  # URL XML locação
    xml_url_unificado = Column(String(500))  # URL XML com ambos
    horario_importacao = Column(String(5), default="08:00")  # Horário da importação
    
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'cliente_id': self.cliente_id,
            'nome_imobiliaria': self.nome_imobiliaria,
            'vendas_ativo': self.vendas_ativo,
            'locacao_ativo': self.locacao_ativo,
            'raio_busca_km': self.raio_busca_km,
            'auto_matching_ativo': self.auto_matching_ativo,
            'crm_ativo': self.crm_ativo,
            'horario_importacao': self.horario_importacao
        }
