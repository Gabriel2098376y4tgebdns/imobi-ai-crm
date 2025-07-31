    def _parse_float(self, value: str) -> Optional[float]:
        """Converter string para float"""
        if not value:
            return None
        try:
            # Corrigir conversão de preço
            clean_value = value.strip()
            if "," in clean_value:
                clean_value = clean_value.replace(".", "").replace(",", ".")
            return float(clean_value)
        except (ValueError, TypeError):
            return None
