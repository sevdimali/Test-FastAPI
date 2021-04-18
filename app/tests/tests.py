import pytest
from httpx import AsyncClient
from main import app

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        response = await ac.get('/')
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": [
            "/api/v1/users"
        ],
        "docs": [
            "/docs",
            "/redoc"
        ],
        "openapi": "/openapi.json"
    }
