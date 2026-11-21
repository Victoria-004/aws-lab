import hmac
import json
import os
from decimal import Decimal


def _default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj == obj.to_integral_value() else float(obj)
    raise TypeError(f"Cannot serialize {type(obj)}")


def json_response(status, body):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body, default=_default, ensure_ascii=False),
    }


def api_key_valid(event):
    expected = os.environ.get("API_KEY", "")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    supplied = headers.get("x-api-key", "")
    return bool(expected) and hmac.compare_digest(supplied.encode(), expected.encode())


def unauthorized():
    return json_response(401, {"error": "invalid or missing x-api-key"})
