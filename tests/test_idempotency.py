"""Перевірка Idempotency-Key для POST /districts.

Запуск проти локального сервісу (docker compose up):
    pytest tests/test_idempotency.py -v
Проти хмари:
    $env:BASE_URL = "http://labdatabase-alb-598287063.eu-north-1.elb.amazonaws.com"; pytest tests/test_idempotency.py -v
"""
import os
import uuid

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")


def districts_named(name):
    response = requests.get(f"{BASE_URL}/districts", timeout=30)
    response.raise_for_status()
    return [d for d in response.json() if d["district_name"] == name]


@pytest.fixture
def district_name():
    name = f"idem-{uuid.uuid4().hex[:8]}"
    yield name
    for district in districts_named(name):
        requests.delete(f"{BASE_URL}/districts/{district['district_id']}", timeout=30)


def test_same_key_creates_one_record(district_name):
    key = str(uuid.uuid4())
    payload = {"district_name": district_name, "city_id": 1}
    headers = {"Idempotency-Key": key}

    first = requests.post(f"{BASE_URL}/districts", json=payload, headers=headers, timeout=30)
    second = requests.post(f"{BASE_URL}/districts", json=payload, headers=headers, timeout=30)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert first.headers["Idempotent-Replayed"] == "false"
    assert second.headers["Idempotent-Replayed"] == "true"
    assert len(districts_named(district_name)) == 1


def test_same_key_with_different_body_is_rejected(district_name):
    key = str(uuid.uuid4())
    headers = {"Idempotency-Key": key}

    first = requests.post(f"{BASE_URL}/districts", headers=headers, timeout=30,
                          json={"district_name": district_name, "city_id": 1})
    second = requests.post(f"{BASE_URL}/districts", headers=headers, timeout=30,
                           json={"district_name": district_name, "city_id": 2})

    assert first.status_code == 201
    assert second.status_code == 422
    assert len(districts_named(district_name)) == 1


def test_without_key_creates_two_records(district_name):
    payload = {"district_name": district_name, "city_id": 1}

    requests.post(f"{BASE_URL}/districts", json=payload, timeout=30)
    requests.post(f"{BASE_URL}/districts", json=payload, timeout=30)

    assert len(districts_named(district_name)) == 2
