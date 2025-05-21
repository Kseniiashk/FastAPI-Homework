import pytest
from fastapi import HTTPException
from jose import JWTError
from app import auth
from datetime import datetime, timedelta

def test_verify_password_valid():
    hashed = auth.get_password_hash("password")
    assert auth.verify_password("password", hashed) is True

def test_verify_password_invalid():
    hashed = auth.get_password_hash("password")
    assert auth.verify_password("wrong", hashed) is False

def test_create_access_token():
    token = auth.create_access_token({"sub": "test"})
    assert isinstance(token, str)

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db):
    from app.auth import get_current_user
    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid_token", db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_valid_token(db, test_user):
    # Создаем токен с явным указанием времени жизни
    token = auth.create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=15)
    )

    # Получаем пользователя через асинхронный вызов
    user = await auth.get_current_user(token, db)

    # Проверяем результаты
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email