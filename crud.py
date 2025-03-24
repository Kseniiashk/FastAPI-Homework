from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
import models, schemas
from datetime import datetime
import auth

def get_user_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()

def get_user_tasks(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = None,
        sort_order: str = "asc",
        search: str = None
):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    if search:
        query = query.filter(or_(
            models.Task.title.contains(search),
            models.Task.description.contains(search)
        ))
    if sort_by:
        if sort_order == "asc":
            query = query.order_by(asc(getattr(models.Task, sort_by)))
        else:
            query = query.order_by(desc(getattr(models.Task, sort_by)))

    return query.offset(skip).limit(limit).all()

def get_top_priority_tasks(db: Session, user_id: int, limit: int = 5):
    return db.query(models.Task).filter(
        models.Task.owner_id == user_id
    ).order_by(desc(models.Task.priority)).limit(limit).all()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_user_task(db: Session, task_id: int, task: schemas.TaskCreate, user_id: int):
    db_task = get_user_task(db, task_id, user_id)
    if not db_task:
        return None

    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_user_task(db: Session, task_id: int, user_id: int):
    db_task = get_user_task(db, task_id, user_id)
    if not db_task:
        return None

    db.delete(db_task)
    db.commit()
    return db_task

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user