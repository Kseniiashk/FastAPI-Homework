import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from app import models, schemas, crud, auth
from app.database import SessionLocal, engine
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from fastapi_cache.decorator import cache

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=schemas.User, status_code=201)
async def register_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)

@app.post("/token/", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=120)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/tasks/", response_model=schemas.Task)
def create_task(
        task: schemas.TaskCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_user_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[schemas.Task])
@cache(expire=120)
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_user_tasks(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search
    )

@app.get("/tasks/top/", response_model=List[schemas.Task])
@cache(expire=120)
def read_top_priority_tasks(
        limit: int = 5,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_top_priority_tasks(db, user_id=current_user.id, limit=limit)

@app.get("/tasks/{task_id}", response_model=schemas.Task)
@cache(expire=60)
def read_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_task = crud.get_user_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
        task_id: int,
        task: schemas.TaskCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_task = crud.update_user_task(db, task_id=task_id, task=task, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    db_task = crud.delete_user_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
