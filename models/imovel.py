"""
Modelo de dados para Imóveis
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class Imovel(Base):
    __tablename__ = "imoveis"
    
    # Campos obrigatórios
    id = Column(String(50), primary_key=True)  # ID do XML
    cliente_id = Column(String(50), nullable=False, index=True)  # ID do cliente
    codigo_imovel = Column(String(100), nullable=False)  # Código do imóvel no CRM
    
    # Informações básicas
    titulo = Column(String(500), nullable=False)
    tipo = Column(String(100), nullable=False)  # apartamento, casa, terreno
    categoria = Column(String(100))  # venda, locacao, temporada
    preco = Column(Float, nullable=False)
    preco_condominio = Column(Float)
    preco_iptu = Column(Float)
    
    # Localização
    endereco = Column(String(500))
    numero = Column(String(20))
    complemento = Column(String(200))
    bairro = Column(String(200))
    cidade = Column(String(200), nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Características
    area_total = Column(Float)
    area_construida = Column(Float)
    area_terreno = Column(Float)
    quartos = Column(Integer)
    suites = Column(Integer)
    banheiros = Column(Integer)
    vagas_garagem = Column(Integer)
    andar = Column(Integer)
    total_andares = Column(Integer)
    
    # Descrição e mídia
    descricao = Column(Text)
    observacoes = Column(Text)
    fotos = Column(JSON)  # Lista de URLs das fotos
    videos = Column(JSON)  # Lista de URLs dos vídeos
    tour_virtual = Column(String(500))
    
    # Status e controle
    status = Column(String(50), default='ativo')  # ativo, inativo, vendido, alugado
    destaque = Column(Boolean, default=False)
    exclusivo = Column(Boolean, default=False)
    
    # Metadados
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    data_ultima_importacao = Column(DateTime, default=func.now())
    hash_xml = Column(String(64))  # Hash para detectar mudanças
    
    # Campos extras específicos do cliente
    campos_extras = Column(JSON)  # Dados específicos do XML do cliente
    
    def __repr__(self):
        return f"<Imovel(id={self.id}, titulo={self.titulo}, preco={self.preco})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'codigo_imovel': self.codigo_imovel,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'preco': self.preco,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'area_total': self.area_total,
            'quartos': self.quartos,
            'banheiros': self.banheiros,
            'vagas_garagem': self.vagas_garagem,
            'fotos': self.fotos,
            'status': self.status,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class ImportacaoLog(Base):
    __tablename__ = "importacao_logs"
    
    id = Column(String(50), primary_key=True)
    cliente_id = Column(String(50), nullable=False, index=True)
    data_importacao = Column(DateTime, default=func.now())
    status = Column(String(50))  # sucesso, erro, parcial
    total_imoveis = Column(Integer, default=0)
    imoveis_novos = Column(Integer, default=0)
    imoveis_atualizados = Column(Integer, default=0)
    imoveis_removidos = Column(Integer, default=0)
    tempo_execucao = Column(Float)  # em segundos
    erros = Column(JSON)  # Lista de erros encontrados
    url_xml = Column(String(500))
    
    def __repr__(self):
        return f"<ImportacaoLog(cliente_id={self.cliente_id}, status={self.status})>"
