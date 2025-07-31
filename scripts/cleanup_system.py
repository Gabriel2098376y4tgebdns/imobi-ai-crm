"""
Script de limpeza do sistema
"""

import os
import shutil
from pathlib import Path

def cleanup_system():
    """Limpar arquivos desnecessários do sistema"""
    
    print("🧹 Iniciando limpeza do sistema...")
    
    # Remover __pycache__
    pycache_dirs = list(Path('.').rglob('__pycache__'))
    for dir_path in pycache_dirs:
        if '.venv' not in str(dir_path):
            print(f"🗑️ Removendo {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
    
    # Remover arquivos .pyc
    pyc_files = list(Path('.').rglob('*.pyc'))
    for file_path in pyc_files:
        if '.venv' not in str(file_path):
            print(f"🗑️ Removendo {file_path}")
            file_path.unlink(missing_ok=True)
    
    # Remover arquivos temporários
    temp_patterns = ['*.tmp', '*.bak', '*.old', '*~']
    for pattern in temp_patterns:
        temp_files = list(Path('.').rglob(pattern))
        for file_path in temp_files:
            if '.venv' not in str(file_path):
                print(f"🗑️ Removendo {file_path}")
                file_path.unlink(missing_ok=True)
    
    print("✅ Limpeza concluída!")

def analyze_file_sizes():
    """Analisar tamanhos de arquivos"""
    
    print("\n📊 ANÁLISE DE TAMANHOS:")
    
    py_files = list(Path('.').rglob('*.py'))
    py_files = [f for f in py_files if '.venv' not in str(f)]
    
    file_sizes = []
    for file_path in py_files:
        try:
            size = file_path.stat().st_size
            lines = len(file_path.read_text(encoding='utf-8').splitlines())
            file_sizes.append((str(file_path), size, lines))
        except:
            continue
    
    # Ordenar por número de linhas
    file_sizes.sort(key=lambda x: x[2], reverse=True)
    
    print("\n📄 ARQUIVOS POR TAMANHO (linhas):")
    for file_path, size, lines in file_sizes[:15]:
        print(f"   {lines:4d} linhas - {size:6d} bytes - {file_path}")
    
    # Arquivos muito pequenos (possíveis vazios)
    small_files = [f for f in file_sizes if f[2] < 10]
    if small_files:
        print("\n⚠️ ARQUIVOS MUITO PEQUENOS (< 10 linhas):")
        for file_path, size, lines in small_files:
            print(f"   {lines:2d} linhas - {file_path}")

if __name__ == "__main__":
    cleanup_system()
    analyze_file_sizes()
