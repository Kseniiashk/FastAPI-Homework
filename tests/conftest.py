import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Task

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="fakehashedpass"
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # Refresh to ensure ID is populated
    return user

@pytest.fixture(scope="function")
def test_task(db, test_user):
    task = Task(
        title="Test Task",
        description="Test Description",
        status="в ожидании",
        priority=3,
        owner_id=test_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task