"""
Endpoints básicos para XML (temporário)
"""
from fastapi import APIRouter

router = APIRouter(prefix="/xml-import", tags=["XML Import"])

@router.get("/status")
def status():
    return {"status": "ok"}
