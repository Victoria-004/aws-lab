import os
import threading

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

# Пул створюється один раз на процес gunicorn. Розмір має бути не меншим за кількість потоків
# воркера (--threads 4), інакше потік не отримає з'єднання. Усього до бази:
# розмір пулу × воркери × задачі (6 × 2 × 4 = 48 при max 4 задачі, ліміт db.t3.micro ≈ 80).
POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '6'))

_pool = None
_pool_lock = threading.Lock()


def _get_pool():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = pooling.MySQLConnectionPool(
                    pool_name='app_pool',
                    pool_size=POOL_SIZE,
                    pool_reset_session=True,
                    host=os.getenv('DB_HOST', 'localhost'),
                    user=os.getenv('DB_USER', 'root'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME', 'lab3_db'),
                    port=int(os.getenv('DB_PORT', '3306')),
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                )
    return _pool


def get_db_connection():
    """Повертає з'єднання з пулу; conn.close() не закриває його, а повертає в пул."""
    return _get_pool().get_connection()
