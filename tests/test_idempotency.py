"""Перевірка Idempotency-Key для POST /districts.

Запуск проти локального сервісу (docker compose up):
    pytest tests/test_idempotency.py -v
Проти хмари:
    $env:BASE_URL = "http://labdatabase-alb-470200426.eu-north-1.elb.amazonaws.com"; pytest tests/test_idempotency.py -v

Список GET /districts кешується (TTL 45 с, без інвалідації), тому перед підрахунком записів
тест чекає, поки кеш спливе. Інакше він побачив би застарілий список.
"""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")


def wait_for_fresh_list():
    stats = requests.get(f"{BASE_URL}/cache/stats", timeout=10).json()
    if stats.get("enabled"):
        time.sleep(stats["ttl_seconds"] + 1)


def districts_named(name):
    wait_for_fresh_list()
    response = requests.get(f"{BASE_URL}/districts", timeout=30)
    response.raise_for_status()
    return [d for d in response.json() if d["district_name"] == name]


@pytest.fixture
def created_ids():
    ids = []
    yield ids
    for district_id in set(ids):
        requests.delete(f"{BASE_URL}/districts/{district_id}", timeout=30)


def create(name, city_id, created_ids, key=None):
    headers = {"Idempotency-Key": key} if key else {}
    response = requests.post(f"{BASE_URL}/districts", headers=headers, timeout=30,
                             json={"district_name": name, "city_id": city_id})
    if response.status_code == 201:
        created_ids.append(response.json()["district_id"])
    return response


def test_same_key_creates_one_record(created_ids):
    name = f"idem-{uuid.uuid4().hex[:8]}"
    key = str(uuid.uuid4())

    first = create(name, 1, created_ids, key)
    second = create(name, 1, created_ids, key)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert first.headers["Idempotent-Replayed"] == "false"
    assert second.headers["Idempotent-Replayed"] == "true"
    assert len(districts_named(name)) == 1


def test_same_key_with_different_body_is_rejected(created_ids):
    name = f"idem-{uuid.uuid4().hex[:8]}"
    key = str(uuid.uuid4())

    first = create(name, 1, created_ids, key)
    second = create(name, 2, created_ids, key)

    assert first.status_code == 201
    assert second.status_code == 422
    assert len(districts_named(name)) == 1


def test_without_key_creates_two_records(created_ids):
    name = f"idem-{uuid.uuid4().hex[:8]}"

    first = create(name, 1, created_ids)
    second = create(name, 1, created_ids)

    assert first.json()["district_id"] != second.json()["district_id"]
    assert len(districts_named(name)) == 2
