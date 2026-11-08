import random

import gevent.pool
import requests
from locust import HttpUser, LoadTestShape, between, events, task

DISTRICT_NAME = "Load test district"
DISTRICT_PAYLOAD = {
    "district_name": DISTRICT_NAME,
    "city_id": 1,
}


@events.test_start.add_listener
def prepare(environment, **kwargs):
    """Перед тестом видаляє райони, створені попередніми прогонами, і скидає статистику кешу,
    щоб усі прогони стартували з однакового стану бази."""
    host = environment.host
    districts = requests.get(f"{host}/districts", timeout=60).json()
    leftovers = [d["district_id"] for d in districts if d["district_name"] == DISTRICT_NAME]
    pool = gevent.pool.Pool(10)
    for district_id in leftovers:
        pool.spawn(requests.delete, f"{host}/districts/{district_id}", timeout=30)
    pool.join()
    print(f"Видалено тестових районів: {len(leftovers)}")
    requests.delete(f"{host}/cache/stats", timeout=10)


@events.test_stop.add_listener
def report_cache(environment, **kwargs):
    stats = requests.get(f"{environment.host}/cache/stats", timeout=10).json()
    print(f"Статистика кешу: {stats}")


class FireApiUser(HttpUser):
    """Цикл одного користувача: 1 запис і 9 читань.
    Район — аналог поста, пожежні частини району — аналог даних автора."""

    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.district_ids = []
        with self.client.get("/districts", name="GET /districts [init]",
                             catch_response=True) as r:
            if r.status_code == 200:
                self.district_ids = [d["district_id"] for d in r.json()
                                     if d["district_name"] != DISTRICT_NAME]
            else:
                r.failure(f"init failed: {r.status_code}")

    def read_random_district(self):
        if self.district_ids:
            self.client.get(f"/districts/{random.choice(self.district_ids)}",
                            name="GET /districts/[id]")

    def read_random_firedepartments(self):
        if self.district_ids:
            self.client.get(f"/districts/{random.choice(self.district_ids)}/firedepartments",
                            name="GET /districts/[id]/firedepartments")

    @task
    def write_then_read(self):
        # 1 запис
        with self.client.post("/districts", json=DISTRICT_PAYLOAD,
                              name="POST /districts",
                              catch_response=True) as r:
            if r.status_code != 201:
                r.failure(f"create failed: {r.status_code}")
                return
            new_id = r.json().get("district_id")
            if new_id is None:
                r.failure("no district_id in create response")
                return
        self.wait()

        # 9 читань
        self.client.get(f"/districts/{new_id}", name="GET /districts/[id] [created]")
        self.wait()
        self.client.get("/districts", name="GET /districts")
        self.wait()
        self.read_random_district()
        self.wait()
        self.read_random_firedepartments()
        self.wait()
        self.read_random_district()
        self.wait()
        self.client.get("/districts", name="GET /districts")
        self.wait()
        self.read_random_firedepartments()
        self.wait()
        self.read_random_district()
        self.wait()
        self.client.get("/districts", name="GET /districts")


class StagesShape(LoadTestShape):
    """Наростання 0→30 за 3 хв, стале навантаження 5 хв, спад 30→0 за 2 хв. Разом 10 хв."""

    stages = [
        {"duration": 180, "users": 30, "spawn_rate": 30 / 180},
        {"duration": 480, "users": 30, "spawn_rate": 30 / 180},
        {"duration": 600, "users": 0, "spawn_rate": 30 / 120},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
