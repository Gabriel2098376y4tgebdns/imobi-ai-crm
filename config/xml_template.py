"""
Template de configuração XML por cliente
"""

from services.xml_importer.parser import XMLMapping


class ClienteXMLConfig:
    """Configuração XML base para cliente"""
    
    def __init__(self):
        self.cliente_id = "CLIENTE_ID"
        self.nome_cliente = "Nome do Cliente"
        self.xml_url = "https://exemplo.com/imoveis.xml"
        self.ativo = True
        self.horario_importacao = "08:00"
        
    def get_xml_mapping(self) -> XMLMapping:
        """Retornar mapeamento XML específico do cliente"""
        return XMLMapping(
            id_field="id",
            codigo_field="codigo",
            titulo_field="titulo",
            tipo_field="tipo",
            preco_field="preco",
            cidade_field="cidade",
            estado_field="estado",
            categoria_field="categoria",
            endereco_field="endereco",
            bairro_field="bairro",
            cep_field="cep",
            area_total_field="area_total",
            quartos_field="quartos",
            banheiros_field="banheiros",
            vagas_field="vagas",
            descricao_field="descricao",
            fotos_field="fotos",
            status_field="status",
            fotos_separator=",",
            root_element="imoveis",
            item_element="imovel",
            tipo_mapping={
                "apt": "apartamento",
                "casa": "casa",
                "terreno": "terreno",
                "comercial": "comercial"
            },
            status_mapping={
                "A": "ativo",
                "I": "inativo",
                "V": "vendido"
            }
        )
    
    def get_config(self) -> dict:
        """Retornar configuração completa"""
        return {
            'cliente_id': self.cliente_id,
            'nome_cliente': self.nome_cliente,
            'xml_url': self.xml_url,
            'ativo': self.ativo,
            'horario_importacao': self.horario_importacao,
            'xml_mapping': self.get_xml_mapping()
        }
