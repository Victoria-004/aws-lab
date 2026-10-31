import random

from locust import HttpUser, between, task

from locust import LoadTestShape

DISTRICT_PAYLOAD = {
    "district_name": "Load test district",
    "city_id": 1,
}


class FireApiUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.district_ids = []
        with self.client.get("/districts", name="GET /districts [init]",
                             catch_response=True) as r:
            if r.status_code == 200:
                self.district_ids = [d["district_id"] for d in r.json()]
            else:
                r.failure(f"init failed: {r.status_code}")

    @task(1)
    def create_then_read(self):
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
            self.district_ids.append(new_id)

        self.client.get(f"/districts/{new_id}",
                        name="GET /districts/[id]")

    @task(2)
    def list_districts(self):
        self.client.get("/districts", name="GET /districts")

    @task(4)
    def get_district(self):
        if not self.district_ids:
            return
        district_id = random.choice(self.district_ids)
        self.client.get(f"/districts/{district_id}",
                        name="GET /districts/[id]")

    @task(3)
    def get_firedepartments(self):
        if not self.district_ids:
            return
        district_id = random.choice(self.district_ids)
        self.client.get(f"/districts/{district_id}/firedepartments",
                        name="GET /districts/[id]/firedepartments")

class StagesShape(LoadTestShape):
    stages = [
        {"duration": 150, "users": 30, "spawn_rate": 0.2},  
        {"duration": 450, "users": 30, "spawn_rate": 0.2},  
        {"duration": 570, "users": 0,  "spawn_rate": 0.5},  
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None  