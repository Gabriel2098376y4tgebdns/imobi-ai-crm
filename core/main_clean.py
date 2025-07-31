from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import get_settings
from core.logger import logger, setup_logging
from datetime import datetime
import uuid

# Configurar settings
settings = get_settings()
setup_logging(settings.log_level, settings.log_file)

app = FastAPI(
    title="Imobi AI CRM",
    description="Sistema de Follow-up Inteligente para Imobiliárias",
    version="0.1.0"
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Imobi AI CRM iniciando...")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Redis: {settings.redis_url}")

@app.get("/")
def read_root():
    logger.info("Endpoint raiz acessado")
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "estrutura": "AI RECOMENDACAO/imobi-ai-crm",
        "environment": settings.environment
    }

@app.get("/health")
def health_check():
    logger.info("Health check realizado")
    return {
        "status": "healthy", 
        "service": "imobi-ai-crm",
        "environment": settings.environment
    }

@app.get("/xml-exemplo")
def get_xml_exemplo():
    return {
        "xml_url": "http://localhost:8000/static/exemplo_imoveis.xml",
        "descricao": "XML de exemplo com 3 imóveis para teste"
    }

# XML Importer
try:
    from services.xml_importer.importer import XMLImporter
    from config.examples.cliente_teste_local import TesteLocalXML
    
    @app.post("/import-xml-local")
    def import_xml_local():
        try:
            config = TesteLocalXML().get_config()
            importer = XMLImporter(
                config['cliente_id'],
                config['xml_url'], 
                config['xml_mapping']
            )
            resultado = importer.import_imoveis()
            return resultado
        except Exception as e:
            logger.error(f"Erro na importação local: {e}")
            return {"erro": str(e)}
            
except ImportError as e:
    logger.warning(f"XML Importer não disponível: {e}")

# Database
try:
    from core.database import create_tables, test_connection, get_db_session
    from models.imovel import Imovel
    
    @app.post("/database/create-tables")
    def create_database_tables():
        try:
            create_tables()
            return {"status": "Tabelas criadas com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return {"erro": str(e)}
    
    @app.get("/imoveis/{cliente_id}")
    def list_imoveis(cliente_id: str, limit: int = 10):
        try:
            with get_db_session() as db:
                imoveis = db.query(Imovel).filter(
                    Imovel.cliente_id == cliente_id,
                    Imovel.status == 'ativo'
                ).limit(limit).all()
                
                return {
                    "cliente_id": cliente_id,
                    "total": len(imoveis),
                    "imoveis": [imovel.to_dict() for imovel in imoveis]
                }
        except Exception as e:
            logger.error(f"Erro ao listar imóveis: {e}")
            return {"erro": str(e)}
            
except ImportError:
    logger.warning("Database não disponível")

# AI Matching (versão simplificada)
try:
    from services.ai_matching.matching_engine import MatchingEngine
    
    @app.post("/test/create-sample-lead")
    def create_sample_lead():
        try:
            # Por ora, apenas simular criação
            lead_id = str(uuid.uuid4())
            
            sample_lead = {
                "lead_id": lead_id,
                "cliente_id": "teste_local",
                "nome": "João Silva",
                "telefone": "(11) 99999-9999",
                "email": "joao.silva@email.com",
                "tipo_imovel": "apartamento",
                "categoria": "venda",
                "orcamento_min": 400000,
                "orcamento_max": 600000,
                "quartos_min": 2,
                "quartos_max": 3,
                "cidades_interesse": ["São Paulo"],
                "bairros_interesse": ["Centro", "Jardins"],
                "observacoes": "Procuro apartamento com boa vista e piscina"
            }
            
            return {
                "status": "sucesso",
                "message": "Lead de teste criado (simulado)",
                "lead_data": sample_lead
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    @app.post("/matching/test-engine")
    def test_matching_engine():
        try:
            engine = MatchingEngine()
            return {
                "status": "sucesso",
                "message": "Engine de matching funcionando",
                "weights": engine.score_weights
            }
        except Exception as e:
            return {"erro": str(e)}
            
except ImportError as e:
    logger.warning(f"AI Matching não disponível: {e}")
    
    @app.post("/test/create-sample-lead")
    def create_sample_lead():
        return {"erro": "Sistema de matching não disponível"}
