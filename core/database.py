"""
Configuração do banco de dados
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from core.config import get_settings
from core.logger import logger

settings = get_settings()

# Engine do SQLAlchemy
engine = create_engine(
    settings.database_url,
    echo=False,  # True para debug SQL
    pool_pre_ping=True,
    pool_recycle=300
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db() -> Session:
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager para sessões do banco"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na sessão do banco: {e}")
        raise
    finally:
        db.close()


def create_tables():
    """Criar todas as tabelas"""
    from models.imovel import Base as ImovelBase
    
    try:
        ImovelBase.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise


def test_connection():
    """Testar conexão com banco"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("Conexão com banco OK")
            return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False

# Importar novos modelos
try:
    from models.lead import Lead, Matching
    logger.info("Modelos de Lead e Matching importados com sucesso")
except ImportError as e:
    logger.warning(f"Erro ao importar modelos de Lead: {e}")

# Importar modelo Cliente
try:
    from models.cliente import Cliente
    logger.info("Modelo Cliente importado com sucesso")
except ImportError as e:
    logger.warning(f"Erro ao importar modelo Cliente: {e}")
