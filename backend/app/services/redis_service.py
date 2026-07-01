import redis
import json
from typing import Optional, Any

from app.core.config import settings

class RedisService:
    _instance = None
    _in_memory_cache = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, 'initialized'):
            self.client = None
            self.redis_available = False
            try:
                self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                self.client.ping()
                self.redis_available = True
            except (redis.ConnectionError, Exception) as e:
                print(f"Redis connection failed: {e}. Using in-memory cache fallback.")
                self.redis_available = False
            self.initialized = True

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Set a key-value pair with an optional expiration time."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if self.redis_available and self.client:
            try:
                self.client.set(key, value, ex=ex)
            except Exception as e:
                print(f"Redis set failed: {e}. Using in-memory cache.")
                self._in_memory_cache[key] = value
        else:
            self._in_memory_cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        if self.redis_available and self.client:
            try:
                value = self.client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
            except Exception as e:
                print(f"Redis get failed: {e}. Using in-memory cache.")
                return self._in_memory_cache.get(key)
        
        return self._in_memory_cache.get(key)

    def delete(self, key: str):
        """Delete a key."""
        if self.redis_available and self.client:
            try:
                self.client.delete(key)
            except Exception as e:
                print(f"Redis delete failed: {e}. Using in-memory cache.")
                self._in_memory_cache.pop(key, None)
        else:
            self._in_memory_cache.pop(key, None)

def get_redis_service():
    return RedisService()
