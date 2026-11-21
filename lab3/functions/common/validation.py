import math
import re
from datetime import datetime, timedelta, timezone

SENSOR_TYPES = ("temperature", "humidity", "light", "camera")
SENSOR_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
MAX_OBJECT_KEY_LEN = 255


def parse_iso_utc(value):
    if not isinstance(value, str):
        raise ValueError("must be a string in ISO 8601 format")
    text = value.strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError("is not a valid ISO 8601 timestamp")
    if parsed.tzinfo is None:
        raise ValueError("must include a timezone (use UTC, e.g. 2026-11-20T12:00:00Z)")
    if parsed.utcoffset() != timedelta(0):
        raise ValueError("must be in UTC")
    return parsed.astimezone(timezone.utc)


def format_ts(moment):
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    moment = moment.astimezone(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_measurement(payload):
    errors = []

    def err(field, message):
        errors.append({"field": field, "message": message})

    if not isinstance(payload, dict):
        return None, [{"field": "body", "message": "must be a JSON object"}]

    sensor_id = payload.get("sensor_id")
    if not isinstance(sensor_id, str) or not SENSOR_ID_RE.match(sensor_id):
        err("sensor_id", "required string, 1-64 chars: letters, digits, '_', '.', '-'")

    sensor_type = payload.get("sensor_type")
    if sensor_type not in SENSOR_TYPES:
        err("sensor_type", "must be one of: " + ", ".join(SENSOR_TYPES))

    value = payload.get("value")
    if not _is_number(value):
        err("value", "required finite number")

    unit = payload.get("unit")
    if not isinstance(unit, str) or not unit.strip() or len(unit) > 16:
        err("unit", "required non-empty string, up to 16 chars")

    location = payload.get("location")
    lat = lon = None
    if not isinstance(location, dict):
        err("location", "required object with 'lat' and 'lon'")
    else:
        lat, lon = location.get("lat"), location.get("lon")
        if not _is_number(lat) or not -90 <= lat <= 90:
            err("location.lat", "required number in range -90..90")
        if not _is_number(lon) or not -180 <= lon <= 180:
            err("location.lon", "required number in range -180..180")

    measured_at = None
    try:
        measured_at = parse_iso_utc(payload.get("measured_at"))
    except ValueError as exc:
        err("measured_at", str(exc))

    object_key = payload.get("object_key")
    if sensor_type == "camera":
        prefix = f"camera/{sensor_id}/"
        if (not isinstance(object_key, str) or not isinstance(sensor_id, str)
                or not object_key.startswith(prefix) or len(object_key) > MAX_OBJECT_KEY_LEN):
            err("object_key", "required for camera: key of the uploaded image, 'camera/<sensor_id>/...'")
    elif object_key is not None:
        err("object_key", "allowed only for sensor_type 'camera'")

    if errors:
        return None, errors

    clean = {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "value": value,
        "unit": unit.strip(),
        "location": {"lat": lat, "lon": lon},
        "measured_at": format_ts(measured_at),
    }
    if object_key is not None:
        clean["object_key"] = object_key
    return clean, []
