#!/usr/bin/env python3
"""
Script para criar cliente de exemplo
"""

import requests
import json

# Configuração do cliente
cliente_data = {
    "id": "imobiliaria_exemplo",
    "nome": "Imobiliária Exemplo Ltda",
    "email": "contato@imobiliariaexemplo.com.br",
    "telefone": "(11) 3333-4444",
    "xml_url": "https://www.imobiliariaexemplo.com.br/xml/imoveis.xml",  # ← AQUI VOCÊ COLOCA A URL REAL
    "xml_mapping_config": {
        "id_field": "@id",  # ou "codigo" se não tiver atributo id
        "codigo_field": "codigo",
        "titulo_field": "titulo",
        "tipo_field": "tipo",
        "categoria_field": "categoria",
        "preco_field": "preco",
        "endereco_field": "endereco",
        "cidade_field": "cidade",
        "estado_field": "estado",
        "bairro_field": "bairro",
        "area_total_field": "area_total",
        "quartos_field": "quartos",
        "banheiros_field": "banheiros",
        "vagas_field": "vagas",
        "descricao_field": "descricao",
        "fotos_field": "fotos",
        "status_field": "status"
    },
    "importacao_ativa": True,
    "frequencia_importacao": "diaria",
    "horario_importacao": "08:00",
    "whatsapp_ativo": False,  # Ativar depois
    "ia_ativa": True,
    "score_minimo_match": 0.6,
    "plano": "premium"
}

# Criar cliente via API
try:
    response = requests.post(
        "http://localhost:8000/clientes/",
        json=cliente_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Cliente criado com sucesso!")
        print(f"ID: {result.get('cliente_id')}")
        print(f"Status: {result.get('status')}")
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro na requisição: {e}")
