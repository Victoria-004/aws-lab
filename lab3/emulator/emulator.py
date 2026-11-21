import json
import logging
import math
import os
import random
import struct
import sys
import threading
import time
import zlib
from datetime import datetime, timezone

import requests

LOG = logging.getLogger("emulator")

MIN_INTERVAL_MS, MAX_INTERVAL_MS = 20, 100
MIN_CAMERA_S, MAX_CAMERA_S = 10, 30
REQUEST_TIMEOUT = 5
STATS_EVERY_S = 5

PROFILES = {
    "temperature": {"start": 21.0, "unit": "C", "step": 0.15, "min": 15.0, "max": 30.0, "spike": 15.0},
    "humidity": {"start": 45.0, "unit": "%", "step": 0.5, "min": 25.0, "max": 70.0, "spike": 45.0},
    "light": {"start": 400.0, "unit": "lux", "step": 15.0, "min": 50.0, "max": 900.0, "spike": 80000.0},
}
SPIKE_PROBABILITY = 0.005


class Stats:
    def __init__(self):
        self._lock = threading.Lock()
        self.sent = {}
        self.errors = {}

    def ok(self, sensor_id):
        with self._lock:
            self.sent[sensor_id] = self.sent.get(sensor_id, 0) + 1

    def fail(self, sensor_id):
        with self._lock:
            self.errors[sensor_id] = self.errors.get(sensor_id, 0) + 1

    def snapshot(self):
        with self._lock:
            return dict(self.sent), dict(self.errors)

    def line(self):
        sent, errors = self.snapshot()
        parts = [f"{sid}: sent={sent.get(sid, 0)} errors={errors.get(sid, 0)}"
                 for sid in sorted(set(sent) | set(errors))]
        return f"TOTAL sent={sum(sent.values())} errors={sum(errors.values())} | " + "; ".join(parts)


def load_config():
    path = os.environ.get("EMULATOR_CONFIG", os.path.join(os.path.dirname(__file__), "config.json"))
    with open(path, encoding="utf-8-sig") as handle:
        config = json.load(handle)
    config["base_url"] = os.environ.get("EMULATOR_BASE_URL", config.get("base_url", "")).rstrip("/")
    config["api_key"] = os.environ.get("EMULATOR_API_KEY", config.get("api_key", ""))
    config["duration_s"] = float(os.environ.get("EMULATOR_DURATION_S", config.get("duration_s", 0)))
    validate_config(config)
    return config


def validate_config(config):
    if not config["base_url"]:
        raise SystemExit("Не задано base_url (файл конфігурації або EMULATOR_BASE_URL)")
    if not config["api_key"]:
        raise SystemExit("Не задано api_key (файл конфігурації або EMULATOR_API_KEY)")
    if not config.get("sensors"):
        raise SystemExit("У конфігурації немає жодного датчика")
    for sensor in config["sensors"]:
        kind = sensor.get("sensor_type")
        if kind == "camera":
            period = sensor.get("period_s")
            if period is None or not MIN_CAMERA_S <= period <= MAX_CAMERA_S:
                raise SystemExit(f"{sensor.get('sensor_id')}: period_s камери має бути {MIN_CAMERA_S}-{MAX_CAMERA_S} с")
        elif kind in PROFILES:
            interval = sensor.get("interval_ms")
            if interval is None or not MIN_INTERVAL_MS <= interval <= MAX_INTERVAL_MS:
                raise SystemExit(f"{sensor.get('sensor_id')}: interval_ms має бути {MIN_INTERVAL_MS}-{MAX_INTERVAL_MS}")
        else:
            raise SystemExit(f"{sensor.get('sensor_id')}: невідомий sensor_type {kind!r}")


def now_iso():
    moment = datetime.now(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def make_png(width=320, height=240):
    rows = []
    shift = random.randint(0, 255)
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row += bytes(((x + shift) % 256, (y * 2) % 256, (x + y + random.randint(0, 30)) % 256))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")


class SensorThread(threading.Thread):
    def __init__(self, sensor, base_url, api_key, stats, stop_event):
        super().__init__(daemon=True, name=sensor["sensor_id"])
        self.sensor, self.stats, self.stop_event = sensor, stats, stop_event
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key, "content-type": "application/json"})
        self.location = {"lat": sensor["lat"], "lon": sensor["lon"]}
        self.sensor_id = sensor["sensor_id"]
        profile = PROFILES.get(sensor["sensor_type"])
        self.profile, self.value = profile, (profile["start"] if profile else 0.0)

    def next_value(self):
        profile = self.profile
        self.value += random.uniform(-profile["step"], profile["step"])
        self.value = min(max(self.value, profile["min"]), profile["max"])
        value = self.value
        if random.random() < SPIKE_PROBABILITY:
            value += profile["spike"]
        return round(value, 2)

    def post_measurement(self, value, unit, extra=None):
        body = {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor["sensor_type"],
            "value": value,
            "unit": unit,
            "location": self.location,
            "measured_at": now_iso(),
        }
        if extra:
            body.update(extra)
        try:
            response = self.session.post(f"{self.base_url}/ingest", data=json.dumps(body), timeout=REQUEST_TIMEOUT)
            if response.status_code == 202:
                self.stats.ok(self.sensor_id)
            else:
                self.stats.fail(self.sensor_id)
                LOG.warning("%s: %s %s", self.sensor_id, response.status_code, response.text[:200])
        except requests.RequestException as exc:
            self.stats.fail(self.sensor_id)
            LOG.warning("%s: request failed: %s", self.sensor_id, exc)

    def run(self):
        interval = self.sensor["interval_ms"] / 1000.0
        next_at = time.monotonic()
        while not self.stop_event.is_set():
            self.post_measurement(self.next_value(), self.profile["unit"])
            next_at += interval
            delay = next_at - time.monotonic()
            if delay > 0:
                self.stop_event.wait(delay)
            else:
                next_at = time.monotonic()


class CameraThread(SensorThread):
    def upload_image(self):
        response = self.session.post(f"{self.base_url}/camera/upload-url",
                                     data=json.dumps({"sensor_id": self.sensor_id}), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        ticket = response.json()
        image = make_png()
        put = requests.put(ticket["upload_url"], data=image,
                           headers={"content-type": ticket["content_type"]}, timeout=30)
        put.raise_for_status()
        return ticket["object_key"], len(image)

    def run(self):
        period = self.sensor["period_s"]
        while not self.stop_event.is_set():
            try:
                object_key, size = self.upload_image()
                self.post_measurement(size, "bytes", {"object_key": object_key})
            except (requests.RequestException, KeyError, ValueError) as exc:
                self.stats.fail(self.sensor_id)
                LOG.warning("%s: upload failed: %s", self.sensor_id, exc)
            self.stop_event.wait(period)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()
    stats, stop_event = Stats(), threading.Event()

    threads = []
    for sensor in config["sensors"]:
        cls = CameraThread if sensor["sensor_type"] == "camera" else SensorThread
        threads.append(cls(sensor, config["base_url"], config["api_key"], stats, stop_event))

    LOG.info("Старт: %d датчиків, приймач %s", len(threads), config["base_url"])
    started = time.monotonic()
    for thread in threads:
        thread.start()

    duration = config["duration_s"]
    try:
        while True:
            time.sleep(STATS_EVERY_S)
            LOG.info(stats.line())
            if duration and time.monotonic() - started >= duration:
                break
    except KeyboardInterrupt:
        LOG.info("Зупинка за Ctrl+C")
    stop_event.set()
    for thread in threads:
        thread.join(timeout=5)
    LOG.info("Завершено. %s", stats.line())
    sent, errors = stats.snapshot()
    return 1 if sum(errors.values()) and not sum(sent.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
