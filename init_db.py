import os
import sys
import time

import mysql.connector

SQL_FILE = os.path.join(os.path.dirname(__file__), "app", "data.sql")


def connect():
    for attempt in range(30):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME", "lab3_db"),
                port=int(os.getenv("DB_PORT", "3306")),
                charset="utf8mb4",
            )
        except mysql.connector.Error as err:
            print(f"База ще не готова ({attempt + 1}/30): {err}", flush=True)
            time.sleep(5)
    sys.exit("Не вдалося підключитись до бази")


def main():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SHOW TABLES LIKE 'calls'")
    if cur.fetchone():
        print("Таблиці вже існують, пропускаю ініціалізацію", flush=True)
        return

    print("Створюю таблиці з data.sql", flush=True)
    with open(SQL_FILE, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("--")]
    statements = "".join(lines).split(";\n")
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    print("Ініціалізацію завершено", flush=True)


if __name__ == "__main__":
    main()