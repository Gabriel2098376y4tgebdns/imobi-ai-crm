def _parse_float(self, value: str) -> Optional[float]:
    """Converter string para float - VERSÃO CORRIGIDA"""
    if not value:
        return None
    try:
        # Remover apenas pontos que são separadores de milhares
        # Manter vírgula como separador decimal
        clean_value = value.strip()
        
        # Se tem vírgula, é formato brasileiro (123.456,78)
        if ',' in clean_value:
            # Remover pontos (separadores de milhares)
            clean_value = clean_value.replace('.', '')
            # Trocar vírgula por ponto (separador decimal)
            clean_value = clean_value.replace(',', '.')
        # Se não tem vírgula, assumir formato americano (123456.78)
        
        return float(clean_value)
    except (ValueError, TypeError):
        return None
