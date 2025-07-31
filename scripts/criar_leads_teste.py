"""
Criar leads de teste para demonstrar o matching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db_session
from models.lead_crm_integrado import LeadCRMIntegrado
from datetime import datetime
import uuid

def criar_leads_teste():
    """Criar leads de teste"""
    
    leads_teste = [
        {
            'cliente_id': 'teste_local',
            'crm_lead_id': 'LEAD001',
            'nome': 'João Silva',
            'telefone': '11999999999',
            'email': 'joao@email.com',
            'interesse_venda': True,
            'interesse_locacao': False,
            'operacao_principal': 'venda',
            'status_crm': 'ativo',
            'etapa_crm': 'visita_agendada',
            'latitude_centro': -23.550520,  # Próximo ao centro de SP
            'longitude_centro': -46.633308,
            'raio_busca_km': 3,
            'tipo_imovel': 'apartamento',
            'quartos_min': 2,
            'quartos_max': 4,
            'vagas_min': 1,
            'orcamento_min_venda': 300000,
            'orcamento_max_venda': 500000,
            'aceita_pets_necessario': False
        },
        {
            'cliente_id': 'teste_local',
            'crm_lead_id': 'LEAD002',
            'nome': 'Maria Santos',
            'telefone': '11888888888',
            'email': 'maria@email.com',
            'interesse_venda': False,
            'interesse_locacao': True,
            'operacao_principal': 'locacao',
            'status_crm': 'ativo',
            'etapa_crm': 'atendimento',
            'latitude_centro': -23.560520,  # Próximo aos Jardins
            'longitude_centro': -46.643308,
            'raio_busca_km': 3,
            'tipo_imovel': 'casa',
            'quartos_min': 3,
            'quartos_max': 5,
            'vagas_min': 2,
            'orcamento_max_total_mensal': 4000,
            'aceita_pets_necessario': True,
            'mobiliado_preferencia': 'indiferente'
        },
        {
            'cliente_id': 'teste_local',
            'crm_lead_id': 'LEAD003',
            'nome': 'Carlos Oliveira',
            'telefone': '11777777777',
            'email': 'carlos@email.com',
            'interesse_venda': True,
            'interesse_locacao': True,
            'operacao_principal': 'ambos',
            'status_crm': 'ativo',
            'etapa_crm': 'visita_realizada',
            'latitude_centro': -23.555520,  # Entre centro e jardins
            'longitude_centro': -46.638308,
            'raio_busca_km': 5,
            'tipo_imovel': 'apartamento',
            'quartos_min': 2,
            'quartos_max': 3,
            'vagas_min': 1,
            'orcamento_max_venda': 600000,
            'orcamento_max_total_mensal': 3500,
            'aceita_pets_necessario': False,
            'mobiliado_preferencia': 'nao'
        }
    ]
    
    with get_db_session() as db:
        # Remover leads de teste existentes
        db.query(LeadCRMIntegrado).filter_by(cliente_id='teste_local').delete()
        
        # Criar novos leads
        for lead_data in leads_teste:
            lead = LeadCRMIntegrado(**lead_data)
            db.add(lead)
        
        db.commit()
        print(f"✅ {len(leads_teste)} leads de teste criados")

if __name__ == "__main__":
    criar_leads_teste()
