"""
Criar Tabelas Simples no Supabase
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
        
        if not service_key:
            print("ERRO: Service key necessaria")
            return False
        
        # Cliente admin
        admin_client = create_client(url, service_key)
        
        # SQL para criar tabela
        sql = """
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            phone VARCHAR(20) NOT NULL,
            chat_id VARCHAR(255) NOT NULL,
            contact_name VARCHAR(255),
            conversation_stage VARCHAR(50) DEFAULT 'initial',
            last_intent VARCHAR(50),
            last_message TEXT,
            active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_conversation_sessions_phone ON conversation_sessions(phone);
        CREATE INDEX IF NOT EXISTS idx_conversation_sessions_active ON conversation_sessions(active);
        """
        
        # Executar SQL
        result = admin_client.rpc('exec_sql', {'sql': sql}).execute()
        print("Tabela conversation_sessions: OK")
        
        # Testar inserção
        from supabase import create_client
        client = create_client(url, os.getenv('SUPABASE_ANON_KEY'))
        
        test_data = {
            'phone': '5511999999999',
            'chat_id': 'test_final_' + str(int(__import__('time').time())),
            'contact_name': 'Gabriel Teste',
            'last_intent': 'saudacao',
            'last_message': 'Ola, teste final do sistema'
        }
        
        result = client.table('conversation_sessions').insert(test_data).execute()
        print("Dados de teste inseridos: OK")
        
        # Verificar dados
        result = client.table('conversation_sessions').select('*').execute()
        print(f"Total de registros: {len(result.data)}")
        
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    if create_tables():
        print("\n=== SUCESSO ===")
        print("Tabelas criadas e testadas!")
    else:
        print("\n=== ERRO ===")
        print("Falha na criacao das tabelas")
