from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def create_task(self):
        self.client.post("/tasks/", json={
            "title": "Load Test Task",
            "description": "Test Description",
            "status": "в ожидании",
            "priority": 1
        }, headers={"Authorization": "Bearer testtoken"})

    @task
    def get_tasks(self):
        with self.client.get("/tasks/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Wrong status code: {response.status_code}")
