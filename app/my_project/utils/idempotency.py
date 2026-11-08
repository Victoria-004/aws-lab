import hashlib
import json
import logging
from functools import wraps

import redis
from flask import Response, jsonify, make_response, request

from app.my_project.utils.redis_client import get_redis

log = logging.getLogger(__name__)

IDEMPOTENCY_TTL = 24 * 60 * 60


def idempotent(view):
    """Перший запит із заголовком Idempotency-Key виконується, а його відповідь зберігається в Redis на 24 години.
    Повторний запит із тим самим ключем отримує збережену відповідь без повторного виконання."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        key = request.headers.get('Idempotency-Key')
        client = get_redis()
        if not key or client is None:
            return view(*args, **kwargs)

        redis_key = f"idem:{request.method}:{request.path}:{key}"
        body_hash = hashlib.sha256(request.get_data()).hexdigest()

        try:
            # SET NX: лише один із паралельних запитів займає ключ і виконує операцію
            acquired = client.set(redis_key, json.dumps({"state": "processing", "hash": body_hash}),
                                  nx=True, ex=IDEMPOTENCY_TTL)
            stored = None if acquired else client.get(redis_key)
        except redis.RedisError as err:
            log.warning("Redis недоступний, виконую запит без ідемпотентності: %s", err)
            return view(*args, **kwargs)

        if acquired:
            try:
                response = make_response(view(*args, **kwargs))
            except Exception:
                client.delete(redis_key)
                raise
            if response.status_code >= 500:
                # Помилку сервера не запам'ятовуємо, щоб клієнт міг повторити запит
                client.delete(redis_key)
            else:
                client.set(redis_key, json.dumps({
                    "state": "done",
                    "hash": body_hash,
                    "status": response.status_code,
                    "body": response.get_data(as_text=True),
                    "content_type": response.content_type,
                }), ex=IDEMPOTENCY_TTL)
            response.headers['Idempotent-Replayed'] = 'false'
            return response

        if stored is None:
            # Ключ встиг зникнути між SET NX і GET — просимо клієнта повторити
            return jsonify({"error": "Повторіть запит"}), 409

        record = json.loads(stored)
        if record["hash"] != body_hash:
            return jsonify({"error": "Idempotency-Key уже використано з іншим тілом запиту"}), 422
        if record["state"] == "processing":
            return jsonify({"error": "Запит із цим Idempotency-Key ще виконується"}), 409

        return Response(record["body"], status=record["status"], content_type=record["content_type"],
                        headers={'Idempotent-Replayed': 'true'})

    return wrapper
