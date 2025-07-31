"""
Sistema de Automação da Carol
"""

from typing import Dict, List, Any
from datetime import datetime

from services.ai_agents.agents.carol_ai import enviar_mensagem_novos_imoveis
from services.matching.geo_matching import GeoMatchingEngine
from services.crm_integration.crm_connector import CRMConnector


def processar_novos_imoveis_com_carol(cliente_id: str) -> Dict[str, Any]:
    """
    Processar novos imóveis e enviar mensagens via Carol
    """
    print(f"🤖 Carol processando novos imóveis para {cliente_id}")
    
    resultado = {
        "cliente_id": cliente_id,
        "timestamp": datetime.now().isoformat(),
        "leads_contactados": 0,
        "mensagens_enviadas": 0,
        "erros": []
    }
    
    try:
        # 1. Buscar leads ativos para matching
        crm_connector = CRMConnector(cliente_id)
        leads_prontos = crm_connector.verificar_leads_para_matching()
        
        if not leads_prontos:
            resultado["mensagem"] = "Nenhum lead ativo encontrado"
            return resultado
        
        # 2. Para cada lead, buscar imóveis compatíveis
        matching_engine = GeoMatchingEngine(cliente_id)
        
        for lead in leads_prontos:
            try:
                lead_data = lead.to_dict()
                
                # Buscar imóveis compatíveis
                imoveis_matches = []
                
                # Determinar tipos de operação
                tipos_operacao = []
                if lead.interesse_venda:
                    tipos_operacao.append('venda')
                if lead.interesse_locacao:
                    tipos_operacao.append('locacao')
                
                # Buscar para cada tipo de operação
                for tipo_op in tipos_operacao:
                    filtros = {
                        'tipo_imovel': lead.tipo_imovel,
                        'quartos_min': lead.quartos_min,
                        'quartos_max': lead.quartos_max,
                        'vagas_min': lead.vagas_min
                    }
                    
                    if tipo_op == 'venda':
                        filtros.update({
                            'preco_min': lead.orcamento_min_venda,
                            'preco_max': lead.orcamento_max_venda
                        })
                    else:
                        filtros.update({
                            'aluguel_max': lead.orcamento_max_total_mensal
                        })
                    
                    imoveis_proximos = matching_engine.buscar_imoveis_proximos(
                        lat_centro=lead.latitude_centro,
                        lng_centro=lead.longitude_centro,
                        raio_km=lead.raio_busca_km or 3,
                        tipo_operacao=tipo_op,
                        filtros_adicionais=filtros
                    )
                    
                    # Calcular score e filtrar
                    for imovel in imoveis_proximos:
                        score = matching_engine.calcular_score_compatibilidade(imovel, lead_data)
                        if score >= 60:  # Score mínimo para Carol contactar
                            imovel['score_compatibilidade'] = score
                            imoveis_matches.append(imovel)
                
                # Se encontrou matches, enviar mensagem via Carol
                if imoveis_matches:
                    # Ordenar por score e pegar top 3
                    imoveis_matches.sort(key=lambda x: x['score_compatibilidade'], reverse=True)
                    top_matches = imoveis_matches[:3]
                    
                    # Enviar mensagem via Carol
                    resultado_envio = enviar_mensagem_novos_imoveis(
                        cliente_id=cliente_id,
                        lead_data=lead_data,
                        imoveis_matches=top_matches
                    )
                    
                    resultado["leads_contactados"] += 1
                    resultado["mensagens_enviadas"] += 1
                    
                    print(f"✅ Mensagem enviada para {lead.nome} - {len(top_matches)} imóveis")
                
            except Exception as e:
                erro_msg = f"Erro ao processar lead {lead.nome}: {str(e)}"
                resultado["erros"].append(erro_msg)
                print(f"❌ {erro_msg}")
        
        resultado["status"] = "sucesso"
        
    except Exception as e:
        resultado["status"] = "erro"
        resultado["erro_geral"] = str(e)
        print(f"❌ Erro geral na automação: {e}")
    
    return resultado


def executar_rotina_carol_diaria(cliente_id: str) -> Dict[str, Any]:
    """
    Executar rotina diária completa da Carol
    """
    print(f"🌅 Carol iniciando rotina diária para {cliente_id}")
    
    resultado = {
        "cliente_id": cliente_id,
        "timestamp": datetime.now().isoformat(),
        "etapas": {}
    }
    
    try:
        # ETAPA 1: Sincronizar CRM
        print("📱 ETAPA 1: Sincronizando CRM...")
        from services.crm_integration.crm_connector import sincronizar_crm_cliente
        resultado_crm = sincronizar_crm_cliente(cliente_id)
        resultado["etapas"]["crm_sync"] = resultado_crm
        
        # ETAPA 2: Processar novos imóveis com Carol
        print("🤖 ETAPA 2: Carol processando novos imóveis...")
        resultado_carol = processar_novos_imoveis_com_carol(cliente_id)
        resultado["etapas"]["carol_automation"] = resultado_carol
        
        # ETAPA 3: Gerar resumo
        resultado["resumo"] = {
            "leads_sincronizados": resultado_crm.get("leads_processados", 0),
            "leads_contactados_carol": resultado_carol.get("leads_contactados", 0),
            "mensagens_enviadas": resultado_carol.get("mensagens_enviadas", 0),
            "status": "sucesso"
        }
        
        print("✅ Rotina diária da Carol concluída!")
        
    except Exception as e:
        resultado["resumo"] = {
            "status": "erro",
            "erro": str(e)
        }
        print(f"❌ Erro na rotina da Carol: {e}")
    
    return resultado


if __name__ == "__main__":
    # Teste da automação
    resultado = executar_rotina_carol_diaria('teste_local')
    print(f"Resultado da rotina Carol: {resultado}")
