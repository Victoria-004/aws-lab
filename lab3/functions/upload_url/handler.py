import json
import os
import re
import uuid

import boto3
from botocore.config import Config

from common.http import api_key_valid, json_response, unauthorized

SENSOR_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
CONTENT_TYPE = "image/png"
EXPIRES_IN = 600

_s3 = None


def _s3_client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client(
            "s3",
            region_name=os.environ["AWS_REGION"],
            config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        )
    return _s3


def handler(event, context):
    if not api_key_valid(event):
        return unauthorized()

    try:
        payload = json.loads(event.get("body") or "{}")
    except ValueError:
        return json_response(400, {"error": "invalid JSON body"})

    sensor_id = payload.get("sensor_id") if isinstance(payload, dict) else None
    if not isinstance(sensor_id, str) or not SENSOR_ID_RE.match(sensor_id):
        return json_response(400, {"error": "validation failed", "details": [
            {"field": "sensor_id", "message": "required string, 1-64 chars: letters, digits, '_', '.', '-'"}]})

    object_key = f"camera/{sensor_id}/{uuid.uuid4()}.png"
    upload_url = _s3_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": os.environ["BUCKET"], "Key": object_key, "ContentType": CONTENT_TYPE},
        ExpiresIn=EXPIRES_IN,
    )
    return json_response(200, {
        "upload_url": upload_url,
        "object_key": object_key,
        "content_type": CONTENT_TYPE,
        "expires_in": EXPIRES_IN,
    })
