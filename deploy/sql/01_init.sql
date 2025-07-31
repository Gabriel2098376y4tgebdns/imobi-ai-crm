-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar schema principal
CREATE SCHEMA IF NOT EXISTS imobi_ai;

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar usuário se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'imobi_user') THEN
        CREATE ROLE imobi_user LOGIN PASSWORD 'imobi_pass';
    END IF;
END
$$;

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE imobi_ai TO imobi_user;
GRANT ALL PRIVILEGES ON SCHEMA imobi_ai TO imobi_user;
