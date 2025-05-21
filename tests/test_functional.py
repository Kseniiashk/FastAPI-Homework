from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
import pytest
import uuid

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def test_db():
    from app.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.mark.asyncio
async def test_full_task_flow(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    response = client.post("/register/", json={
        "username": username,
        "email": email,
        "password": "password"
    })
    assert response.status_code == 201