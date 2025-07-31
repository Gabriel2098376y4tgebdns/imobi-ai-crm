"""
Script de inicialização da Fase 1
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db_session, engine
from models.base import Base
from models.configuracao_imobiliaria import ConfiguracaoImobiliaria
from models.imovel_dual import ImovelDual
from models.lead_crm_integrado import LeadCRMIntegrado
from models.garantias_locacao import TipoGarantia, GARANTIAS_INICIAIS
from sqlalchemy import text


def criar_tabelas():
    """Criar todas as tabelas da Fase 1"""
    print("🗄️ Criando tabelas da Fase 1...")
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar índices geográficos específicos
    with get_db_session() as db:
        try:
            # Índice geográfico para busca por proximidade
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_imoveis_dual_location 
                ON imoveis_dual USING GIST (ST_Point(longitude, latitude));
            """))
            
            # Índices compostos para performance
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_imoveis_dual_busca 
                ON imoveis_dual (cliente_id, tipo_operacao, tipo_imovel, ativo);
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leads_crm_etapa 
                ON leads_crm (cliente_id, etapa_crm, ativo);
            """))
            
            db.commit()
            print("✅ Índices geográficos criados")
            
        except Exception as e:
            print(f"⚠️ Aviso: {e}")
            db.rollback()


def popular_garantias():
    """Popular tabela de garantias com dados iniciais"""
    print("📋 Populando base de garantias...")
    
    with get_db_session() as db:
        # Verificar se já existem garantias
        existing = db.query(TipoGarantia).count()
        if existing > 0:
            print("✅ Garantias já existem na base")
            return
        
        # Inserir garantias iniciais
        for i, garantia_data in enumerate(GARANTIAS_INICIAIS):
            garantia = TipoGarantia(
                **garantia_data,
                ordem_apresentacao=i + 1
            )
            db.add(garantia)
        
        db.commit()
        print(f"✅ {len(GARANTIAS_INICIAIS)} tipos de garantia inseridos")


def criar_configuracao_exemplo():
    """Criar configuração de exemplo para teste"""
    print("⚙️ Criando configuração de exemplo...")
    
    with get_db_session() as db:
        # Verificar se já existe
        existing = db.query(ConfiguracaoImobiliaria).filter_by(
            cliente_id='teste_local'
        ).first()
        
        if existing:
            print("✅ Configuração de exemplo já existe")
            return
        
        # Criar configuração de teste
        config = ConfiguracaoImobiliaria(
            cliente_id='teste_local',
            nome_imobiliaria='Imobiliária Teste',
            vendas_ativo=True,
            locacao_ativo=True,
            raio_busca_km=3,
            auto_matching_ativo=True,
            telefone_whatsapp='5511999999999',
            xml_url_unificado='https://exemplo.com/imoveis.xml',
            horario_importacao='08:00'
        )
        
        db.add(config)
        db.commit()
        print("✅ Configuração de exemplo criada")


def verificar_estrutura():
    """Verificar se a estrutura foi criada corretamente"""
    print("🔍 Verificando estrutura...")
    
    with get_db_session() as db:
        # Verificar tabelas
        tabelas = [
            'configuracao_imobiliaria',
            'imoveis_dual', 
            'leads_crm',
            'tipos_garantia'
        ]
        
        for tabela in tabelas:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
                print(f"✅ {tabela}: {result} registros")
            except Exception as e:
                print(f"❌ {tabela}: Erro - {e}")


if __name__ == "__main__":
    print("🚀 INICIALIZANDO FASE 1 - ESTRUTURA BASE")
    print("=" * 50)
    
    try:
        criar_tabelas()
        popular_garantias()
        criar_configuracao_exemplo()
        verificar_estrutura()
        
        print("=" * 50)
        print("🎉 FASE 1 INICIALIZADA COM SUCESSO!")
        print("")
        print("📋 Próximos passos:")
        print("1. Configurar XML com tipo de operação")
        print("2. Implementar integração com CRM")
        print("3. Criar sistema de matching geográfico")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
