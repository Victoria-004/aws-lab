import json
import logging
import os

import redis

from app.my_project.utils.redis_client import get_redis

log = logging.getLogger(__name__)

CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'false').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '45'))
CACHE_INVALIDATE = os.getenv('CACHE_INVALIDATE', 'false').lower() == 'true'

HITS_KEY = 'stats:cache_hits'
MISSES_KEY = 'stats:cache_misses'


def _client():
    return get_redis() if CACHE_ENABLED else None


def get_or_load(key, loader):
    """Cache-aside: повертає дані з кешу, а якщо їх немає — читає з бази і кладе в кеш на CACHE_TTL секунд."""
    client = _client()
    if client is None:
        return loader()

    try:
        cached = client.get(key)
        if cached is not None:
            client.incr(HITS_KEY)
            return json.loads(cached)
        client.incr(MISSES_KEY)
    except redis.RedisError as err:
        # Кеш недоступний — сервіс працює далі, читаючи з бази
        log.warning("Redis недоступний, читаю з бази: %s", err)
        return loader()

    data = loader()
    try:
        client.set(key, json.dumps(data, ensure_ascii=False), ex=CACHE_TTL)
    except redis.RedisError as err:
        log.warning("Не вдалося записати в кеш: %s", err)
    return data


def invalidate(key):
    """Видаляє запис із кешу після зміни даних, якщо увімкнено CACHE_INVALIDATE."""
    client = _client()
    if client is None or not CACHE_INVALIDATE:
        return
    try:
        client.delete(key)
    except redis.RedisError as err:
        log.warning("Не вдалося видалити ключ %s з кешу: %s", key, err)


def get_stats():
    client = _client()
    if client is None:
        return {"enabled": False}
    hits = int(client.get(HITS_KEY) or 0)
    misses = int(client.get(MISSES_KEY) or 0)
    total = hits + misses
    return {
        "enabled": True,
        "ttl_seconds": CACHE_TTL,
        "invalidate_on_write": CACHE_INVALIDATE,
        "hits": hits,
        "misses": misses,
        "hit_ratio": round(hits / total, 4) if total else None,
    }


def reset_stats():
    client = _client()
    if client is not None:
        client.delete(HITS_KEY, MISSES_KEY)
