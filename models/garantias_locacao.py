"""
Base de Conhecimento - Tipos de Garantia para Locação
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
    renda_minima_exigida = Column(String(100))  # Ex: "3x o valor do aluguel"
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


# DADOS INICIAIS PARA POPULAR A TABELA
GARANTIAS_INICIAIS = [
    {
        'nome': 'Seguro Fiança',
        'descricao_curta': 'Seguro que garante o pagamento do aluguel',
        'descricao_completa': 'O seguro fiança é uma modalidade de seguro que garante o pagamento do aluguel e encargos em caso de inadimplência do locatário.',
        'como_funciona': 'Você contrata um seguro que cobre até 36 meses de aluguel. A seguradora paga o proprietário em caso de inadimplência e depois cobra de você. É mais prático que fiador.',
        'documentos_necessarios': [
            'CPF e RG',
            'Comprovante de renda (3x o valor do aluguel)',
            'Comprovante de residência',
            'Declaração de Imposto de Renda',
            'Extratos bancários (3 meses)'
        ],
        'tempo_aprovacao': '24 a 48 horas',
        'custo_aproximado': '1 a 2% do valor do aluguel por mês',
        'renda_minima_exigida': '3x o valor do aluguel',
        'vantagens': [
            'Aprovação rápida',
            'Não precisa de fiador',
            'Aceito pela maioria dos proprietários',
            'Processo 100% digital'
        ],
        'desvantagens': [
            'Custo mensal adicional',
            'Análise de crédito rigorosa'
        ]
    },
    {
        'nome': 'Fiador',
        'descricao_curta': 'Pessoa que se responsabiliza pelo pagamento',
        'descricao_completa': 'O fiador é uma pessoa física que se responsabiliza solidariamente pelo pagamento do aluguel e demais obrigações do contrato.',
        'como_funciona': 'Uma pessoa com renda comprovada e preferencialmente imóvel próprio assina como responsável pelos pagamentos. Em caso de inadimplência, o proprietário pode cobrar tanto do locatário quanto do fiador.',
        'documentos_necessarios': [
            'Documentos pessoais do fiador',
            'Comprovante de renda do fiador (3x o valor do aluguel)',
            'Escritura de imóvel próprio (preferencial)',
            'Declaração de Imposto de Renda do fiador',
            'Certidões negativas do fiador'
        ],
        'tempo_aprovacao': '3 a 7 dias',
        'custo_aproximado': 'Sem custo adicional',
        'renda_minima_exigida': 'Fiador com renda de 3x o valor do aluguel',
        'vantagens': [
            'Sem custo adicional',
            'Amplamente aceito',
            'Modalidade tradicional'
        ],
        'desvantagens': [
            'Difícil encontrar fiador disponível',
            'Fiador assume responsabilidade indefinida',
            'Processo mais burocrático'
        ]
    },
    {
        'nome': 'Título de Capitalização',
        'descricao_curta': 'Aplicação financeira como garantia',
        'descricao_completa': 'Títulos de capitalização são aplicações financeiras que ficam como garantia durante todo o período do contrato de locação.',
        'como_funciona': 'Você compra títulos de capitalização equivalentes a alguns meses de aluguel. Os títulos ficam bloqueados como garantia e você pode resgatar com rendimento no final do contrato.',
        'documentos_necessarios': [
            'CPF e RG',
            'Comprovante de renda',
            'Comprovante de residência'
        ],
        'tempo_aprovacao': '1 a 3 dias',
        'custo_aproximado': 'Valor equivalente a 3-6 meses de aluguel',
        'renda_minima_exigida': 'Variável conforme a seguradora',
        'vantagens': [
            'Você resgata o valor no final',
            'Rendimento durante o período',
            'Aprovação mais simples'
        ],
        'desvantagens': [
            'Valor alto inicial',
            'Dinheiro fica bloqueado',
            'Rendimento baixo'
        ]
    },
    {
        'nome': 'Crédito Pago',
        'descricao_curta': 'Empresa especializada assume o risco',
        'descricao_completa': 'Empresas especializadas em crédito que analisam seu perfil e assumem a responsabilidade pelo pagamento do aluguel.',
        'como_funciona': 'Uma empresa de análise de crédito avalia seu perfil financeiro e assume a responsabilidade pelos pagamentos. Você paga uma taxa mensal para a empresa.',
        'documentos_necessarios': [
            'CPF e RG',
            'Comprovante de renda',
            'Análise de crédito completa',
            'Extratos bancários',
            'Comprovantes de pagamento'
        ],
        'tempo_aprovacao': '24 a 72 horas',
        'custo_aproximado': '0,5% a 1,5% do valor do aluguel por mês',
        'renda_minima_exigida': 'Variável conforme análise de crédito',
        'vantagens': [
            'Aprovação baseada em score',
            'Processo digital',
            'Não precisa de fiador ou imóvel'
        ],
        'desvantagens': [
            'Custo mensal',
            'Análise de crédito rigorosa',
            'Menos aceito que outras modalidades'
        ]
    }
]
