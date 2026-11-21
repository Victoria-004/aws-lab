import os
from datetime import datetime, timedelta, timezone

import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config

from common import db
from common.http import api_key_valid, json_response, unauthorized
from common.validation import SENSOR_ID_RE, format_ts, parse_iso_utc

DEFAULT_LIMIT = 100
MAX_LIMIT = 1000
READ_URL_EXPIRES = 900

_s3 = None
_table = None


def _s3_client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client(
            "s3",
            region_name=os.environ["AWS_REGION"],
            config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        )
    return _s3


def _raw_table():
    global _table
    if _table is None:
        _table = boto3.resource("dynamodb").Table(os.environ["RAW_TABLE"])
    return _table


def _read_url(object_key):
    return _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": os.environ["BUCKET"], "Key": object_key},
        ExpiresIn=READ_URL_EXPIRES,
    )


def _parse_params(event):
    params = event.get("queryStringParameters") or {}
    errors = []

    now = datetime.now(timezone.utc)
    to_dt, from_dt = now, None
    if "to" in params:
        try:
            to_dt = parse_iso_utc(params["to"])
        except ValueError as exc:
            errors.append({"field": "to", "message": str(exc)})
    if "from" in params:
        try:
            from_dt = parse_iso_utc(params["from"])
        except ValueError as exc:
            errors.append({"field": "from", "message": str(exc)})
    else:
        from_dt = to_dt - timedelta(hours=1)

    limit = DEFAULT_LIMIT
    if "limit" in params:
        try:
            limit = int(params["limit"])
            if not 1 <= limit <= MAX_LIMIT:
                raise ValueError
        except ValueError:
            errors.append({"field": "limit", "message": f"must be an integer in range 1..{MAX_LIMIT}"})

    source = params.get("source", "sql")
    if source not in ("sql", "nosql"):
        errors.append({"field": "source", "message": "must be 'sql' or 'nosql'"})

    if not errors and from_dt > to_dt:
        errors.append({"field": "from", "message": "must not be later than 'to'"})
    return from_dt, to_dt, limit, source, errors


def _query_sql(sensor_id, from_dt, to_dt, limit):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT message_id, sensor_id, sensor_type, value, unit, value_norm, unit_norm, delta, "
            "is_anomaly, anomaly_reason, lat, lon, measured_at, received_at, object_key "
            "FROM measurements WHERE sensor_id = %s AND measured_at BETWEEN %s AND %s "
            "ORDER BY measured_at DESC LIMIT %s",
            (sensor_id, from_dt.replace(tzinfo=None), to_dt.replace(tzinfo=None), limit),
        )
        rows = cur.fetchall()
    conn.commit()

    items = []
    for (message_id, sid, stype, value, unit, value_norm, unit_norm, delta, is_anomaly, reason,
         lat, lon, measured_at, received_at, object_key) in rows:
        item = {
            "message_id": message_id,
            "sensor_id": sid,
            "sensor_type": stype,
            "value": value,
            "unit": unit,
            "normalized_value": value_norm,
            "normalized_unit": unit_norm,
            "delta": delta,
            "is_anomaly": bool(is_anomaly),
            "anomaly_reason": reason,
            "location": {"lat": lat, "lon": lon},
            "measured_at": format_ts(measured_at),
            "received_at": format_ts(received_at),
        }
        if object_key:
            item["object_key"] = object_key
            item["image_url"] = _read_url(object_key)
        items.append(item)
    return items


def _query_nosql(sensor_id, from_dt, to_dt, limit):
    response = _raw_table().query(
        KeyConditionExpression=Key("sensor_id").eq(sensor_id)
        & Key("measured_at").between(format_ts(from_dt), format_ts(to_dt)),
        ScanIndexForward=False,
        Limit=limit,
    )
    items = []
    for raw in response["Items"]:
        item = {
            "message_id": raw["message_id"],
            "sensor_id": raw["sensor_id"],
            "sensor_type": raw["sensor_type"],
            "value": raw["value"],
            "unit": raw["unit"],
            "location": {"lat": raw["lat"], "lon": raw["lon"]},
            "measured_at": raw["measured_at"],
            "received_at": raw["received_at"],
        }
        if raw.get("object_key"):
            item["object_key"] = raw["object_key"]
            item["image_url"] = _read_url(raw["object_key"])
        items.append(item)
    return items


def _stats():
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT sensor_type, COUNT(*), COALESCE(SUM(is_anomaly), 0), MIN(measured_at), "
                    "MAX(measured_at) FROM measurements GROUP BY sensor_type ORDER BY sensor_type")
        rows = cur.fetchall()
    conn.commit()
    by_type = [{"sensor_type": t, "count": int(n), "anomalies": int(a),
                "first_measured_at": format_ts(first), "last_measured_at": format_ts(last)}
               for t, n, a, first, last in rows]
    return {"total": sum(item["count"] for item in by_type), "by_sensor_type": by_type}


def handler(event, context):
    if not api_key_valid(event):
        return unauthorized()

    if event.get("rawPath", "").rstrip("/") == "/stats":
        return json_response(200, _stats())

    sensor_id = (event.get("pathParameters") or {}).get("sensor_id", "")
    if not SENSOR_ID_RE.match(sensor_id):
        return json_response(400, {"error": "validation failed", "details": [
            {"field": "sensor_id", "message": "invalid sensor id"}]})

    from_dt, to_dt, limit, source, errors = _parse_params(event)
    if errors:
        return json_response(400, {"error": "validation failed", "details": errors})

    query = _query_sql if source == "sql" else _query_nosql
    return json_response(200, query(sensor_id, from_dt, to_dt, limit))
