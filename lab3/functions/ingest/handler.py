import base64
import json
import os
import uuid
from datetime import datetime, timezone

import boto3

from common.http import api_key_valid, json_response, unauthorized
from common.validation import format_ts, validate_measurement

MAX_BODY_BYTES = 16 * 1024

_sqs = None


def _sqs_client():
    global _sqs
    if _sqs is None:
        _sqs = boto3.client("sqs")
    return _sqs


def _read_body(event):
    raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    if len(raw.encode("utf-8")) > MAX_BODY_BYTES:
        raise ValueError("body is too large (max 16 KB)")
    return json.loads(raw)


def handler(event, context):
    if not api_key_valid(event):
        return unauthorized()

    try:
        payload = _read_body(event)
    except (ValueError, UnicodeDecodeError) as exc:
        return json_response(400, {"error": "invalid JSON body", "details": [{"field": "body", "message": str(exc)}]})

    message, errors = validate_measurement(payload)
    if errors:
        return json_response(400, {"error": "validation failed", "details": errors})

    message["message_id"] = str(uuid.uuid4())
    message["received_at"] = format_ts(datetime.now(timezone.utc))

    _sqs_client().send_message(
        QueueUrl=os.environ["QUEUE_URL"],
        MessageBody=json.dumps(message, ensure_ascii=False),
    )
    return json_response(202, {"message_id": message["message_id"]})
