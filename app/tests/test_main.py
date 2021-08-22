from fastapi import status
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from app.api.api_v1 import settings

from app.api.api_v1.models.tortoise import Person, Comment, Vote

TORTOISE_TEST_DB = getattr(settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"


class TestPersonAPi(test.TestCase):
    async def test_root(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "detail": "Welcome to FastAPI",
            "apis": ["/api/v1/users", "/api/v1/comments", "/api/v1/votes"],
            "fake_data": "/data",
            "docs": ["/docs", "/redoc"],
            "openapi": "/openapi.json",
        }

    async def test_loading_data(self):
        quantity_data = 4
        # load fake data
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                "/data", params={"quantity": quantity_data}
            )
            assert response.status_code == 201
            assert response.json() == {
                "success": True,
                "detail": "Data loaded",
                "home": "/",
            }
        assert await Person.all().count() == quantity_data
        assert await Comment.all().count() == quantity_data
        assert await Vote.all().count() == quantity_data
