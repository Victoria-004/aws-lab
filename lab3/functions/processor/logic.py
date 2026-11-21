RANGES = {
    "temperature": (-50.0, 60.0),
    "humidity": (0.0, 100.0),
    "light": (0.0, 120000.0),
}
MAX_DELTA = {
    "temperature": 5.0,
    "humidity": 20.0,
    "light": 50000.0,
}
NORMAL_UNITS = {"temperature": "C", "humidity": "%", "light": "lux"}


def _normalize_temperature(value, unit):
    key = unit.replace("°", "").strip().upper()
    if key == "C":
        return value
    if key == "F":
        return (value - 32.0) * 5.0 / 9.0
    if key == "K":
        return value - 273.15
    raise ValueError(f"unsupported temperature unit: {unit!r}")


def _normalize_humidity(value, unit):
    if unit.strip() == "%":
        return value
    raise ValueError(f"unsupported humidity unit: {unit!r}")


def _normalize_light(value, unit):
    key = unit.strip().lower()
    if key == "lux":
        return value
    if key == "klx":
        return value * 1000.0
    raise ValueError(f"unsupported light unit: {unit!r}")


_NORMALIZERS = {
    "temperature": _normalize_temperature,
    "humidity": _normalize_humidity,
    "light": _normalize_light,
}


def process(message, previous_value):
    sensor_type = message["sensor_type"]

    if sensor_type == "camera":
        return {"value_norm": float(message["value"]), "unit_norm": message["unit"],
                "delta": None, "is_anomaly": False, "anomaly_reason": None}

    if sensor_type not in _NORMALIZERS:
        raise ValueError(f"unknown sensor_type: {sensor_type!r}")

    value_norm = _NORMALIZERS[sensor_type](float(message["value"]), message["unit"])
    low, high = RANGES[sensor_type]

    delta = None if previous_value is None else value_norm - previous_value
    reason = None
    if not low <= value_norm <= high:
        reason = "out_of_range"
    elif delta is not None and abs(delta) > MAX_DELTA[sensor_type]:
        reason = "spike"

    return {
        "value_norm": value_norm,
        "unit_norm": NORMAL_UNITS[sensor_type],
        "delta": delta,
        "is_anomaly": reason is not None,
        "anomaly_reason": reason,
    }
