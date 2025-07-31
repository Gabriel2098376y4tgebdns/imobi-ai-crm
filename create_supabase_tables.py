"""
Criar tabelas no Supabase
"""

from core.supabase_config import get_admin_client

def create_tables():
    """Criar tabelas no Supabase"""
    
    print("🚀 Criando tabelas no Supabase...")
    
    admin_client = get_admin_client()
    if not admin_client:
        print("❌ Cliente admin não disponível")
        return False
    
    # SQL para criar tabelas
    tables_sql = """
    -- Tabela de sessões de conversa
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

    -- Índices para conversation_sessions
    CREATE INDEX IF NOT EXISTS idx_conversation_sessions_phone ON conversation_sessions(phone);
    CREATE INDEX IF NOT EXISTS idx_conversation_sessions_chat_id ON conversation_sessions(chat_id);
    CREATE INDEX IF NOT EXISTS idx_conversation_sessions_active ON conversation_sessions(active);

    -- Tabela de leads
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
        latitude DECIMAL(10,8),
        longitude DECIMAL(11,8),
        status VARCHAR(20) DEFAULT 'active',
        source VARCHAR(50) DEFAULT 'n8n',
        notes TEXT,
        tags JSONB DEFAULT '[]',
        custom_data JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        last_contact TIMESTAMPTZ
    );

    -- Índices para leads
    CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);
    CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

    -- Tabela de imóveis
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

    -- Índices para properties
    CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
    CREATE INDEX IF NOT EXISTS idx_properties_operation_type ON properties(operation_type);
    CREATE INDEX IF NOT EXISTS idx_properties_neighborhood ON properties(neighborhood);
    """
    
    try:
        # Executar SQL
        result = admin_client.rpc('exec_sql', {'sql': tables_sql}).execute()
        print("✅ Tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        
        # Tentar método alternativo
        try:
            print("🔄 Tentando método alternativo...")
            
            # Criar tabelas uma por vez
            tables = [
                ("conversation_sessions", """
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
                """),
                ("leads", """
                CREATE TABLE IF NOT EXISTS leads (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    phone VARCHAR(20) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    property_type VARCHAR(50),
                    operation_type VARCHAR(20),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """),
                ("properties", """
                CREATE TABLE IF NOT EXISTS properties (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(500) NOT NULL,
                    property_type VARCHAR(50) NOT NULL,
                    operation_type VARCHAR(20) NOT NULL,
                    sale_price DECIMAL(12,2),
                    rent_price DECIMAL(12,2),
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    neighborhood VARCHAR(100),
                    city VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """)
            ]
            
            for table_name, sql in tables:
                try:
                    admin_client.rpc('exec_sql', {'sql': sql}).execute()
                    print(f"✅ Tabela {table_name} criada")
                except Exception as table_error:
                    print(f"⚠️ Erro na tabela {table_name}: {table_error}")
            
            return True
            
        except Exception as e2:
            print(f"❌ Erro no método alternativo: {e2}")
            return False

def test_tables():
    """Testar se as tabelas foram criadas"""
    
    print("\n🧪 Testando tabelas...")
    
    from core.supabase_config import get_supabase_client
    client = get_supabase_client()
    
    if not client:
        print("❌ Cliente não disponível")
        return
    
    tables = ['conversation_sessions', 'leads', 'properties']
    
    for table in tables:
        try:
            result = client.table(table).select('*').limit(1).execute()
            print(f"✅ Tabela {table}: OK")
        except Exception as e:
            print(f"❌ Tabela {table}: {e}")

if __name__ == "__main__":
    if create_tables():
        test_tables()
        print("\n🎉 CONFIGURAÇÃO SUPABASE CONCLUÍDA!")
    else:
        print("\n❌ Falha na configuração")
