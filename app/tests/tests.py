import json
import asyncio

import pytest
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from api.api_v1 import settings


TORTOISE_TEST_DB = getattr(
    settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"
API_ROOT = "/api/v1/users"


class TestPersonAPi(test.TestCase):

    async def test_root(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "detail": "Welcome to FastAPI",
            "apis": ["/api/v1/users"],
            "fake_data": "/data",
            "docs": ["/docs", "/redoc"],
            "openapi": "/openapi.json"
        }

    async def test_create_user(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.post(API_ROOT, data=json.dumps({
                "first_name": "John",
                "last_name": "DOE",
                "email": "john.doe@eliam-lotonga.fr",
                "gender": "Male",
                "avatar": "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1",
                "job": "Compensation Analyst",
                "company": "Edgetag",
                "date_of_birth": "1970-01-01",
                "country_of_birth": "No where",
            }))
        expected = {
            "id": 1,
            "is_admin": False,
            "first_name": "John",
            "last_name": "DOE",
            "email": "john.doe@eliam-lotonga.fr",
            "gender": "Male",
            "avatar": "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1",
            "job": "Compensation Analyst",
            "company": "Edgetag",
            "date_of_birth": "1970-01-01",
            "country_of_birth": "No where",
        }
        assert response.status_code == 200
        assert response.json() == expected
