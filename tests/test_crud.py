import pytest
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import Base, engine
from fastapi import HTTPException

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    return crud.create_user(db, user_data)


@pytest.fixture
def test_task(db: Session, test_user):
    task_data = schemas.TaskCreate(
        title="Test Task",
        description="Test Description",
        status="в ожидании",
        priority=3
    )
    return crud.create_user_task(db, task_data, test_user.id)


def test_create_task(db):
    from app.crud import create_user_task
    from app.schemas import TaskCreate

    task_data = TaskCreate(
        title="Test",
        status="в ожидании",
        priority=3
    )
    task = create_user_task(db, task_data, 1)
    assert task.id is not None


def test_get_existing_task(db: Session, test_task):
    task = crud.get_user_task(db, test_task.id, test_task.owner_id)
    assert task is not None
    assert task.title == "Test Task"


def test_get_nonexistent_task(db: Session, test_user):
    task = crud.get_user_task(db, 999, test_user.id)
    assert task is None


def test_get_tasks_with_filters(db: Session, test_user):
    db.query(models.Task).delete()
    tasks = [
        {"title": "Task 1", "priority": 5, "status": "в ожидании"},
        {"title": "Task 2", "priority": 1, "status": "завершено"},
        {"title": "Important", "priority": 3, "status": "в работе"},
    ]
    for task in tasks:
        crud.create_user_task(db, schemas.TaskCreate(**task), test_user.id)
    sorted_tasks = crud.get_user_tasks(db, test_user.id, sort_by="priority", sort_order="desc")
    assert [t.priority for t in sorted_tasks] == [5, 3, 1]


def test_update_task(db: Session, test_task):
    updated_data = schemas.TaskCreate(
        title="Updated Task",
        description="New Description",
        status="завершено",
        priority=5
    )

    updated_task = crud.update_user_task(
        db,
        task_id=test_task.id,
        task=updated_data,
        user_id=test_task.owner_id
    )

    assert updated_task.title == "Updated Task"
    assert updated_task.status == "завершено"
    assert updated_task.priority == 5


def test_delete_task(db: Session, test_task):
    deleted_task = crud.delete_user_task(db, test_task.id, test_task.owner_id)
    assert deleted_task.id == test_task.id
    assert db.query(models.Task).count() == 0


def test_top_priority_tasks(db: Session, test_user):
    priorities = [5, 3, 1, 4, 2]
    for p in priorities:
        crud.create_user_task(
            db,
            schemas.TaskCreate(
                title=f"Task {p}",
                priority=p,
                status="в ожидании"
            ),
            test_user.id
        )

    top_tasks = crud.get_top_priority_tasks(db, test_user.id, limit=3)
    assert [t.priority for t in top_tasks] == [5, 4, 3]


def test_invalid_status_handling(db: Session, test_user):
    with pytest.raises(ValueError):
        invalid_data = schemas.TaskCreate(
            title="Invalid",
            status="неправильный статус",
            priority=1
        )
        crud.create_user_task(db, invalid_data, test_user.id)


def test_foreign_key_constraint(db: Session):
    with pytest.raises(Exception):
        task_data = schemas.TaskCreate(title="No Owner")
        crud.create_user_task(db, task_data, user_id=999)


def test_update_task_with_invalid_owner(db: Session, test_task):
    updated_data = schemas.TaskCreate(
        title="Hacked",
        status="в ожидании",
        priority=1
    )
    result = crud.update_user_task(
        db,
        task_id=test_task.id,
        task=updated_data,
        user_id=999
    )
    assert result is None

def test_delete_task_not_owner(db, test_task):
    result = crud.delete_user_task(db, test_task.id, user_id=999)
    assert result is None