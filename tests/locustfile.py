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

    @task(3)
    def get_tasks(self):
        self.client.get("/tasks/", headers={"Authorization": "Bearer testtoken"})