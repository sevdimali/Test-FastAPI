import json
import asyncio
import concurrent.futures as futures

import pytest
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from api.api_v1 import settings
from api.utils import API_functools
from api.api_v1.models.tortoise import Person
from api.api_v1.storage.initial_data import INIT_DATA

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

    async def test_get_users_with_limit_and_offset(self):
        limit = 5
        offset = 0
        users = INIT_DATA[:10]
        with futures.ProcessPoolExecutor() as executor:
            for user in users:
                executor.map(await API_functools._create_default_person(user))

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"limit": 5, "offset": offset})

        expected = {
            "next": f"/api/v1/users/?limit={limit}&offset={limit}",
            'previous': None,
            'users': [{"id": n, **user} for n, user in enumerate(users[:5], start=1)]
        }
        assert response.status_code == 200
        assert response.json() == expected

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"limit": 5, "offset": limit})
        expected = {
            "next": None,
            'previous': f"/api/v1/users/?limit={limit}&offset={offset}",
            'users': [{"id": n, **user} for n, user in enumerate(users[5:], start=6)]
        }

        assert response.status_code == 200
        assert response.json() == expected

    async def test_get_users_sorted_by_attribute(self):
        # sort by first_name ascending order
        asc = "first_name:asc"
        # sort by first_name descending order
        desc = "first_name:desc"

        users = INIT_DATA[:4]
        with futures.ProcessPoolExecutor() as executor:
            for user in users:
                executor.map(await API_functools._create_default_person(user))

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": asc})

        expected = {
            "next": None,
            'previous': None,
            'users': sorted(

                [{"id": n, **user}
                    for n, user in enumerate(users, start=1)],
                key=lambda u: u[asc.split(":")[0]]
            )
        }
        assert response.status_code == 200
        assert response.json() == expected

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": desc})
        expected = {
            "next": None,
            'previous': None,
            'users': sorted(

                [{"id": n, **user}
                    for n, user in enumerate(users, start=1)],
                key=lambda u: u[desc.split(":")[0]], reverse=True
            )
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

    async def test_put_user(self):
        # Create new User
        person1 = await Person.create(
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
        person2 = await Person.create(
            **USER_DATA
        )
        assert person1.id == 1
        assert person2.id == 2

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.put(
                f"{API_ROOT}{person2.id}",
                data=json.dumps(USER_DATA),
                params={"new_user": person1.id}
            )
        expected = {"id": person1.id, **USER_DATA}

        user_deleted = await Person.filter(id=2).first()

        assert user_deleted == None

        assert response.status_code == 200
        assert response.json() == expected

    async def test_get_user_by_id(self):
        # Create new User
        person = await Person.create(
            **USER_DATA
        )
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                f"{API_ROOT}{person.id}")
        expected = {
            "success": True,
            "user": {"id": person.id, **USER_DATA}
        }

        assert response.status_code == 200
        assert response.json() == expected

    async def test_delete_user(self):
        # Create new User
        person = await Person.create(
            **USER_DATA
        )
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.delete(
                f"{API_ROOT}{person.id}")
        expected = {
            "success": True,
            "user": {**USER_DATA, "id": 1},
            "detail": "User 1 delete successfully ⭐"
        }
        deleted_user = await Person.filter(id=1).first()
        assert response.status_code == 200
        assert response.json() == expected
        assert None == deleted_user
