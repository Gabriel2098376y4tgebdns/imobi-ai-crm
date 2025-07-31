"""
Configuração corrigida para cliente teste local
"""

from services.xml_importer.parser import XMLMapping


class TesteLocalXML:
    """Configuração para cliente de teste local"""
    
    def get_config(self):
        return {
            'cliente_id': 'teste_local',
            'nome': 'Cliente Teste Local',
            'ativo': True,
            'xml_url': 'http://localhost:8000/static/exemplo_imoveis.xml',
            'xml_mapping': XMLMapping(
                id_field="codigo",  # Usar código como ID em vez de @id
                codigo_field="codigo",
                titulo_field="titulo",
                tipo_field="tipo",
                categoria_field="categoria",
                preco_field="preco",
                endereco_field="endereco",
                cidade_field="cidade",
                estado_field="estado",
                bairro_field="bairro",
                area_total_field="area_total",
                quartos_field="quartos",
                banheiros_field="banheiros",
                vagas_field="vagas_garagem",
                descricao_field="descricao",
                fotos_field="fotos",
                status_field="status"
            )
        }
