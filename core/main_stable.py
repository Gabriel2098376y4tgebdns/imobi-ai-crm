from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Imobi AI CRM",
    description="Sistema de Follow-up Inteligente para Imobiliárias",
    version="0.1.0"
)

# Servir arquivos estáticos se diretório existir
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "version": "stable"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "imobi-ai-crm",
        "version": "stable"
    }

@app.get("/xml-exemplo")
def get_xml_exemplo():
    return {
        "xml_url": "http://localhost:8000/static/exemplo_imoveis.xml",
        "descricao": "XML de exemplo com 3 imóveis para teste"
    }

# Importação XML (versão simplificada)
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
            return {"erro": str(e)}
            
except ImportError:
    @app.post("/import-xml-local")
    def import_xml_local():
        return {"erro": "XML Importer não disponível"}

# Database (versão simplificada)
try:
    from core.database import get_db_session
    from models.imovel import Imovel
    
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
            return {"erro": str(e)}
            
except ImportError:
    @app.get("/imoveis/{cliente_id}")
    def list_imoveis(cliente_id: str, limit: int = 10):
        return {"erro": "Database não disponível"}
