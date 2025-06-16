from locust import HttpUser, task, between
import random


class QuickstartUser(HttpUser):
    host = "http://localhost:8000"

    wait_time = between(1, 2.5)

    def on_start(self):
        response = self.client.post("/token/", data={
            "username": "testuser",
            "password": "password"
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_tasks(self):
        with self.client.get("/tasks/", headers=self.headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Status: {response.status_code}")

    @task
    def create_task(self):
        task_data = {
            "title": f"Task {random.randint(1, 10000)}",
            "description": "Load test",
            "status": random.choice(["в ожидании", "в работе", "завершено"]),
            "priority": random.randint(1, 5)
        }
        self.client.post("/tasks/", json=task_data, headers=self.headers)
