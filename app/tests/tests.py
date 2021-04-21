import json
import asyncio

import pytest
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from api.api_v1 import settings
from api.api_v1.models.tortoise import Person


TORTOISE_TEST_DB = getattr(
    settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"
API_ROOT = "/api/v1/users/"

USER_DATA = {
    "is_admin": True,
    "first_name": "John",
    "last_name": "DOE",
    "email": "john.doe@eliam-lotonga.fr",
    "gender": "Male",
    "avatar": "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1",
    "job": "Compensation Analyst",
    "company": "Edgetag",
    "date_of_birth": "1970-01-01",
    "country_of_birth": "No where"
}


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
            response = await ac.post(API_ROOT, data=json.dumps(USER_DATA))
        expected = {
            "id": 1,
            **USER_DATA
        }
        assert response.status_code == 200
        assert response.json() == expected

    async def test_get_users(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "detail": 'Not Found',
            'success': False,
            'users': []
        }
        assert response.status_code == 200
        assert response.json() == expected
        # Create new User
        person = await Person.create(
            **USER_DATA
        )
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "next": None,
            "previous": None,
            "users": [
                {
                    "id": 1,
                    **USER_DATA
                }
            ]
        }
        assert response.status_code == 200
        assert response.json() == expected

    async def test_patch_user(self):
        # Create new User
        person = await Person.create(
            **{
                "is_admin": False,
                "first_name": "John1",
                "last_name": "DOE1",
                "email": "john1.doe1@eliam-lotonga.fr",
                "gender": "Female",
                "avatar": "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set11",
                "job": "Compensation Analyst 1",
                "company": "Edgetag 1",
                "date_of_birth": "1971-02-02",
                "country_of_birth": "No where 1"
            }
        )
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.patch(f"{API_ROOT}{person.id}", data=json.dumps(USER_DATA))
        expected = {"id": person.id, **USER_DATA}

        assert response.status_code == 200
        assert response.json() == expected
