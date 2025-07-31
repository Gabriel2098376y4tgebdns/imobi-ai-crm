"""
Serviço principal de importação XML
"""

from typing import Dict, List, Any
from datetime import datetime
import uuid
import time
from core.logger import logger
from services.xml_importer.parser import XMLParser, XMLMapping


class XMLImporter:
    """Serviço de importação XML"""
    
    def __init__(self, cliente_id: str, xml_url: str, xml_mapping: XMLMapping):
        self.cliente_id = cliente_id
        self.xml_url = xml_url
        self.xml_mapping = xml_mapping
        self.parser = XMLParser(xml_mapping)
        
    def import_imoveis(self) -> Dict[str, Any]:
        """Importar imóveis do XML"""
        start_time = time.time()
        log_id = str(uuid.uuid4())
        
        logger.info(f"Iniciando importação XML para cliente: {self.cliente_id}")
        
        try:
            # Baixar e parsear XML
            xml_content = self.parser.fetch_xml(self.xml_url)
            imoveis_data = self.parser.parse_xml(xml_content)
            
            # Processar imóveis
            resultado = self._process_imoveis(imoveis_data)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Importação concluída: {resultado}")
            return {
                'status': 'sucesso',
                'log_id': log_id,
                'tempo_execucao': execution_time,
                **resultado
            }
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Erro na importação: {error_msg}")
            
            return {
                'status': 'erro',
                'log_id': log_id,
                'erro': error_msg,
                'tempo_execucao': execution_time
            }
    
    def _process_imoveis(self, imoveis_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Processar lista de imóveis"""
        stats = {
            'total_imoveis': len(imoveis_data),
            'imoveis_novos': 0,
            'imoveis_atualizados': 0,
            'imoveis_removidos': 0,
            'erros': 0
        }
        
        try:
            from core.database import get_db_session
            from models.imovel import Imovel
            
            with get_db_session() as db:
                # IDs dos imóveis no XML atual
                xml_imovel_ids = set()
                
                for imovel_data in imoveis_data:
                    try:
                        imovel_id = f"{self.cliente_id}_{imovel_data['id']}"
                        xml_imovel_ids.add(imovel_id)
                        
                        # Buscar imóvel existente
                        existing_imovel = db.query(Imovel).filter(
                            Imovel.id == imovel_id
                        ).first()
                        
                        if existing_imovel:
                            # Verificar se houve mudanças
                            if existing_imovel.hash_xml != imovel_data['hash_xml']:
                                self._update_imovel(existing_imovel, imovel_data)
                                stats['imoveis_atualizados'] += 1
                                logger.debug(f"Imóvel atualizado: {imovel_id}")
                        else:
                            # Criar novo imóvel
                            self._create_imovel(db, imovel_id, imovel_data)
                            stats['imoveis_novos'] += 1
                            logger.debug(f"Novo imóvel criado: {imovel_id}")
                            
                    except Exception as e:
                        stats['erros'] += 1
                        logger.error(f"Erro ao processar imóvel {imovel_data.get('id', 'unknown')}: {e}")
                
                # Remover imóveis que não estão mais no XML
                stats['imoveis_removidos'] = self._remove_missing_imoveis(db, xml_imovel_ids)
                
        except ImportError:
            logger.warning("Banco de dados não disponível - simulando processamento")
            stats['imoveis_novos'] = len(imoveis_data)
        
        return stats
    
    def _create_imovel(self, db, imovel_id: str, imovel_data: Dict[str, Any]):
        """Criar novo imóvel"""
        from models.imovel import Imovel
        
        imovel = Imovel(
            id=imovel_id,
            cliente_id=self.cliente_id,
            codigo_imovel=imovel_data['codigo_imovel'],
            titulo=imovel_data['titulo'],
            tipo=imovel_data['tipo'],
            categoria=imovel_data.get('categoria'),
            preco=imovel_data['preco'],
            endereco=imovel_data.get('endereco'),
            bairro=imovel_data.get('bairro'),
            cidade=imovel_data['cidade'],
            estado=imovel_data['estado'],
            cep=imovel_data.get('cep'),
            area_total=imovel_data.get('area_total'),
            quartos=imovel_data.get('quartos'),
            banheiros=imovel_data.get('banheiros'),
            vagas_garagem=imovel_data.get('vagas_garagem'),
            descricao=imovel_data.get('descricao'),
            fotos=imovel_data.get('fotos', []),
            status=imovel_data.get('status', 'ativo'),
            hash_xml=imovel_data['hash_xml'],
            data_ultima_importacao=imovel_data['data_ultima_importacao']
        )
        
        db.add(imovel)
    
    def _update_imovel(self, imovel, imovel_data: Dict[str, Any]):
        """Atualizar imóvel existente"""
        imovel.titulo = imovel_data['titulo']
        imovel.tipo = imovel_data['tipo']
        imovel.categoria = imovel_data.get('categoria')
        imovel.preco = imovel_data['preco']
        imovel.endereco = imovel_data.get('endereco')
        imovel.bairro = imovel_data.get('bairro')
        imovel.cidade = imovel_data['cidade']
        imovel.estado = imovel_data['estado']
        imovel.cep = imovel_data.get('cep')
        imovel.area_total = imovel_data.get('area_total')
        imovel.quartos = imovel_data.get('quartos')
        imovel.banheiros = imovel_data.get('banheiros')
        imovel.vagas_garagem = imovel_data.get('vagas_garagem')
        imovel.descricao = imovel_data.get('descricao')
        imovel.fotos = imovel_data.get('fotos', [])
        imovel.status = imovel_data.get('status', 'ativo')
        imovel.hash_xml = imovel_data['hash_xml']
        imovel.data_ultima_importacao = imovel_data['data_ultima_importacao']
    
    def _remove_missing_imoveis(self, db, xml_imovel_ids: set) -> int:
        """Remover imóveis que não estão mais no XML"""
        from models.imovel import Imovel
        
        # Buscar todos os imóveis ativos do cliente
        existing_imoveis = db.query(Imovel).filter(
            Imovel.cliente_id == self.cliente_id,
            Imovel.status == 'ativo'
        ).all()
        
        removed_count = 0
        for imovel in existing_imoveis:
            if imovel.id not in xml_imovel_ids:
                imovel.status = 'removido'
                removed_count += 1
                logger.debug(f"Imóvel removido: {imovel.id}")
        
        return removed_count
