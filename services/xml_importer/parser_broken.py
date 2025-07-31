"""
Parser XML configurável para diferentes formatos de imobiliárias
"""

import xml.etree.ElementTree as ET
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import hashlib
from datetime import datetime
from core.logger import logger


@dataclass
class XMLMapping:
    """Mapeamento de campos XML para modelo interno"""
    
    # Campos obrigatórios
    id_field: str = "id"
    codigo_field: str = "codigo"
    titulo_field: str = "titulo"
    tipo_field: str = "tipo"
    preco_field: str = "preco"
    cidade_field: str = "cidade"
    estado_field: str = "estado"
    
    # Campos opcionais
    categoria_field: str = "categoria"
    endereco_field: str = "endereco"
    bairro_field: str = "bairro"
    cep_field: str = "cep"
    area_total_field: str = "area_total"
    area_construida: str = "area_construida"
    quartos_field: str = "quartos"
    banheiros_field: str = "banheiros"
    vagas_field: str = "vagas"
    descricao_field: str = "descricao"
    fotos_field: str = "fotos"
    status_field: str = "status"
    
    # Configurações especiais
    fotos_separator: str = ","
    root_element: str = "imoveis"
    item_element: str = "imovel"
    
    # Mapeamento de valores
    tipo_mapping: Dict[str, str] = None
    status_mapping: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tipo_mapping is None:
            self.tipo_mapping = {}
        if self.status_mapping is None:
            self.status_mapping = {}


class XMLParser:
    """Parser XML configurável"""
    
    def __init__(self, mapping: XMLMapping):
        self.mapping = mapping
        
    def fetch_xml(self, url: str, timeout: int = 30) -> str:
        """Baixar XML da URL"""
        try:
            logger.info(f"Baixando XML de: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            content = response.text
            ET.fromstring(content)  # Validar XML
            
            logger.info(f"XML baixado com sucesso. Tamanho: {len(content)} chars")
            return content
            
        except requests.RequestException as e:
            logger.error(f"Erro ao baixar XML: {e}")
            raise
        except ET.ParseError as e:
            logger.error(f"XML inválido: {e}")
            raise
    
    def parse_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parsear XML e retornar lista de imóveis"""
        try:
            root = ET.fromstring(xml_content)
            
            imoveis_root = root.find(self.mapping.root_element)
            if imoveis_root is None:
                imoveis_root = root
            
            imovel_elements = imoveis_root.findall(self.mapping.item_element)
            if not imovel_elements:
                imovel_elements = root.findall(self.mapping.item_element)
            
            logger.info(f"Encontrados {len(imovel_elements)} imóveis no XML")
            
            imoveis = []
            for i, element in enumerate(imovel_elements):
                logger.debug(f"Parseando imóvel {i+1}/{len(imovel_elements)}")
                imovel_data = self._parse_imovel_element(element)
                if imovel_data:
                    imoveis.append(imovel_data)
                    logger.debug(f"Imóvel {i+1} parseado com sucesso: {imovel_data['titulo']}")
                else:
                    logger.warning(f"Imóvel {i+1} falhou no parse")
            
            logger.info(f"Parseados {len(imoveis)} imóveis válidos")
            return imoveis
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no parse XML: {e}")
            raise
    
    def _parse_imovel_element(self, element: ET.Element) -> Optional[Dict[str, Any]]:
        """Parsear elemento individual de imóvel"""
        try:
            imovel = {}
            
            # Debug: mostrar estrutura do elemento
            logger.debug(f"Elemento XML: tag={element.tag}, attrib={element.attrib}")
            
            # Campos obrigatórios
            imovel['id'] = self._get_field_value(element, self.mapping.id_field)
            imovel['codigo_imovel'] = self._get_field_value(element, self.mapping.codigo_field)
            imovel['titulo'] = self._get_field_value(element, self.mapping.titulo_field)
            imovel['tipo'] = self._map_value(
                self._get_field_value(element, self.mapping.tipo_field),
                self.mapping.tipo_mapping
            )
            imovel['preco'] = self._parse_float(self._get_field_value(element, self.mapping.preco_field))
            imovel['cidade'] = self._get_field_value(element, self.mapping.cidade_field)
            imovel['estado'] = self._get_field_value(element, self.mapping.estado_field)
            
            # Debug: mostrar valores extraídos
            logger.debug(f"Valores extraídos: id={imovel['id']}, titulo={imovel['titulo']}, tipo={imovel['tipo']}, preco={imovel['preco']}")
            
            # Validar campos obrigatórios
            if not all([imovel['id'], imovel['titulo'], imovel['tipo'], imovel['preco']]):
                logger.warning(f"Imóvel com campos obrigatórios faltando: id={imovel['id']}, titulo={imovel['titulo']}, tipo={imovel['tipo']}, preco={imovel['preco']}")
                return None
            
            # Campos opcionais
            imovel['categoria'] = self._get_field_value(element, self.mapping.categoria_field)
            imovel['endereco'] = self._get_field_value(element, self.mapping.endereco_field)
            imovel['bairro'] = self._get_field_value(element, self.mapping.bairro_field)
            imovel['cep'] = self._get_field_value(element, self.mapping.cep_field)
            imovel['area_total'] = self._parse_float(self._get_field_value(element, self.mapping.area_total_field))
            imovel['quartos'] = self._parse_int(self._get_field_value(element, self.mapping.quartos_field))
            imovel['banheiros'] = self._parse_int(self._get_field_value(element, self.mapping.banheiros_field))
            imovel['vagas_garagem'] = self._parse_int(self._get_field_value(element, self.mapping.vagas_field))
            imovel['descricao'] = self._get_field_value(element, self.mapping.descricao_field)
            imovel['status'] = self._map_value(
                self._get_field_value(element, self.mapping.status_field, 'ativo'),
                self.mapping.status_mapping
            )
            
            # Parsear fotos
            fotos_str = self._get_field_value(element, self.mapping.fotos_field)
            if fotos_str:
                imovel['fotos'] = [
                    foto.strip() for foto in fotos_str.split(self.mapping.fotos_separator)
                    if foto.strip()
                ]
            else:
                imovel['fotos'] = []
            
            # Gerar hash para detectar mudanças
            imovel['hash_xml'] = self._generate_hash(imovel)
            
            # Timestamp da importação
            imovel['data_ultima_importacao'] = datetime.now()
            
            return imovel
            
        except Exception as e:
            logger.error(f"Erro ao parsear imóvel: {e}")
            return None
    
    def _get_field_value(self, element: ET.Element, field_path: str, default: str = None) -> Optional[str]:
        """Buscar valor de campo no XML"""
        if not field_path:
            return default
            
        try:
            # Se começa com @, é um atributo
            if field_path.startswith('@'):
                attr_name = field_path[1:]
                value = element.get(attr_name, default)
                logger.debug(f"Atributo {attr_name}: {value}")
                return value
            
            # Senão, é um elemento filho
            found = element.find(field_path)
            if found is not None and found.text:
                value = found.text.strip()
                logger.debug(f"Elemento {field_path}: {value}")
                return value
            
            logger.debug(f"Campo {field_path} não encontrado, usando default: {default}")
            return default
            
        except Exception as e:
            logger.debug(f"Erro ao buscar campo {field_path}: {e}")
            return default
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Converter string para float"""
        if not value:
            return None
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
            return None        if not value:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _map_value(self, value: str, mapping: Dict[str, str]) -> str:
        """Mapear valor usando dicionário"""
        if not value or not mapping:
            return value
        return mapping.get(value, value)
    
    def _generate_hash(self, imovel_data: Dict[str, Any]) -> str:
        """Gerar hash MD5 dos dados do imóvel"""
        hash_fields = ['titulo', 'preco', 'endereco', 'area_total', 'quartos', 'banheiros', 'descricao', 'status']
        
        hash_string = ""
        for field in hash_fields:
            value = imovel_data.get(field, '')
            hash_string += f"{field}:{value}|"
        
        return hashlib.md5(hash_string.encode()).hexdigest()
