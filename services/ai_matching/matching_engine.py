"""
Engine de Matching Inteligente (versão simplificada sem FAISS)
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from core.logger import logger
from core.database import get_db_session
from models.lead import Lead, Matching
from models.imovel import Imovel
import uuid
import json


class MatchingEngine:
    """Engine principal de matching inteligente"""
    
    def __init__(self):
        self.score_weights = {
            'preco': 0.35,        # 35% - Compatibilidade de preço
            'localizacao': 0.25,  # 25% - Localização
            'caracteristicas': 0.25,  # 25% - Características do imóvel
            'ia_semantic': 0.15   # 15% - Análise semântica IA
        }
    
    def find_matches_for_lead(self, lead_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Encontrar os melhores matches para um lead
        """
        try:
            logger.info(f"[MATCHING] Iniciando busca de matches para lead: {lead_id}")
            
            with get_db_session() as db:
                # Buscar lead
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
                if not lead:
                    raise ValueError(f"Lead {lead_id} não encontrado")
                
                # Buscar imóveis ativos do mesmo cliente
                imoveis = db.query(Imovel).filter(
                    Imovel.cliente_id == lead.cliente_id,
                    Imovel.status == 'ativo'
                ).all()
                
                if not imoveis:
                    logger.warning(f"[MATCHING] Nenhum imóvel ativo encontrado para cliente {lead.cliente_id}")
                    return []
                
                # Calcular scores para cada imóvel
                matches = []
                for imovel in imoveis:
                    score_data = self._calculate_match_score(lead, imovel)
                    if score_data['score_geral'] > 0.3:  # Threshold mínimo
                        matches.append({
                            'imovel': imovel,
                            'scores': score_data,
                            'lead_id': lead_id
                        })
                
                # Ordenar por score geral
                matches.sort(key=lambda x: x['scores']['score_geral'], reverse=True)
                
                # Limitar resultados
                matches = matches[:limit]
                
                # Salvar matches no banco
                self._save_matches(matches, db)
                
                logger.info(f"[MATCHING] Encontrados {len(matches)} matches para lead {lead_id}")
                return matches
                
        except Exception as e:
            logger.error(f"[MATCHING] Erro ao buscar matches: {e}")
            return []
    
    def _calculate_match_score(self, lead: Lead, imovel: Imovel) -> Dict[str, Any]:
        """
        Calcular score de compatibilidade entre lead e imóvel
        """
        try:
            # Score de preço
            score_preco = self._calculate_price_score(lead, imovel)
            
            # Score de localização
            score_localizacao = self._calculate_location_score(lead, imovel)
            
            # Score de características
            score_caracteristicas = self._calculate_features_score(lead, imovel)
            
            # Score de IA semântica (simplificado)
            score_ia = self._calculate_ai_score(lead, imovel)
            
            # Score geral ponderado
            score_geral = (
                score_preco * self.score_weights['preco'] +
                score_localizacao * self.score_weights['localizacao'] +
                score_caracteristicas * self.score_weights['caracteristicas'] +
                score_ia * self.score_weights['ia_semantic']
            )
            
            # Motivos do match
            motivos = self._generate_match_reasons(lead, imovel, {
                'preco': score_preco,
                'localizacao': score_localizacao,
                'caracteristicas': score_caracteristicas,
                'ia': score_ia
            })
            
            # Pontos de atenção
            pontos_atencao = self._generate_attention_points(lead, imovel)
            
            return {
                'score_geral': round(score_geral, 3),
                'score_preco': round(score_preco, 3),
                'score_localizacao': round(score_localizacao, 3),
                'score_caracteristicas': round(score_caracteristicas, 3),
                'score_ia': round(score_ia, 3),
                'motivos_match': motivos,
                'pontos_atencao': pontos_atencao
            }
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro ao calcular score: {e}")
            return {
                'score_geral': 0.0,
                'score_preco': 0.0,
                'score_localizacao': 0.0,
                'score_caracteristicas': 0.0,
                'score_ia': 0.0,
                'motivos_match': [],
                'pontos_atencao': ['Erro no cálculo de compatibilidade']
            }
    
    def _calculate_price_score(self, lead: Lead, imovel: Imovel) -> float:
        """Calcular score de compatibilidade de preço"""
        try:
            if not lead.orcamento_min or not lead.orcamento_max or not imovel.preco:
                return 0.5  # Score neutro se não há informação
            
            preco_imovel = imovel.preco
            orcamento_min = lead.orcamento_min
            orcamento_max = lead.orcamento_max
            
            # Se está dentro do orçamento
            if orcamento_min <= preco_imovel <= orcamento_max:
                return 1.0
            
            # Se está fora do orçamento
            if preco_imovel < orcamento_min:
                # Abaixo do orçamento - pode ser interessante
                diff_percent = (orcamento_min - preco_imovel) / orcamento_min
                return max(0.7 - diff_percent, 0.0)
            
            # Acima do orçamento - penalizar mais
            diff_percent = (preco_imovel - orcamento_max) / orcamento_max
            return max(0.3 - diff_percent * 2, 0.0)
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro no score de preço: {e}")
            return 0.0
    
    def _calculate_location_score(self, lead: Lead, imovel: Imovel) -> float:
        """Calcular score de compatibilidade de localização"""
        try:
            score = 0.0
            
            # Score por cidade
            if lead.cidades_interesse and imovel.cidade:
                if imovel.cidade.lower() in [c.lower() for c in lead.cidades_interesse]:
                    score += 0.6
                else:
                    score += 0.1
            else:
                score += 0.3
            
            # Score por bairro
            if lead.bairros_interesse and imovel.bairro:
                if imovel.bairro.lower() in [b.lower() for b in lead.bairros_interesse]:
                    score += 0.4
                else:
                    score += 0.1
            else:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro no score de localização: {e}")
            return 0.0
    
    def _calculate_features_score(self, lead: Lead, imovel: Imovel) -> float:
        """Calcular score de características do imóvel"""
        try:
            score = 0.0
            
            # Verificar tipo de imóvel
            if lead.tipo_imovel and imovel.tipo:
                if lead.tipo_imovel.lower() == imovel.tipo.lower():
                    score += 0.3
            
            # Verificar categoria (venda/locação)
            if lead.categoria and imovel.categoria:
                if lead.categoria.lower() == imovel.categoria.lower():
                    score += 0.2
            
            # Verificar quartos
            if lead.quartos_min and imovel.quartos:
                if imovel.quartos >= lead.quartos_min:
                    score += 0.2
            
            # Verificar banheiros
            if lead.banheiros_min and imovel.banheiros:
                if imovel.banheiros >= lead.banheiros_min:
                    score += 0.1
            
            # Verificar área
            if lead.area_min and imovel.area_total:
                if imovel.area_total >= lead.area_min:
                    score += 0.1
            
            # Verificar vagas
            if lead.vagas_min and imovel.vagas_garagem:
                if imovel.vagas_garagem >= lead.vagas_min:
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro no score de características: {e}")
            return 0.0
    
    def _calculate_ai_score(self, lead: Lead, imovel: Imovel) -> float:
        """Calcular score usando análise de texto simples"""
        try:
            score = 0.5  # Score base
            
            # Analisar observações do lead vs descrição do imóvel
            if lead.observacoes and imovel.descricao:
                lead_words = set(lead.observacoes.lower().split())
                imovel_words = set(imovel.descricao.lower().split())
                
                # Palavras-chave importantes
                keywords = {
                    'piscina', 'churrasqueira', 'varanda', 'sacada', 'jardim',
                    'garagem', 'elevador', 'portaria', 'academia', 'playground',
                    'novo', 'reformado', 'mobiliado', 'vista', 'sol'
                }
                
                lead_keywords = lead_words.intersection(keywords)
                imovel_keywords = imovel_words.intersection(keywords)
                
                if lead_keywords and imovel_keywords:
                    match_ratio = len(lead_keywords.intersection(imovel_keywords)) / len(lead_keywords)
                    score = 0.3 + (match_ratio * 0.7)
            
            return score
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro no score de IA: {e}")
            return 0.5
    
    def _generate_match_reasons(self, lead: Lead, imovel: Imovel, scores: Dict[str, float]) -> List[str]:
        """Gerar motivos do match"""
        motivos = []
        
        try:
            if scores['preco'] > 0.8:
                motivos.append("Preço dentro do orçamento ideal")
            
            if scores['localizacao'] > 0.8:
                motivos.append("Localização perfeita")
            
            if scores['caracteristicas'] > 0.8:
                motivos.append("Características ideais do imóvel")
            
            if lead.tipo_imovel and imovel.tipo and lead.tipo_imovel.lower() == imovel.tipo.lower():
                motivos.append(f"Tipo de imóvel desejado: {imovel.tipo}")
            
            return motivos or ["Match encontrado pelo sistema"]
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro ao gerar motivos: {e}")
            return ["Match encontrado pelo sistema"]
    
    def _generate_attention_points(self, lead: Lead, imovel: Imovel) -> List[str]:
        """Gerar pontos de atenção"""
        pontos = []
        
        try:
            # Verificar preço
            if lead.orcamento_max and imovel.preco and imovel.preco > lead.orcamento_max:
                diff_percent = ((imovel.preco - lead.orcamento_max) / lead.orcamento_max) * 100
                pontos.append(f"Preço {diff_percent:.1f}% acima do orçamento máximo")
            
            return pontos
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro ao gerar pontos de atenção: {e}")
            return []
    
    def _save_matches(self, matches: List[Dict[str, Any]], db):
        """Salvar matches no banco de dados"""
        try:
            for match_data in matches:
                imovel = match_data['imovel']
                scores = match_data['scores']
                lead_id = match_data['lead_id']
                
                # Verificar se match já existe
                existing_match = db.query(Matching).filter(
                    Matching.lead_id == lead_id,
                    Matching.imovel_id == imovel.id
                ).first()
                
                if existing_match:
                    # Atualizar match existente
                    existing_match.score_geral = scores['score_geral']
                    existing_match.score_preco = scores['score_preco']
                    existing_match.score_localizacao = scores['score_localizacao']
                    existing_match.score_caracteristicas = scores['score_caracteristicas']
                    existing_match.score_ia = scores['score_ia']
                    existing_match.motivos_match = scores['motivos_match']
                    existing_match.pontos_atencao = scores['pontos_atencao']
                    existing_match.data_atualizacao = datetime.now()
                else:
                    # Criar novo match
                    new_match = Matching(
                        id=str(uuid.uuid4()),
                        lead_id=lead_id,
                        imovel_id=imovel.id,
                        cliente_id=imovel.cliente_id,
                        score_geral=scores['score_geral'],
                        score_preco=scores['score_preco'],
                        score_localizacao=scores['score_localizacao'],
                        score_caracteristicas=scores['score_caracteristicas'],
                        score_ia=scores['score_ia'],
                        motivos_match=scores['motivos_match'],
                        pontos_atencao=scores['pontos_atencao']
                    )
                    db.add(new_match)
            
            logger.info(f"[MATCHING] Salvos {len(matches)} matches no banco")
            
        except Exception as e:
            logger.error(f"[MATCHING] Erro ao salvar matches: {e}")
