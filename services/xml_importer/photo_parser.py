"""
Parser especializado para fotos de imóveis
"""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse, urljoin
from core.logger import logger


class PhotoParser:
    """Parser especializado para extrair e processar fotos de imóveis"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    
    def parse_photos_from_xml(self, photos_field: str) -> List[str]:
        """Extrair URLs de fotos do campo XML"""
        if not photos_field:
            return []
        
        try:
            # Separadores comuns: vírgula, ponto e vírgula, pipe, quebra de linha
            separators = [',', ';', '|', '\n', '\r\n']
            
            photos = [photos_field]
            
            # Aplicar separadores
            for separator in separators:
                new_photos = []
                for photo in photos:
                    new_photos.extend([p.strip() for p in photo.split(separator) if p.strip()])
                photos = new_photos
            
            # Filtrar URLs válidas
            valid_photos = []
            for photo in photos:
                if self._is_valid_photo_url(photo):
                    valid_photos.append(photo)
            
            logger.info(f"Fotos extraídas: {len(valid_photos)} de {len(photos)} encontradas")
            return valid_photos[:10]  # Máximo 10 fotos
            
        except Exception as e:
            logger.error(f"Erro ao processar fotos: {e}")
            return []
    
    def _is_valid_photo_url(self, url: str) -> bool:
        """Verificar se URL é válida para foto"""
        try:
            parsed = urlparse(url)
            
            # Verificar se tem esquema (http/https)
            if not parsed.scheme:
                return False
            
            # Verificar extensão
            path_lower = parsed.path.lower()
            has_valid_extension = any(path_lower.endswith(ext) for ext in self.supported_formats)
            
            # Ou verificar se contém palavras-chave de imagem
            has_image_keywords = any(keyword in url.lower() for keyword in ['foto', 'image', 'img', 'picture', 'pic'])
            
            return has_valid_extension or has_image_keywords
            
        except Exception:
            return False
    
    def create_photo_gallery_data(self, imovel_data: Dict) -> Dict:
        """Criar dados para galeria de fotos"""
        photos = imovel_data.get('fotos', [])
        
        gallery_data = {
            'imovel_id': imovel_data.get('id'),
            'codigo_imovel': imovel_data.get('codigo_imovel'),
            'titulo': imovel_data.get('titulo'),
            'endereco': imovel_data.get('endereco'),
            'preco': imovel_data.get('preco'),
            'fotos': [
                {
                    'url': photo,
                    'thumbnail': self._generate_thumbnail_url(photo),
                    'alt': f"Foto {i+1} - {imovel_data.get('titulo', 'Imóvel')}"
                }
                for i, photo in enumerate(photos)
            ],
            'total_fotos': len(photos)
        }
        
        return gallery_data
    
    def _generate_thumbnail_url(self, photo_url: str) -> str:
        """Gerar URL de thumbnail (se disponível)"""
        # Muitos portais têm padrões para thumbnails
        thumbnail_patterns = [
            ('_large.', '_thumb.'),
            ('_big.', '_small.'),
            ('/fotos/', '/thumbs/'),
            ('/images/', '/thumbnails/')
        ]
        
        for pattern, replacement in thumbnail_patterns:
            if pattern in photo_url:
                return photo_url.replace(pattern, replacement)
        
        # Se não encontrar padrão, usar a foto original
        return photo_url
