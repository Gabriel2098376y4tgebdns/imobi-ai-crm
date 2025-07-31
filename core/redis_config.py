import redis
from core.config import get_settings

settings = get_settings()

def get_redis_client():
    try:
        if settings.redis_url:
            return redis.from_url(settings.redis_url, decode_responses=True)
        
        return redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )
    except Exception as e:
        print(f"Erro ao conectar Redis: {e}")
        return None

# Cliente Redis global
redis_client = get_redis_client()
