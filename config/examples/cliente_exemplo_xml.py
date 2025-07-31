"""
Exemplo de configuração XML para cliente específico
"""

from config.xml_template import ClienteXMLConfig
from services.xml_importer.parser import XMLMapping


class ExemploImobiliariaXML(ClienteXMLConfig):
    """Configuração XML para Exemplo Imobiliária"""
    
    def __init__(self):
        super().__init__()
        self.cliente_id = "exemplo_imobiliaria"
        self.nome_cliente = "Exemplo Imobiliária"
        # URL de exemplo que vai dar erro (para teste)
        self.xml_url = "https://httpbin.org/xml"
        self.ativo = True
        self.horario_importacao = "08:00"
    
    def get_xml_mapping(self) -> XMLMapping:
        """Mapeamento específico da Exemplo Imobiliária"""
        return XMLMapping(
            id_field="@id",
            codigo_field="codigo_interno",
            titulo_field="titulo_imovel",
            tipo_field="tipo_propriedade",
            preco_field="valor_venda",
            cidade_field="localizacao/cidade",
            estado_field="localizacao/uf",
            categoria_field="finalidade",
            endereco_field="localizacao/endereco_completo",
            bairro_field="localizacao/bairro",
            cep_field="localizacao/cep",
            area_total_field="caracteristicas/area_total",
            quartos_field="caracteristicas/dormitorios",
            banheiros_field="caracteristicas/banheiros",
            vagas_field="caracteristicas/garagem",
            descricao_field="descricao_completa",
            fotos_field="midias/fotos",
            status_field="situacao",
            fotos_separator=";",
            root_element="imoveis",
            item_element="imovel",
            tipo_mapping={
                "apartamento": "apartamento",
                "casa_terrea": "casa",
                "casa_sobrado": "casa",
                "terreno_urbano": "terreno",
                "sala_comercial": "comercial",
                "loja": "comercial"
            },
            status_mapping={
                "disponivel": "ativo",
                "reservado": "ativo",
                "vendido": "vendido",
                "alugado": "alugado",
                "suspenso": "inativo"
            }
        )
