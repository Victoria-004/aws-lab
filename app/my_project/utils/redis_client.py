import os

import redis
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_redis():
    """Спільний клієнт Redis або None, якщо REDIS_HOST не задано."""
    global _client
    host = os.getenv('REDIS_HOST')
    if not host:
        return None
    if _client is None:
        _client = redis.Redis(
            host=host,
            port=int(os.getenv('REDIS_PORT', '6379')),
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
    return _client
