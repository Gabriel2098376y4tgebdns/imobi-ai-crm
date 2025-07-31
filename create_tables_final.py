"""
Criar Tabelas Final - Sem Emojis
"""

import os
from dotenv import load_dotenv

load_dotenv('.env.supabase')

def create_tables():
    print("=== CRIANDO TABELAS NO SUPABASE ===")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not service_key:
            print("ERRO: Service key necessaria")
            return False
        
        # Cliente admin
        admin_client = create_client(url, service_key)
        
        # SQL para criar tabela conversation_sessions
        sql_sessions = """
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            phone VARCHAR(20) NOT NULL,
            chat_id VARCHAR(255) NOT NULL,
            contact_name VARCHAR(255),
            conversation_stage VARCHAR(50) DEFAULT 'initial',
            last_intent VARCHAR(50),
            last_message TEXT,
            collected_info JSONB DEFAULT '{}',
            context_data JSONB DEFAULT '{}',
            active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '24 hours')
        );
        
        CREATE INDEX IF NOT EXISTS idx_conversation_sessions_phone ON conversation_sessions(phone);
        CREATE INDEX IF NOT EXISTS idx_conversation_sessions_chat_id ON conversation_sessions(chat_id);
        CREATE INDEX IF NOT EXISTS idx_conversation_sessions_active ON conversation_sessions(active);
        """
        
        # SQL para criar tabela leads
        sql_leads = """
        CREATE TABLE IF NOT EXISTS leads (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            phone VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            property_type VARCHAR(50),
            operation_type VARCHAR(20),
            min_price DECIMAL(12,2),
            max_price DECIMAL(12,2),
            bedrooms INTEGER,
            bathrooms INTEGER,
            preferred_regions JSONB DEFAULT '[]',
            status VARCHAR(20) DEFAULT 'active',
            source VARCHAR(50) DEFAULT 'n8n',
            notes TEXT,
            tags JSONB DEFAULT '[]',
            custom_data JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            last_contact TIMESTAMPTZ
        );
        
        CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_property_type ON leads(property_type);
        """
        
        # SQL para criar tabela properties
        sql_properties = """
        CREATE TABLE IF NOT EXISTS properties (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            external_id VARCHAR(100) UNIQUE,
            code VARCHAR(50) UNIQUE,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            property_type VARCHAR(50) NOT NULL,
            operation_type VARCHAR(20) NOT NULL,
            sale_price DECIMAL(12,2),
            rent_price DECIMAL(12,2),
            condo_fee DECIMAL(12,2),
            iptu DECIMAL(12,2),
            bedrooms INTEGER,
            bathrooms INTEGER,
            suites INTEGER,
            parking_spaces INTEGER,
            area_total DECIMAL(10,2),
            area_useful DECIMAL(10,2),
            address VARCHAR(500),
            neighborhood VARCHAR(100),
            city VARCHAR(100),
            state VARCHAR(2),
            zipcode VARCHAR(10),
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            images JSONB DEFAULT '[]',
            virtual_tour VARCHAR(500),
            status VARCHAR(20) DEFAULT 'active',
            featured BOOLEAN DEFAULT false,
            amenities JSONB DEFAULT '[]',
            custom_data JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            imported_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
        CREATE INDEX IF NOT EXISTS idx_properties_operation_type ON properties(operation_type);
        CREATE INDEX IF NOT EXISTS idx_properties_neighborhood ON properties(neighborhood);
        CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
        """
        
        # Executar SQLs
        print("Criando tabela conversation_sessions...")
        result1 = admin_client.rpc('exec_sql', {'sql': sql_sessions}).execute()
        print("Tabela conversation_sessions: OK")
        
        print("Criando tabela leads...")
        result2 = admin_client.rpc('exec_sql', {'sql': sql_leads}).execute()
        print("Tabela leads: OK")
        
        print("Criando tabela properties...")
        result3 = admin_client.rpc('exec_sql', {'sql': sql_properties}).execute()
        print("Tabela properties: OK")
        
        # Testar inserção de dados
        print("Inserindo dados de teste...")
        client = create_client(url, anon_key)
        
        # Dados de teste para conversation_sessions
        test_session = {
            'phone': '5511999999999',
            'chat_id': 'test_final_' + str(int(__import__('time').time())),
            'contact_name': 'Gabriel Teste',
            'conversation_stage': 'initial',
            'last_intent': 'saudacao',
            'last_message': 'Ola, teste final do sistema',
            'collected_info': {'interesse': 'apartamento'},
            'context_data': {'origem': 'teste_final'},
            'active': True
        }
        
        result = client.table('conversation_sessions').insert(test_session).execute()
        print("Dados de teste conversation_sessions: OK")
        
        # Dados de teste para leads
        test_lead = {
            'phone': '5511999999999',
            'name': 'Gabriel - Desenvolvedor',
            'email': 'gabriel@teste.com',
            'property_type': 'apartamento',
            'operation_type': 'venda',
            'min_price': 400000,
            'max_price': 600000,
            'bedrooms': 3,
            'bathrooms': 2,
            'preferred_regions': ['vila_madalena', 'pinheiros'],
            'status': 'active',
            'source': 'n8n',
            'notes': 'Lead de teste - desenvolvedor interessado em apartamento',
            'tags': ['teste', 'desenvolvedor', 'prioritario']
        }
        
        result = client.table('leads').insert(test_lead).execute()
        print("Dados de teste leads: OK")
        
        # Dados de teste para properties
        test_property = {
            'external_id': 'test_001_final',
            'code': 'APT001_TESTE',
            'title': 'Apartamento Teste - Vila Madalena',
            'description': 'Apartamento de teste para validacao do sistema',
            'property_type': 'apartamento',
            'operation_type': 'venda',
            'sale_price': 550000,
            'rent_price': 3500,
            'condo_fee': 800,
            'iptu': 200,
            'bedrooms': 3,
            'bathrooms': 2,
            'suites': 1,
            'parking_spaces': 2,
            'area_total': 85.5,
            'area_useful': 75.0,
            'address': 'Rua Teste, 123 - Vila Madalena',
            'neighborhood': 'Vila Madalena',
            'city': 'Sao Paulo',
            'state': 'SP',
            'zipcode': '05432-000',
            'images': ['https://exemplo.com/img1.jpg', 'https://exemplo.com/img2.jpg'],
            'status': 'active',
            'featured': True,
            'amenities': ['piscina', 'academia', 'salao_festas', 'portaria_24h']
        }
        
        result = client.table('properties').insert(test_property).execute()
        print("Dados de teste properties: OK")
        
        # Verificar dados
        print("Verificando dados inseridos...")
        
        sessions = client.table('conversation_sessions').select('*').execute()
        print(f"Total conversation_sessions: {len(sessions.data)}")
        
        leads = client.table('leads').select('*').execute()
        print(f"Total leads: {len(leads.data)}")
        
        properties = client.table('properties').select('*').execute()
        print(f"Total properties: {len(properties.data)}")
        
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    if create_tables():
        print("\n=== SUCESSO TOTAL ===")
        print("Todas as tabelas criadas e testadas!")
        print("Sistema pronto para producao!")
    else:
        print("\n=== ERRO ===")
        print("Falha na criacao das tabelas")
