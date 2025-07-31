from fastapi import FastAPI
import os

app = FastAPI(title="Imobi AI CRM", version="0.1.0")

@app.get("/")
def read_root():
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "version": "minimal"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "imobi-ai-crm"
    }

@app.get("/test")
def test_endpoint():
    return {
        "message": "Sistema funcionando",
        "python_path": os.sys.executable,
        "working_dir": os.getcwd()
    }
