import pytest
from unittest.mock import Mock
from datetime import datetime
from app.crud import create_user, create_user_task
from app.schemas import UserCreate, TaskCreate


def test_create_user(mocker):
    mock_db = Mock()
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    mocker.patch("app.auth.get_password_hash", return_value="hashedpass")
    result = create_user(mock_db, user_data)
    assert result.username == "testuser"
    assert result.hashed_password == "hashedpass"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_user_task(mocker):
    mock_db = Mock()
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        status="в ожидании",
        priority=3
    )

    result = create_user_task(mock_db, task_data, user_id=1)

    assert result.title == "Test Task"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()