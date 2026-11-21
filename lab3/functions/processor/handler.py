import json
import os
from decimal import Decimal

import boto3

from common import db
from common.validation import format_ts, parse_iso_utc, validate_measurement
from logic import process

_dynamo_table = None
_s3 = None


def _table():
    global _dynamo_table
    if _dynamo_table is None:
        _dynamo_table = boto3.resource("dynamodb").Table(os.environ["RAW_TABLE"])
    return _dynamo_table


def _s3_client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client("s3")
    return _s3


def _naive_utc(timestamp):
    return parse_iso_utc(timestamp).replace(tzinfo=None)


def _previous_value(cur, message):
    cur.execute(
        "SELECT value_norm FROM measurements "
        "WHERE sensor_id = %s AND sensor_type = %s AND measured_at < %s "
        "ORDER BY measured_at DESC LIMIT 1",
        (message["sensor_id"], message["sensor_type"], _naive_utc(message["measured_at"])),
    )
    row = cur.fetchone()
    return None if row is None else row[0]


def _store_sql(conn, message, result):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT IGNORE INTO measurements (message_id, sensor_id, sensor_type, value, unit, "
            "value_norm, unit_norm, delta, is_anomaly, anomaly_reason, lat, lon, measured_at, "
            "received_at, object_key) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (message["message_id"], message["sensor_id"], message["sensor_type"], message["value"],
             message["unit"], result["value_norm"], result["unit_norm"], result["delta"],
             int(result["is_anomaly"]), result["anomaly_reason"], message["location"]["lat"],
             message["location"]["lon"], _naive_utc(message["measured_at"]),
             _naive_utc(message["received_at"]), message.get("object_key")),
        )
        inserted = cur.rowcount == 1
    conn.commit()
    return inserted


def _store_raw(message):
    item = {
        "sensor_id": message["sensor_id"],
        "measured_at": message["measured_at"],
        "message_id": message["message_id"],
        "sensor_type": message["sensor_type"],
        "value": Decimal(str(message["value"])),
        "unit": message["unit"],
        "lat": Decimal(str(message["location"]["lat"])),
        "lon": Decimal(str(message["location"]["lon"])),
        "received_at": message["received_at"],
    }
    if message.get("object_key"):
        item["object_key"] = message["object_key"]
    _table().put_item(Item=item)


def process_record(conn, body):
    message, errors = validate_measurement(body)
    if errors:
        raise ValueError(f"invalid message: {errors}")
    message["message_id"] = body.get("message_id")
    if not isinstance(message["message_id"], str) or len(message["message_id"]) != 36:
        raise ValueError("invalid message: message_id must be a UUID string")
    try:
        message["received_at"] = format_ts(parse_iso_utc(body.get("received_at")))
    except ValueError as exc:
        raise ValueError(f"invalid message: received_at {exc}")

    if message["sensor_type"] == "camera":
        _s3_client().head_object(Bucket=os.environ["BUCKET"], Key=message["object_key"])

    with conn.cursor() as cur:
        previous = _previous_value(cur, message)
    result = process(message, previous)

    inserted = _store_sql(conn, message, result)
    _store_raw(message)
    return message, result, inserted


def handler(event, context):
    conn = db.get_connection()
    failures = []
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            message, result, inserted = process_record(conn, body)
            print(json.dumps({
                "status": "stored" if inserted else "duplicate",
                "message_id": message["message_id"],
                "sensor_id": message["sensor_id"],
                "sensor_type": message["sensor_type"],
                "anomaly": result["anomaly_reason"],
            }))
        except Exception as exc:
            try:
                conn.rollback()
            except Exception:
                pass
            print(json.dumps({
                "status": "failed",
                "sqs_message_id": record.get("messageId"),
                "receive_count": record.get("attributes", {}).get("ApproximateReceiveCount"),
                "error": f"{type(exc).__name__}: {exc}",
            }))
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
