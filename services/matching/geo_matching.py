"""
Sistema de Matching Geográfico - Busca por proximidade (3km)
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from core.database import get_db_session
from models.imovel_dual import ImovelDual
from models.lead_crm_integrado import LeadCRMIntegrado
from models.configuracao_imobiliaria import ConfiguracaoImobiliaria


class GeoMatchingEngine:
    """
    Motor de matching geográfico para imóveis
    """
    
    def __init__(self, cliente_id: str):
        self.cliente_id = cliente_id
        self.config = self._get_configuracao()
        
    def _get_configuracao(self) -> Optional[ConfiguracaoImobiliaria]:
        """Buscar configuração da imobiliária"""
        with get_db_session() as db:
            return db.query(ConfiguracaoImobiliaria).filter_by(
                cliente_id=self.cliente_id
            ).first()
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcular distância entre dois pontos usando fórmula de Haversine
        Retorna distância em quilômetros
        """
        # Converter graus para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Diferenças
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Fórmula de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        
        return c * r
    
    def buscar_imoveis_proximos(
        self, 
        lat_centro: float, 
        lng_centro: float, 
        raio_km: int = 3,
        tipo_operacao: str = None,
        filtros_adicionais: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar imóveis dentro do raio especificado
        """
        if not self.config:
            return []
        
        # Usar raio da configuração se não especificado
        if raio_km is None:
            raio_km = self.config.raio_busca_km or 3
        
        with get_db_session() as db:
            # Query base
            query = db.query(ImovelDual).filter(
                and_(
                    ImovelDual.cliente_id == self.cliente_id,
                    ImovelDual.ativo == True,
                    ImovelDual.latitude.isnot(None),
                    ImovelDual.longitude.isnot(None)
                )
            )
            
            # Filtrar por tipo de operação se especificado
            if tipo_operacao:
                query = query.filter(ImovelDual.tipo_operacao == tipo_operacao)
            
            # Aplicar filtros adicionais
            if filtros_adicionais:
                if filtros_adicionais.get('tipo_imovel'):
                    query = query.filter(ImovelDual.tipo_imovel == filtros_adicionais['tipo_imovel'])
                
                if filtros_adicionais.get('quartos_min'):
                    query = query.filter(ImovelDual.quartos >= filtros_adicionais['quartos_min'])
                
                if filtros_adicionais.get('quartos_max'):
                    query = query.filter(ImovelDual.quartos <= filtros_adicionais['quartos_max'])
                
                if filtros_adicionais.get('vagas_min'):
                    query = query.filter(ImovelDual.vagas_garagem >= filtros_adicionais['vagas_min'])
                
                # Filtros financeiros para venda
                if tipo_operacao == 'venda':
                    if filtros_adicionais.get('preco_min'):
                        query = query.filter(ImovelDual.preco_venda >= filtros_adicionais['preco_min'])
                    if filtros_adicionais.get('preco_max'):
                        query = query.filter(ImovelDual.preco_venda <= filtros_adicionais['preco_max'])
                
                # Filtros financeiros para locação
                elif tipo_operacao == 'locacao':
                    if filtros_adicionais.get('aluguel_max'):
                        query = query.filter(ImovelDual.valor_total_mensal <= filtros_adicionais['aluguel_max'])
                    
                    if filtros_adicionais.get('mobiliado'):
                        query = query.filter(ImovelDual.mobiliado == filtros_adicionais['mobiliado'])
                    
                    if filtros_adicionais.get('aceita_pets'):
                        query = query.filter(ImovelDual.aceita_pets == True)
            
            # Buscar todos os imóveis que passaram nos filtros
            imoveis = query.all()
            
            # Calcular distância e filtrar por proximidade
            imoveis_proximos = []
            for imovel in imoveis:
                try:
                    distancia = self.calcular_distancia_haversine(
                        lat_centro, lng_centro,
                        float(imovel.latitude), float(imovel.longitude)
                    )
                    
                    if distancia <= raio_km:
                        imovel_dict = imovel.to_dict()
                        imovel_dict['distancia_km'] = round(distancia, 2)
                        imoveis_proximos.append(imovel_dict)
                        
                except Exception as e:
                    print(f"Erro ao calcular distância para imóvel {imovel.codigo_imovel}: {e}")
                    continue
            
            # Ordenar por distância
            imoveis_proximos.sort(key=lambda x: x['distancia_km'])
            
            return imoveis_proximos
    
    def calcular_score_compatibilidade(
        self, 
        imovel: Dict[str, Any], 
        lead_criterios: Dict[str, Any]
    ) -> float:
        """
        Calcular score de compatibilidade entre imóvel e critérios do lead
        Score de 0 a 100
        """
        score = 0.0
        peso_total = 0.0
        
        # PESO 1: Proximidade geográfica (30%)
        peso_proximidade = 30.0
        if 'distancia_km' in imovel:
            # Score inversamente proporcional à distância
            # 0km = 100%, 3km = 0%
            score_proximidade = max(0, 100 - (imovel['distancia_km'] / 3.0 * 100))
            score += score_proximidade * (peso_proximidade / 100)
        peso_total += peso_proximidade
        
        # PESO 2: Faixa de preço (25%)
        peso_preco = 25.0
        if imovel['tipo_operacao'] == 'venda':
            preco = imovel.get('preco_venda', 0)
            preco_min = lead_criterios.get('orcamento_min_venda', 0)
            preco_max = lead_criterios.get('orcamento_max_venda', float('inf'))
            
            if preco_min <= preco <= preco_max:
                score += 100 * (peso_preco / 100)
            elif preco < preco_min:
                # Penalizar menos se estiver abaixo do mínimo
                score += 70 * (peso_preco / 100)
            else:
                # Penalizar mais se estiver acima do máximo
                score += 30 * (peso_preco / 100)
                
        elif imovel['tipo_operacao'] == 'locacao':
            valor_total = imovel.get('valor_total_mensal', 0)
            valor_max = lead_criterios.get('orcamento_max_total_mensal', float('inf'))
            
            if valor_total <= valor_max:
                score += 100 * (peso_preco / 100)
            else:
                # Penalizar proporcionalmente ao excesso
                excesso_percentual = (valor_total - valor_max) / valor_max
                score_preco = max(0, 100 - (excesso_percentual * 100))
                score += score_preco * (peso_preco / 100)
        
        peso_total += peso_preco
        
        # PESO 3: Características obrigatórias (25%)
        peso_caracteristicas = 25.0
        score_caracteristicas = 0
        checks_caracteristicas = 0
        
        # Tipo de imóvel
        if lead_criterios.get('tipo_imovel'):
            checks_caracteristicas += 1
            if imovel.get('tipo_imovel') == lead_criterios['tipo_imovel']:
                score_caracteristicas += 100
        
        # Quartos
        quartos_min = lead_criterios.get('quartos_min', 0)
        quartos_max = lead_criterios.get('quartos_max', float('inf'))
        quartos_imovel = imovel.get('quartos', 0)
        
        if quartos_min > 0 or quartos_max < float('inf'):
            checks_caracteristicas += 1
            if quartos_min <= quartos_imovel <= quartos_max:
                score_caracteristicas += 100
            elif quartos_imovel >= quartos_min:
                # Bonus se tiver mais quartos que o mínimo
                score_caracteristicas += 80
        
        # Vagas
        vagas_min = lead_criterios.get('vagas_min', 0)
        if vagas_min > 0:
            checks_caracteristicas += 1
            vagas_imovel = imovel.get('vagas_garagem', 0)
            if vagas_imovel >= vagas_min:
                score_caracteristicas += 100
        
        # Pets (para locação)
        if imovel['tipo_operacao'] == 'locacao' and lead_criterios.get('aceita_pets_necessario'):
            checks_caracteristicas += 1
            if imovel.get('aceita_pets'):
                score_caracteristicas += 100
        
        if checks_caracteristicas > 0:
            score += (score_caracteristicas / checks_caracteristicas) * (peso_caracteristicas / 100)
        peso_total += peso_caracteristicas
        
        # PESO 4: Características extras (20%)
        peso_extras = 20.0
        score_extras = 0
        checks_extras = 0
        
        # Mobiliado (para locação)
        if imovel['tipo_operacao'] == 'locacao':
            mobiliado_pref = lead_criterios.get('mobiliado_preferencia', 'indiferente')
            if mobiliado_pref != 'indiferente':
                checks_extras += 1
                mobiliado_imovel = imovel.get('mobiliado', 'nao')
                if mobiliado_pref == mobiliado_imovel:
                    score_extras += 100
                elif mobiliado_pref == 'nao' and mobiliado_imovel in ['sim', 'semi']:
                    score_extras += 70  # Aceita mobiliado mesmo preferindo vazio
        
        # Área
        area_min = lead_criterios.get('area_min', 0)
        area_max = lead_criterios.get('area_max', float('inf'))
        area_imovel = imovel.get('area_total', 0)
        
        if area_min > 0 or area_max < float('inf'):
            checks_extras += 1
            if area_min <= area_imovel <= area_max:
                score_extras += 100
        
        if checks_extras > 0:
            score += (score_extras / checks_extras) * (peso_extras / 100)
        peso_total += peso_extras
        
        # Normalizar score final
        if peso_total > 0:
            score_final = (score / peso_total) * 100
        else:
            score_final = 0
        
        return min(100, max(0, score_final))
    
    def buscar_leads_para_matching(
        self, 
        etapas_ativas: List[str] = None
    ) -> List[LeadCRMIntegrado]:
        """
        Buscar leads que estão em etapas ativas para matching
        """
        if not etapas_ativas:
            etapas_ativas = [
                'visita_agendada',
                'visita_realizada', 
                'proposta_enviada',
                'atendimento',
                'negociacao'
            ]
        
        with get_db_session() as db:
            leads = db.query(LeadCRMIntegrado).filter(
                and_(
                    LeadCRMIntegrado.cliente_id == self.cliente_id,
                    LeadCRMIntegrado.ativo == True,
                    LeadCRMIntegrado.etapa_crm.in_(etapas_ativas),
                    LeadCRMIntegrado.latitude_centro.isnot(None),
                    LeadCRMIntegrado.longitude_centro.isnot(None)
                )
            ).all()
            
            return leads
    
    def fazer_matching_completo(self) -> Dict[str, Any]:
        """
        Fazer matching completo: buscar leads ativos e encontrar imóveis compatíveis
        """
        if not self.config or not self.config.auto_matching_ativo:
            return {"erro": "Matching automático não está ativo"}
        
        resultado = {
            "leads_processados": 0,
            "matches_encontrados": 0,
            "matches_por_lead": {},
            "estatisticas": {
                "vendas": {"leads": 0, "matches": 0},
                "locacao": {"leads": 0, "matches": 0}
            }
        }
        
        # Buscar leads ativos
        leads_ativos = self.buscar_leads_para_matching()
        
        for lead in leads_ativos:
            lead_dict = lead.to_dict()
            matches_lead = []
            
            # Determinar tipos de operação para buscar
            tipos_operacao = []
            if lead.interesse_venda and self.config.vendas_ativo:
                tipos_operacao.append('venda')
            if lead.interesse_locacao and self.config.locacao_ativo:
                tipos_operacao.append('locacao')
            
            # Buscar imóveis para cada tipo de operação
            for tipo_op in tipos_operacao:
                # Preparar filtros baseados nos critérios do lead
                filtros = {
                    'tipo_imovel': lead.tipo_imovel,
                    'quartos_min': lead.quartos_min,
                    'quartos_max': lead.quartos_max,
                    'vagas_min': lead.vagas_min,
                    'aceita_pets': lead.aceita_pets_necessario
                }
                
                # Filtros específicos por tipo
                if tipo_op == 'venda':
                    filtros.update({
                        'preco_min': lead.orcamento_min_venda,
                        'preco_max': lead.orcamento_max_venda
                    })
                    resultado["estatisticas"]["vendas"]["leads"] += 1
                    
                elif tipo_op == 'locacao':
                    filtros.update({
                        'aluguel_max': lead.orcamento_max_total_mensal,
                        'mobiliado': lead.mobiliado_preferencia if lead.mobiliado_preferencia != 'indiferente' else None
                    })
                    resultado["estatisticas"]["locacao"]["leads"] += 1
                
                # Buscar imóveis próximos
                imoveis_proximos = self.buscar_imoveis_proximos(
                    lat_centro=lead.latitude_centro,
                    lng_centro=lead.longitude_centro,
                    raio_km=lead.raio_busca_km or self.config.raio_busca_km,
                    tipo_operacao=tipo_op,
                    filtros_adicionais=filtros
                )
                
                # Calcular score de compatibilidade para cada imóvel
                for imovel in imoveis_proximos:
                    score = self.calcular_score_compatibilidade(imovel, lead_dict)
                    imovel['score_compatibilidade'] = round(score, 1)
                    
                    # Só incluir imóveis com score mínimo
                    if score >= 50:  # Score mínimo de 50%
                        matches_lead.append(imovel)
                        
                        if tipo_op == 'venda':
                            resultado["estatisticas"]["vendas"]["matches"] += 1
                        else:
                            resultado["estatisticas"]["locacao"]["matches"] += 1
            
            # Ordenar matches por score (maior primeiro)
            matches_lead.sort(key=lambda x: x['score_compatibilidade'], reverse=True)
            
            # Limitar a top 10 matches
            matches_lead = matches_lead[:10]
            
            if matches_lead:
                resultado["matches_por_lead"][str(lead.id)] = {
                    "lead_info": {
                        "nome": lead.nome,
                        "telefone": lead.telefone,
                        "etapa_crm": lead.etapa_crm,
                        "interesse_venda": lead.interesse_venda,
                        "interesse_locacao": lead.interesse_locacao
                    },
                    "matches": matches_lead,
                    "total_matches": len(matches_lead)
                }
                resultado["matches_encontrados"] += len(matches_lead)
            
            resultado["leads_processados"] += 1
        
        return resultado
    
    def buscar_leads_para_novo_imovel(self, imovel: ImovelDual) -> List[Dict[str, Any]]:
        """
        Buscar leads compatíveis quando um novo imóvel é cadastrado
        """
        if not imovel.latitude or not imovel.longitude:
            return []
        
        # Buscar leads que podem ter interesse neste imóvel
        with get_db_session() as db:
            query = db.query(LeadCRMIntegrado).filter(
                and_(
                    LeadCRMIntegrado.cliente_id == self.cliente_id,
                    LeadCRMIntegrado.ativo == True,
                    LeadCRMIntegrado.latitude_centro.isnot(None),
                    LeadCRMIntegrado.longitude_centro.isnot(None)
                )
            )
            
            # Filtrar por tipo de interesse
            if imovel.tipo_operacao == 'venda':
                query = query.filter(LeadCRMIntegrado.interesse_venda == True)
            else:
                query = query.filter(LeadCRMIntegrado.interesse_locacao == True)
            
            leads = query.all()
        
        leads_compativeis = []
        imovel_dict = imovel.to_dict()
        
        for lead in leads:
            # Calcular distância
            try:
                distancia = self.calcular_distancia_haversine(
                    float(imovel.latitude), float(imovel.longitude),
                    lead.latitude_centro, lead.longitude_centro
                )
                
                raio_busca = lead.raio_busca_km or self.config.raio_busca_km or 3
                
                if distancia <= raio_busca:
                    # Calcular score de compatibilidade
                    imovel_dict['distancia_km'] = round(distancia, 2)
                    score = self.calcular_score_compatibilidade(imovel_dict, lead.to_dict())
                    
                    if score >= 60:  # Score mínimo mais alto para novos imóveis
                        leads_compativeis.append({
                            "lead": lead.to_dict(),
                            "score_compatibilidade": round(score, 1),
                            "distancia_km": round(distancia, 2),
                            "motivo_match": "novo_imovel_cadastrado"
                        })
                        
            except Exception as e:
                print(f"Erro ao processar lead {lead.id}: {e}")
                continue
        
        # Ordenar por score
        leads_compativeis.sort(key=lambda x: x['score_compatibilidade'], reverse=True)
        
        return leads_compativeis


# FUNÇÕES UTILITÁRIAS PARA USO NO SISTEMA

def executar_matching_automatico(cliente_id: str) -> Dict[str, Any]:
    """
    Executar matching automático para um cliente
    """
    print(f"🎯 Executando matching automático para {cliente_id}")
    
    engine = GeoMatchingEngine(cliente_id)
    resultado = engine.fazer_matching_completo()
    
    print(f"📊 Resultado: {resultado['leads_processados']} leads processados, {resultado['matches_encontrados']} matches encontrados")
    
    return resultado


def buscar_leads_para_imovel(cliente_id: str, imovel_id: str) -> List[Dict[str, Any]]:
    """
    Buscar leads compatíveis para um imóvel específico
    """
    with get_db_session() as db:
        imovel = db.query(ImovelDual).filter_by(
            cliente_id=cliente_id,
            id=imovel_id
        ).first()
        
        if not imovel:
            return []
        
        engine = GeoMatchingEngine(cliente_id)
        return engine.buscar_leads_para_novo_imovel(imovel)


if __name__ == "__main__":
    # Teste do sistema
    resultado = executar_matching_automatico('teste_local')
    print(f"Resultado do teste: {resultado}")
