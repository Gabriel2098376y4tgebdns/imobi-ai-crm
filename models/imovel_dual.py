"""
Modelo de Imóvel Unificado - Vendas e Locação
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base
from datetime import datetime
import uuid


class ImovelDual(Base):
    __tablename__ = "imoveis_dual"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(String(255), nullable=False, index=True)
    codigo_imovel = Column(String(100), nullable=False)
    
    # TIPO DE OPERAÇÃO - FUNDAMENTAL
    tipo_operacao = Column(String(10), nullable=False)  # 'venda' ou 'locacao'
    
    # INFORMAÇÕES BÁSICAS (COMUM PARA AMBOS)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    endereco = Column(String(500), nullable=False)
    bairro = Column(String(100))
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String(10))
    
    # COORDENADAS GEOGRÁFICAS (OBRIGATÓRIO PARA MATCHING)
    latitude = Column(Numeric(10, 8), index=True)
    longitude = Column(Numeric(11, 8), index=True)
    endereco_normalizado = Column(Text)  # Para geocoding
    
    # CARACTERÍSTICAS DO IMÓVEL (COMUM)
    tipo_imovel = Column(String(50), nullable=False, index=True)  # apartamento, casa, comercial
    quartos = Column(Integer, default=0, index=True)
    banheiros = Column(Integer, default=0)
    suites = Column(Integer, default=0)
    vagas_garagem = Column(Integer, default=0, index=True)
    area_total = Column(Numeric(8,2))
    area_util = Column(Numeric(8,2))
    
    # VALORES PARA VENDA
    preco_venda = Column(Numeric(12,2))
    aceita_financiamento = Column(Boolean, default=True)
    valor_entrada_minima = Column(Numeric(12,2))
    
    # VALORES PARA LOCAÇÃO
    valor_aluguel = Column(Numeric(10,2))
    valor_condominio = Column(Numeric(10,2), default=0)
    valor_iptu = Column(Numeric(8,2), default=0)
    valor_total_mensal = Column(Numeric(10,2))  # Calculado automaticamente
    
    # CARACTERÍSTICAS ESPECÍFICAS DE LOCAÇÃO
    mobiliado = Column(String(20), default='nao')  # 'sim', 'semi', 'nao'
    aceita_pets = Column(Boolean, default=False)
    disponivel_a_partir = Column(DateTime)
    tempo_minimo_contrato = Column(Integer, default=12)  # meses
    
    # METADADOS
    fotos = Column(Text)  # URLs separadas por vírgula
    caracteristicas_extras = Column(Text)  # JSON com características adicionais
    
    # CONTROLE
    ativo = Column(Boolean, default=True, index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_ultima_importacao = Column(DateTime)  # Controle de importação XML
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Calcular valor total mensal automaticamente
        if self.tipo_operacao == 'locacao':
            self.calcular_valor_total_mensal()
    
    def calcular_valor_total_mensal(self):
        """Calcular valor total mensal para locação"""
        if self.valor_aluguel:
            self.valor_total_mensal = (
                (self.valor_aluguel or 0) + 
                (self.valor_condominio or 0) + 
                (self.valor_iptu or 0)
            )
    
    def to_dict(self):
        """Converter para dicionário com dados específicos por operação"""
        base_dict = {
            'id': str(self.id),
            'cliente_id': self.cliente_id,
            'codigo_imovel': self.codigo_imovel,
            'tipo_operacao': self.tipo_operacao,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'tipo_imovel': self.tipo_imovel,
            'quartos': self.quartos,
            'banheiros': self.banheiros,
            'suites': self.suites,
            'vagas_garagem': self.vagas_garagem,
            'area_total': float(self.area_total) if self.area_total else None,
            'area_util': float(self.area_util) if self.area_util else None,
            'aceita_pets': self.aceita_pets,
            'fotos': self.fotos.split(',') if self.fotos else [],
            'galeria_url': f"/galeria/{self.cliente_id}/{self.id}",
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
        
        # Adicionar dados específicos por operação
        if self.tipo_operacao == 'venda':
            base_dict.update({
                'preco_venda': float(self.preco_venda) if self.preco_venda else None,
                'aceita_financiamento': self.aceita_financiamento,
                'valor_entrada_minima': float(self.valor_entrada_minima) if self.valor_entrada_minima else None
            })
        elif self.tipo_operacao == 'locacao':
            base_dict.update({
                'valor_aluguel': float(self.valor_aluguel) if self.valor_aluguel else None,
                'valor_condominio': float(self.valor_condominio) if self.valor_condominio else None,
                'valor_iptu': float(self.valor_iptu) if self.valor_iptu else None,
                'valor_total_mensal': float(self.valor_total_mensal) if self.valor_total_mensal else None,
                'mobiliado': self.mobiliado,
                'disponivel_a_partir': self.disponivel_a_partir.isoformat() if self.disponivel_a_partir else None,
                'tempo_minimo_contrato': self.tempo_minimo_contrato
            })
        
        return base_dict
