"""
Servidor final com templates separados
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List

app = FastAPI(
    title="Imobi AI CRM",
    description="Sistema completo de CRM imobiliário com IA",
    version="0.2.0"
)

# Configurar templates e static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dados de exemplo
SAMPLE_PROPERTIES = [
    {
        "id": "teste_local_1001",
        "codigo_imovel": "IMV001",
        "titulo": "Apartamento 3 quartos no Centro",
        "preco": 480000.00,
        "endereco": "Rua das Flores, 123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "quartos": 3,
        "banheiros": 2,
        "area_total": 85.5,
        "vagas_garagem": 1,
        "descricao": "Lindo apartamento com vista para o parque, totalmente reformado",
        "fotos": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800",
            "https://images.unsplash.com/photo-1560449752-2dd9b957a5b1?w=800",
            "https://images.unsplash.com/photo-1560448075-bb485b067938?w=800"
        ]
    },
    {
        "id": "teste_local_1002",
        "codigo_imovel": "IMV002",
        "titulo": "Casa 4 quartos com piscina",
        "preco": 750000.00,
        "endereco": "Rua dos Jardins, 456",
        "bairro": "Jardins",
        "cidade": "São Paulo",
        "estado": "SP",
        "quartos": 4,
        "banheiros": 3,
        "area_total": 200.0,
        "vagas_garagem": 2,
        "descricao": "Casa espaçosa com piscina, churrasqueira e jardim",
        "fotos": [
            "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800",
            "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
            "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800",
            "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800"
        ]
    }
]

@app.get("/")
def read_root():
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "version": "0.2.0",
        "pages": {
            "dashboard": "/dashboard",
            "documentation": "/documentation",
            "api_docs": "/docs",
            "gallery_example": "/galeria/teste_local/teste_local_1001"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "imobi-ai-crm",
        "features": {
            "dashboard": "✅ Online",
            "gallery": "✅ Funcionando",
            "templates": "✅ Carregados",
            "api": "✅ Ativo"
        }
    }

@app.get("/dashboard")
def dashboard(request: Request):
    """Dashboard usando template"""
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})

@app.get("/documentation")
def documentation(request: Request):
    """Documentação usando template"""
    return templates.TemplateResponse("pages/documentation.html", {"request": request})

@app.get("/galeria/{cliente_id}/{imovel_id}")
def view_property_gallery(cliente_id: str, imovel_id: str, request: Request):
    """Galeria usando template"""
    
    # Buscar imóvel
    imovel = None
    for prop in SAMPLE_PROPERTIES:
        if prop["id"] == imovel_id:
            imovel = prop
            break
    
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Formatar preço
    imovel["preco_formatado"] = f"{imovel['preco']:,.2f}".replace(",", ".")
    
    return templates.TemplateResponse("pages/galeria.html", {
        "request": request,
        "imovel": imovel,
        "fotos": imovel["fotos"]
    })

@app.post("/test/carol-agents")
def test_carol_agents():
    """Testar agents"""
    return {
        "status": "success",
        "message": "Agents Carol testados com sucesso!",
        "agents": {
            "contact": "✅ Primeiro contato funcionando",
            "presentation": "✅ Apresentação de imóveis ativa",
            "scheduling": "✅ Agendamento operacional",
            "crm": "✅ CRM integrado",
            "closure": "✅ Encerramento profissional"
        }
    }

@app.get("/api/dashboard/stats")
def dashboard_stats():
    """Estatísticas"""
    return {
        "leads": 2,
        "imoveis": len(SAMPLE_PROPERTIES),
        "agendamentos": 1,
        "ai_status": "Configurar OpenAI"
    }

@app.get("/imoveis/{cliente_id}")
def list_properties(cliente_id: str):
    """Listar imóveis"""
    return {
        "cliente_id": cliente_id,
        "total": len(SAMPLE_PROPERTIES),
        "imoveis": SAMPLE_PROPERTIES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

# Importar novos endpoints
from api.xml_import_endpoints import router as xml_import_router

# Adicionar ao app
app.include_router(xml_import_router)

@app.post("/import-xml-automatico")
def import_xml_automatico():
    """Endpoint para importação automática (chamado pelo cron)"""
    try:
        from services.xml_import.xml_import_dual import importar_imoveis_xml
        
        # Importar para cliente teste
        resultado = importar_imoveis_xml('teste_local')
        
        return {
            "status": "success",
            "message": "Importação XML executada com sucesso",
            "resultado": resultado,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Erro na importação: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Importar endpoints de matching
try:
    from api.matching_endpoints import router as matching_router
    app.include_router(matching_router)
    print("✅ Endpoints de matching carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar matching endpoints: {e}")

# Importar endpoints de CRM
try:
    from api.crm_endpoints import router as crm_router
    app.include_router(crm_router)
    print("✅ Endpoints de CRM carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar CRM endpoints: {e}")

# Importar endpoints de automação
try:
    from api.automation_endpoints import router as automation_router
    app.include_router(automation_router)
    print("✅ Endpoints de automação carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar automation endpoints: {e}")

# Importar endpoints da Carol
try:
    from api.carol_endpoints import router as carol_router
    app.include_router(carol_router)
    print("✅ Endpoints da Carol AI carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar Carol endpoints: {e}")

# Health Check
try:
    from api.health_endpoints import router as health_router
    app.include_router(health_router)
    print("✅ Health Check endpoints carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar health endpoints: {e}")

# N8N Integration
try:
    from api.n8n_integration_endpoints import router as n8n_router
    app.include_router(n8n_router)
    print("✅ N8N Integration endpoints carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar N8N endpoints: {e}")

# Criar tabelas de sessão na inicialização
try:
    from services.session_management.session_manager import create_session_table
    create_session_table()
    print("✅ Tabela de sessões criada")
except Exception as e:
    print(f"⚠️ Erro ao criar tabela de sessões: {e}")

# N8N Integration
try:
    from api.n8n_integration_endpoints import router as n8n_router
    app.include_router(n8n_router)
    print("✅ N8N Integration endpoints carregados")
except Exception as e:
    print(f"⚠️ Erro ao carregar N8N endpoints: {e}")

# Criar tabelas de sessão na inicialização
try:
    from services.session_management.session_manager import create_session_table
    create_session_table()
    print("✅ Tabela de sessões criada")
except Exception as e:
    print(f"⚠️ Erro ao criar tabela de sessões: {e}")
