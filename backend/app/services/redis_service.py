import redis
import json
from typing import Optional, Any

class RedisService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, 'initialized'):
            self.client = redis.Redis(host=host, port=port, db=db)
            self.initialized = True

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Set a key-value pair with an optional expiration time."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8')
        return None

    def delete(self, key: str):
        """Delete a key."""
        self.client.delete(key)

def get_redis_service():
    return RedisService()
