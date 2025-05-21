import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import TaskCreate, UserCreate
from app.database import Base, engine
from sqlalchemy.orm import Session

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    response = client.post("/register/", json=user_data.model_dump())
    return response.json()

@pytest.fixture
def auth_header(test_user):
    client.post("/register/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password"
    })

    auth = client.post("/token/", data={
        "username": "testuser",
        "password": "password"
    })
    token = auth.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_task(auth_header):
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        status="в ожидании",
        priority=3
    )
    response = client.post("/tasks/", json=task_data.model_dump(), headers=auth_header)
    return response.json()


def test_register_user():
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    assert "id" in response.json()


def test_login_valid_user(test_user):
    response = client.post("/token/", data={
        "username": "testuser",
        "password": "password"
    })
    assert response.status_code == 200


def test_create_task(auth_header):
    task_data = {
        "title": "New Task",
        "description": "Description",
        "status": "в работе",
        "priority": 2
    }
    response = client.post("/tasks/", json=task_data, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["title"] == "New Task"


def test_get_tasks(auth_header, test_task):
    response = client.get("/tasks/", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Task"


def test_get_task_by_id(auth_header, test_task):
    task_id = test_task["id"]
    response = client.get(f"/tasks/{task_id}", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_update_task(auth_header, test_task):
    task_id = test_task["id"]
    update_data = {
        "title": "Updated Task",
        "status": "завершено",
        "priority": 5
    }
    response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"


def test_delete_task(auth_header, test_task):
    task_id = test_task["id"]
    response = client.delete(f"/tasks/{task_id}", headers=auth_header)
    assert response.status_code == 200
    response = client.get(f"/tasks/{task_id}", headers=auth_header)
    assert response.status_code == 404


def test_invalid_task_id(auth_header):
    response = client.get("/tasks/999", headers=auth_header)
    assert response.status_code == 404


def test_unauthorized_access():
    response = client.get("/tasks/")
    assert response.status_code == 401


def test_invalid_task_data(auth_header):
    invalid_data = {
        "title": 123,
        "status": "неправильный статус",
        "priority": 100
    }
    response = client.post("/tasks/", json=invalid_data, headers=auth_header)
    assert response.status_code == 422


def test_task_filtering(auth_header):
    tasks = [
        {"title": "Task A", "priority": 5, "status": "в ожидании"},
        {"title": "Task B", "priority": 1, "status": "завершено"},
        {"title": "Important", "priority": 3, "status": "в работе"},
    ]
    for task in tasks:
        client.post("/tasks/", json=task, headers=auth_header)
    response = client.get("/tasks/?sort_by=priority&sort_order=desc", headers=auth_header)
    priorities = [t["priority"] for t in response.json()]
    assert priorities == [5, 3, 1]
    response = client.get("/tasks/?search=Important", headers=auth_header)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Important"


def test_top_priority_tasks(auth_header):
    for i in range(1, 6):
        client.post("/tasks/", json={
            "title": f"Task {i}",
            "priority": i,
            "status": "в ожидании"
        }, headers=auth_header)

    response = client.get("/tasks/top/?limit=3", headers=auth_header)
    assert len(response.json()) == 3
    assert [t["priority"] for t in response.json()] == [5, 4, 3]

def test_register_existing_user():
    response = client.post("/register/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 400

def test_login_invalid_password():
    response = client.post("/token/", data={
        "username": "testuser",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_update_task_invalid_status(auth_header, test_task):
    task_id = test_task["id"]
    response = client.put(f"/tasks/{task_id}", json={
        "title": "Test",
        "status": "invalid",
        "priority": 1
    }, headers=auth_header)
    assert response.status_code == 422