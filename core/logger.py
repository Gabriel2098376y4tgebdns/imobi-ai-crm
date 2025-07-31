import logging
import sys
from pathlib import Path
from loguru import logger

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Configurar sistema de logs estruturados"""
    
    # Remover handler padrão do loguru
    logger.remove()
    
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Formato de log estruturado
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console output
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # File output
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger

# Configurar logs com valores padrão
setup_logging()
