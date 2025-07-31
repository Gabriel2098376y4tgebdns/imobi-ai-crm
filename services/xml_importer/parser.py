"""
Parser XML para importação de imóveis
"""

import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from core.logger import logger
import hashlib


@dataclass
class XMLMapping:
    """Mapeamento de campos XML para modelo de dados"""
    id_field: str = "@id"
    codigo_field: str = "codigo"
    titulo_field: str = "titulo"
    tipo_field: str = "tipo"
    categoria_field: str = "categoria"
    preco_field: str = "preco"
    endereco_field: str = "endereco"
    cidade_field: str = "cidade"
    estado_field: str = "estado"
    bairro_field: str = "bairro"
    area_total_field: str = "area_total"
    quartos_field: str = "quartos"
    banheiros_field: str = "banheiros"
    vagas_field: str = "vagas_garagem"
    descricao_field: str = "descricao"
    fotos_field: str = "fotos"
    status_field: str = "status"


class XMLParser:
    """Parser XML configurável para diferentes formatos de CRM"""
    
    def __init__(self, mapping: XMLMapping):
        self.mapping = mapping
        
    def fetch_xml(self, url: str, timeout: int = 30) -> str:
        """Baixar XML de uma URL"""
        try:
            logger.info(f"Baixando XML de: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ImobiAI/1.0)',
                'Accept': 'application/xml, text/xml, */*'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            content = response.text
            logger.info(f"XML baixado com sucesso. Tamanho: {len(content)} chars")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar XML: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar XML: {e}")
            raise
    
    def parse_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parsear XML e extrair dados dos imóveis"""
        try:
            # Parse do XML
            root = ET.fromstring(xml_content)
            
            # Encontrar elementos de imóveis
            imoveis_elements = root.findall('.//imovel')
            
            if not imoveis_elements:
                # Tentar outros padrões comuns
                imoveis_elements = root.findall('.//property') or root.findall('.//item')
            
            logger.info(f"Encontrados {len(imoveis_elements)} imóveis no XML")
            
            imoveis = []
            for element in imoveis_elements:
                try:
                    imovel_data = self._extract_imovel_data(element)
                    if imovel_data:
                        imoveis.append(imovel_data)
                except Exception as e:
                    logger.warning(f"Erro ao processar imóvel: {e}")
                    continue
            
            logger.info(f"Parseados {len(imoveis)} imóveis válidos")
            return imoveis
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no parse: {e}")
            raise
    
    def _extract_imovel_data(self, element: ET.Element) -> Optional[Dict[str, Any]]:
        """Extrair dados de um elemento imóvel"""
        try:
            # ID único (obrigatório)
            imovel_id = self._get_field_value(element, self.mapping.id_field)
            if not imovel_id:
                return None
            
            # Extrair todos os campos
            data = {
                'id_xml': imovel_id,
                'codigo_imovel': self._get_field_value(element, self.mapping.codigo_field),
                'titulo': self._get_field_value(element, self.mapping.titulo_field),
                'tipo': self._get_field_value(element, self.mapping.tipo_field),
                'categoria': self._get_field_value(element, self.mapping.categoria_field, 'venda'),
                'preco': self._parse_float(self._get_field_value(element, self.mapping.preco_field)),
                'endereco': self._get_field_value(element, self.mapping.endereco_field),
                'cidade': self._get_field_value(element, self.mapping.cidade_field),
                'estado': self._get_field_value(element, self.mapping.estado_field),
                'bairro': self._get_field_value(element, self.mapping.bairro_field),
                'area_total': self._parse_float(self._get_field_value(element, self.mapping.area_total_field)),
                'quartos': self._parse_int(self._get_field_value(element, self.mapping.quartos_field)),
                'banheiros': self._parse_int(self._get_field_value(element, self.mapping.banheiros_field)),
                'vagas_garagem': self._parse_int(self._get_field_value(element, self.mapping.vagas_field)),
                'descricao': self._get_field_value(element, self.mapping.descricao_field),
                'fotos': self._parse_fotos(self._get_field_value(element, self.mapping.fotos_field)),
                'status': self._get_field_value(element, self.mapping.status_field, 'ativo')
            }
            
            # Gerar hash para detecção de mudanças
            data['hash_conteudo'] = self._generate_content_hash(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do imóvel: {e}")
            return None
    
    def _get_field_value(self, element: ET.Element, field_path: str, default: str = None) -> Optional[str]:
        """Extrair valor de um campo usando path"""
        try:
            if field_path.startswith('@'):
                # Atributo
                attr_name = field_path[1:]
                return element.get(attr_name, default)
            else:
                # Elemento filho
                child = element.find(field_path)
                if child is not None and child.text:
                    return child.text.strip()
                return default
        except Exception:
            return default
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Converter string para float"""
        if not value:
            return None
        try:
            clean_value = value.strip()
            if "," in clean_value:
                clean_value = clean_value.replace(".", "").replace(",", ".")
            return float(clean_value)
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Converter string para int"""
        if not value:
            return None
        try:
            return int(float(value.strip()))
        except (ValueError, TypeError):
            return None
    
    def _parse_fotos(self, value: str) -> List[str]:
        """Parsear campo de fotos"""
        if not value:
            return []
        
        try:
            # Se for uma string com URLs separadas
            if ',' in value:
                return [url.strip() for url in value.split(',') if url.strip()]
            elif ';' in value:
                return [url.strip() for url in value.split(';') if url.strip()]
            else:
                return [value.strip()] if value.strip() else []
        except Exception:
            return []
    
    def _generate_content_hash(self, data: Dict[str, Any]) -> str:
        """Gerar hash MD5 do conteúdo para detecção de mudanças"""
        try:
            # Campos relevantes para hash (excluir campos de controle)
            relevant_fields = {
                'codigo_imovel', 'titulo', 'tipo', 'categoria', 'preco',
                'endereco', 'cidade', 'estado', 'bairro', 'area_total',
                'quartos', 'banheiros', 'vagas_garagem', 'descricao', 'status'
            }
            
            hash_data = {}
            for field in relevant_fields:
                if field in data and data[field] is not None:
                    hash_data[field] = str(data[field])
            
            # Criar string ordenada para hash consistente
            hash_string = '|'.join(f"{k}:{v}" for k, v in sorted(hash_data.items()))
            
            return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao gerar hash: {e}")
            return hashlib.md5(str(data).encode('utf-8')).hexdigest()
