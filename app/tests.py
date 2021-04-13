import pytest
from httpx import AsyncClient
from app import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get('/')
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": [
            "/users"
        ],
        "docs": [
            "/docs",
            "/redoc"
        ]
    }
