import os

import pymysql

SCHEMA = """
CREATE TABLE IF NOT EXISTS measurements (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    message_id     CHAR(36)     NOT NULL,
    sensor_id      VARCHAR(64)  NOT NULL,
    sensor_type    VARCHAR(16)  NOT NULL,
    value          DOUBLE       NOT NULL,
    unit           VARCHAR(16)  NOT NULL,
    value_norm     DOUBLE       NOT NULL,
    unit_norm      VARCHAR(16)  NOT NULL,
    delta          DOUBLE       NULL,
    is_anomaly     TINYINT(1)   NOT NULL DEFAULT 0,
    anomaly_reason VARCHAR(64)  NULL,
    lat            DOUBLE       NOT NULL,
    lon            DOUBLE       NOT NULL,
    measured_at    DATETIME(3)  NOT NULL,
    received_at    DATETIME(3)  NOT NULL,
    object_key     VARCHAR(255) NULL,
    UNIQUE KEY uq_message_id (message_id),
    KEY idx_sensor_time (sensor_id, measured_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_connection = None
_schema_ready = False


def _connect():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        connect_timeout=10,
        autocommit=False,
        ssl={"fake_flag_to_enable_tls": True},
    )


def get_connection():
    global _connection, _schema_ready
    if _connection is None:
        _connection = _connect()
    else:
        try:
            _connection.ping(reconnect=True)
        except pymysql.MySQLError:
            _connection = _connect()
    if not _schema_ready:
        with _connection.cursor() as cur:
            cur.execute(SCHEMA)
        _connection.commit()
        _schema_ready = True
    return _connection
