"""
Versão simplificada para teste
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Imobi AI CRM", version="0.2.0")

# Configurar templates e static
try:
    templates = Jinja2Templates(directory="templates")
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

@app.get("/")
def read_root():
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "version": "0.2.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "imobi-ai-crm"
    }

@app.get("/dashboard")
def dashboard(request: Request):
    """Dashboard simples"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Imobi AI CRM - Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-8">
            <h1 class="text-3xl font-bold text-center mb-8">🏠 Imobi AI CRM</h1>
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Dashboard</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-blue-50 p-4 rounded">
                        <h3 class="font-medium text-blue-900">Sistema</h3>
                        <p class="text-blue-700">✅ Online</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded">
                        <h3 class="font-medium text-green-900">API</h3>
                        <p class="text-green-700">✅ Funcionando</p>
                    </div>
                    <div class="bg-purple-50 p-4 rounded">
                        <h3 class="font-medium text-purple-900">Agents</h3>
                        <p class="text-purple-700">🤖 Prontos</p>
                    </div>
                </div>
                <div class="mt-6">
                    <h3 class="font-medium mb-2">Links Úteis:</h3>
                    <ul class="space-y-2">
                        <li><a href="/docs" class="text-blue-600 hover:underline">📖 Documentação da API</a></li>
                        <li><a href="/health" class="text-blue-600 hover:underline">🔍 Health Check</a></li>
                        <li><a href="/galeria/teste_local/teste_local_1001" class="text-blue-600 hover:underline">🏠 Exemplo de Galeria</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/docs-simple")
def docs_simple():
    """Documentação simples"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Documentação - Imobi AI CRM</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="container mx-auto py-8">
            <h1 class="text-3xl font-bold text-center mb-8">📖 Documentação</h1>
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Imobi AI CRM</h2>
                <p class="mb-4">Sistema completo de CRM imobiliário com IA para automação de vendas via WhatsApp.</p>
                
                <h3 class="text-lg font-medium mb-2">🎯 Funcionalidades:</h3>
                <ul class="list-disc list-inside space-y-1 mb-6">
                    <li>🤖 Agents de IA (Carol) para atendimento automatizado</li>
                    <li>📱 Integração WhatsApp Business</li>
                    <li>🏠 Gestão de imóveis com galeria de fotos</li>
                    <li>📊 CRM completo com leads e agendamentos</li>
                    <li>📈 Dashboard de gestão</li>
                </ul>
                
                <h3 class="text-lg font-medium mb-2">🔌 Endpoints Principais:</h3>
                <div class="space-y-2">
                    <div class="bg-gray-50 p-3 rounded">
                        <code>GET /</code> - Status da aplicação
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <code>GET /health</code> - Health check
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <code>GET /dashboard</code> - Dashboard principal
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <code>GET /docs</code> - Documentação interativa da API
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
