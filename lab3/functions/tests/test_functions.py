import importlib.util
import json
from pathlib import Path

import pytest

from common.validation import format_ts, parse_iso_utc, validate_measurement
import logic

FUNCTIONS = Path(__file__).resolve().parents[1]


def load_handler(name):
    spec = importlib.util.spec_from_file_location(f"handler_{name}", FUNCTIONS / name / "handler.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def good(**overrides):
    body = {
        "sensor_id": "temp-01", "sensor_type": "temperature", "value": 21.5, "unit": "C",
        "location": {"lat": 49.84, "lon": 24.03}, "measured_at": "2026-11-20T12:00:00.123Z",
    }
    body.update(overrides)
    return body


def test_valid_message_is_normalized():
    clean, errors = validate_measurement(good(measured_at="2026-11-20T12:00:00+00:00"))
    assert errors == []
    assert clean["measured_at"] == "2026-11-20T12:00:00.000Z"


@pytest.mark.parametrize("field,value", [
    ("sensor_id", ""), ("sensor_id", "bad id!"), ("sensor_type", "pressure"), ("value", "21"),
    ("value", True), ("value", float("nan")), ("unit", ""), ("location", {"lat": 91, "lon": 0}),
    ("location", {"lat": 0}), ("measured_at", "2026-11-20 12:00:00"),
    ("measured_at", "2026-11-20T12:00:00+02:00"), ("measured_at", "yesterday"),
])
def test_invalid_field_is_reported(field, value):
    clean, errors = validate_measurement(good(**{field: value}))
    assert clean is None
    assert errors


def test_missing_fields_are_all_reported():
    _, errors = validate_measurement({})
    assert {e["field"] for e in errors} >= {"sensor_id", "sensor_type", "value", "unit", "location", "measured_at"}


def test_camera_requires_object_key_with_sensor_prefix():
    camera = good(sensor_id="cam-01", sensor_type="camera", value=1000, unit="bytes")
    assert validate_measurement(camera)[1]
    assert validate_measurement({**camera, "object_key": "camera/other/x.png"})[1]
    assert validate_measurement({**camera, "object_key": "camera/cam-01/x.png"})[1] == []
    assert validate_measurement(good(object_key="camera/temp-01/x.png"))[1]


def test_timestamp_helpers_roundtrip():
    moment = parse_iso_utc("2026-11-20T12:00:00.5Z")
    assert format_ts(moment) == "2026-11-20T12:00:00.500Z"


def msg(sensor_type, value, unit):
    return {"sensor_type": sensor_type, "value": value, "unit": unit}


def test_temperature_units_are_converted_to_celsius():
    assert logic.process(msg("temperature", 212, "F"), None)["value_norm"] == pytest.approx(100.0)
    assert logic.process(msg("temperature", 293.15, "K"), None)["value_norm"] == pytest.approx(20.0)


def test_out_of_range_is_anomaly():
    result = logic.process(msg("humidity", 130, "%"), None)
    assert result["is_anomaly"] and result["anomaly_reason"] == "out_of_range"


def test_spike_against_previous_value_is_anomaly():
    assert logic.process(msg("temperature", 30, "C"), 20.0)["anomaly_reason"] == "spike"
    normal = logic.process(msg("temperature", 21, "C"), 20.0)
    assert not normal["is_anomaly"] and normal["delta"] == pytest.approx(1.0)


def test_light_klx_converted_to_lux():
    assert logic.process(msg("light", 2, "klx"), None)["value_norm"] == 2000


@pytest.mark.parametrize("sensor_type,unit", [("temperature", "parsec"), ("humidity", "lux"), ("light", "C")])
def test_unknown_unit_raises(sensor_type, unit):
    with pytest.raises(ValueError):
        logic.process(msg(sensor_type, 1, unit), None)


class FakeSqs:
    def __init__(self):
        self.sent = []

    def send_message(self, **kwargs):
        self.sent.append(kwargs)


@pytest.fixture
def ingest(monkeypatch):
    module = load_handler("ingest")
    fake = FakeSqs()
    module._sqs = fake
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.setenv("QUEUE_URL", "https://sqs.example/queue")
    return module, fake


def event(body, key="secret"):
    return {"headers": {"X-Api-Key": key} if key else {}, "body": json.dumps(body)}


def test_ingest_accepts_valid_message(ingest):
    module, fake = ingest
    response = module.handler(event(good()), None)
    assert response["statusCode"] == 202
    sent = json.loads(fake.sent[0]["MessageBody"])
    assert sent["message_id"] == json.loads(response["body"])["message_id"]
    assert sent["sensor_id"] == "temp-01" and "received_at" in sent


def test_ingest_rejects_bad_key(ingest):
    module, fake = ingest
    assert module.handler(event(good(), key="wrong"), None)["statusCode"] == 401
    assert module.handler(event(good(), key=None), None)["statusCode"] == 401
    assert fake.sent == []


def test_ingest_rejects_invalid_body(ingest):
    module, fake = ingest
    response = module.handler(event(good(value="x")), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"])["details"][0]["field"] == "value"
    assert module.handler({"headers": {"x-api-key": "secret"}, "body": "{not json"}, None)["statusCode"] == 400
    assert fake.sent == []


def test_history_parameters(monkeypatch):
    module = load_handler("history")
    from_dt, to_dt, limit, source, errors = module._parse_params(
        {"queryStringParameters": {"from": "2026-11-20T10:00:00Z", "to": "2026-11-20T11:00:00Z", "limit": "5"}})
    assert errors == [] and limit == 5 and source == "sql" and from_dt < to_dt

    for params in ({"limit": "0"}, {"limit": "abc"}, {"from": "bad"}, {"source": "other"},
                   {"from": "2026-11-21T00:00:00Z", "to": "2026-11-20T00:00:00Z"}):
        assert module._parse_params({"queryStringParameters": params})[4], params


class FakeCursor:
    def __init__(self, db):
        self.db, self.rowcount = db, 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=()):
        if sql.startswith("SELECT"):
            self.row = None
        elif sql.startswith("INSERT IGNORE"):
            message_id = params[0]
            self.rowcount = 0 if message_id in self.db.rows else 1
            self.db.rows.setdefault(message_id, params)

    def fetchone(self):
        return self.row


class FakeDb:
    def __init__(self):
        self.rows = {}

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        pass

    def rollback(self):
        pass


def test_processor_is_idempotent_and_reports_failures(monkeypatch):
    module = load_handler("processor")
    raw_items = []

    class FakeTable:
        def put_item(self, Item):
            raw_items.append(Item)

    module._dynamo_table = FakeTable()
    db = FakeDb()
    monkeypatch.setattr(module.db, "get_connection", lambda: db)

    valid = {**good(), "message_id": "11111111-1111-1111-1111-111111111111",
             "received_at": "2026-11-20T12:00:01.000Z"}
    event_ = {"Records": [
        {"messageId": "a", "body": json.dumps(valid)},
        {"messageId": "b", "body": json.dumps(valid)},
        {"messageId": "c", "body": "not-json"},
        {"messageId": "d", "body": json.dumps({**valid, "sensor_type": "pressure"})},
    ]}
    result = module.handler(event_, None)

    assert len(db.rows) == 1
    assert result["batchItemFailures"] == [{"itemIdentifier": "c"}, {"itemIdentifier": "d"}]


def test_history_stats_route(monkeypatch):
    from datetime import datetime
    module = load_handler("history")
    monkeypatch.setenv("API_KEY", "secret")

    class StatsCursor:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def execute(self, sql, params=()):
            pass

        def fetchall(self):
            return [("temperature", 10, 2, datetime(2026, 11, 20, 12, 0, 0), datetime(2026, 11, 20, 12, 5, 0))]

    class StatsDb:
        def cursor(self):
            return StatsCursor()

        def commit(self):
            pass

    monkeypatch.setattr(module.db, "get_connection", lambda: StatsDb())
    response = module.handler({"rawPath": "/stats", "headers": {"x-api-key": "secret"}}, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200 and body["total"] == 10
    assert body["by_sensor_type"][0]["anomalies"] == 2
    assert module.handler({"rawPath": "/stats", "headers": {}}, None)["statusCode"] == 401
