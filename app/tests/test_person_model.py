import json
import concurrent.futures as futures

from fastapi import status
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from api.api_v1 import settings
from api.utils import API_functools
from api.api_v1.models.pydantic import User
from api.api_v1.models.tortoise import Person
from api.api_v1.storage.initial_data import INIT_DATA

TORTOISE_TEST_DB = getattr(settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"
API_ROOT = "/api/v1/users/"
avatar = "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1"
USER_DATA = {
    "is_admin": True,
    "first_name": "John",
    "last_name": "DOE",
    "email": "john.doe@eliam-lotonga.fr",
    "gender": "Male",
    "avatar": avatar,
    "job": "Compensation Analyst",
    "company": "Edgetag",
    "date_of_birth": "1970-01-01",
    "country_of_birth": "No where",
}
USER_DATA_WITH_SAME_NAME = {
    "is_admin": True,
    "first_name": "Alice",
    "last_name": "Bod",
    "email": "alice.bob@eliam-lotonga.fr",
    "gender": "Male",
    "avatar": avatar,
    "job": "Compensation Analyst",
    "company": "Edgetag",
    "date_of_birth": "1970-01-01",
    "country_of_birth": "No where",
}
USER_DATA2 = {
    "first_name": "John1",
    "last_name": "DOE1",
    "email": "john1.doe1@eliam-lotonga.fr",
    "avatar": avatar + "1",
    "company": "Edgetag 1",
    "job": "Compensation Analyst 1",
    "is_admin": False,
    "gender": "Female",
    "date_of_birth": "1971-02-02",
    "country_of_birth": "No where 1",
}


class TestPersonAPi(test.TestCase):
    def test__str__repr__(self):
        person = Person(**USER_DATA)
        expected_repr = "Class({!r})(first_name={!r}, last_name={!r},...)"
        expected_str = "{!s}(first_name={!s}, last_name={!s},...)"
        assert person.__repr__() == expected_repr.format(
            person.__class__.__name__, person.first_name, person.last_name
        )
        assert person.__str__() == expected_str.format(
            person.__class__.__name__, person.first_name, person.last_name
        )

    async def test_root(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "detail": "Welcome to FastAPI",
            "apis": ["/api/v1/users"],
            "fake_data": "/data",
            "docs": ["/docs", "/redoc"],
            "openapi": "/openapi.json",
        }

    async def test_create_user(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.post(API_ROOT, data=json.dumps(USER_DATA))

        expected = {"id": 1, **USER_DATA}
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected

    async def test_loading_data(self):
        quantity_users = 4
        # load fake data
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get("/data", params={"quantity": quantity_users})

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "next": None,
            "previous": None,
            "users": [
                {"id": pk, **user}
                for pk, user in enumerate(INIT_DATA[:quantity_users], start=1)
            ],
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    async def test_get_users(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)

        expected = {"detail": "Not Found", "success": False, "users": []}

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Create new User
        person = await Person.create(**USER_DATA)
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "next": None,
            "previous": None,
            "users": [{"id": person.id, **USER_DATA}],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    async def test_limit_offset(self):
        limit = 5
        offset = 0
        users = INIT_DATA[:10]

        # Insert data
        with futures.ProcessPoolExecutor() as executor:
            for user in users:
                executor.map(await API_functools._create_default_person(user))

        assert await Person.all().count() == len(users)

        # Scene 1 get first data, previous=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"limit": limit, "offset": offset})

        expected = {
            "next": f"{API_ROOT}?limit={limit}&offset={limit}",
            "previous": None,
            "users": [{"id": n, **user} for n, user in enumerate(users[:limit], start=1)],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # Scene 2 get last data, next=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"limit": limit, "offset": limit})
        expected = {
            "next": None,
            "previous": f"{API_ROOT}?limit={limit}&offset={offset}",
            "users": [
                {"id": n, **user} for n, user in enumerate(users[limit:], start=limit + 1)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        limit = 0
        offset = -1
        # Test bad limit and offset values
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"limit": limit, "offset": limit})
        expected = {
            "success": False,
            "users": [],
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected

    async def test_sorted_by_attribute(self):
        # sort by first_name ascending order
        asc = "first_name:asc"
        # sort by first_name descending order
        desc = "first_name:desc"

        users = INIT_DATA[:4]
        with futures.ProcessPoolExecutor() as executor:
            for user in users:
                executor.map(await API_functools._create_default_person(user))

        assert await Person.all().count() == len(users)

        # Test order by first_name ASC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": asc})

        expected = {
            "next": None,
            "previous": None,
            "users": sorted(
                [{"id": n, **user} for n, user in enumerate(users, start=1)],
                key=lambda u: u[asc.split(":")[0]],
            ),
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # Test order by first_name DESC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": desc})
        expected = {
            "next": None,
            "previous": None,
            "users": sorted(
                [{"id": n, **user} for n, user in enumerate(users, start=1)],
                key=lambda u: u[desc.split(":")[0]],
                reverse=True,
            ),
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # Test bad order by
        order_by = "undefined:asc"
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": order_by})
        detail = "Invalid sort parameters. it must match \
            attribute:order. ex: id:asc or id:desc"
        expected = {
            "success": False,
            "users": [],
            "detail": detail,
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected

    async def test_patch_user(self):

        # User doesn't exist
        user_ID = 100
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.patch(f"{API_ROOT}{user_ID}", data=json.dumps(USER_DATA))
        expected = {
            "success": False,
            "user": {},
            "detail": f"User with ID {user_ID} doesn't exist.",
        }
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        data = {**USER_DATA}
        data.pop("is_admin", None)
        data.pop("gender", None)
        data.pop("date_of_birth", None)
        data.pop("country_of_birth", None)
        # Create new User
        person = await Person.create(**USER_DATA2)
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.patch(f"{API_ROOT}{person.id}", data=json.dumps(data))
        user_expected = {
            **person.__dict__,
            **data,
            "gender": person.gender.value,
            "date_of_birth": person.date_of_birth.strftime("%Y-%m-%d"),
        }
        user_expected.pop("_custom_generated_pk", None)
        user_expected.pop("_partial", None)
        user_expected.pop("_saved_in_db", None)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == user_expected

    async def test_put_user(self):

        # test user doesn't exist
        user_ID = 1
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.put(
                f"{API_ROOT}{user_ID}",
                data=json.dumps(USER_DATA),
            )
        expected = {
            "success": False,
            "user": {},
            "detail": f"User with ID {user_ID} doesn't exist.",
        }

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Create new User
        person = await Person.create(**USER_DATA2)
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.put(
                f"{API_ROOT}{person.id}",
                data=json.dumps(USER_DATA),
            )
        expected = {"id": person.id, **USER_DATA}

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == expected

    async def test_get_user_by_ID(self):
        # Not found
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}1")
        expected = {"success": False, "user": {}, "detail": "Not Found"}

        assert response.status_code == 404
        assert response.json() == expected

        # Create new User
        person = await Person.create(**USER_DATA)
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}{person.id}")
        expected = {"success": True, "user": {"id": person.id, **USER_DATA}}

        assert response.status_code == 200
        assert response.json() == expected

    async def test_get_user_by_attribute(self):
        person = await Person.create(**USER_DATA)
        assert person.id == 1

        person2 = await Person.create(**USER_DATA_WITH_SAME_NAME)
        assert person2.id == 2

        # Not found
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}filter/first_name/notfound")
        expected = {"success": False, "users": [], "detail": "Not Found"}

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Invalid attribute
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}filter/id/{person.id}")
        expected = {
            "success": False,
            "users": [],
            "detail": f"""
            Invalid attribute filter.
            Try with: {tuple(
            User.__dict__.get("__fields__", {}).keys())}
            """,
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                f"{API_ROOT}filter/first_name/{person.first_name[:4].lower()}"
            )
        expected = {"success": True, "users": [{"id": person.id, **USER_DATA}]}

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # first_name 'john'
        url = "filter/first_name/"
        # Test with keyword "Or"
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT + url + "john")
        expected = {"success": True, "users": [{"id": person.id, **USER_DATA}]}

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # first_name or last_name must contains 'john'
        url = "filter/first_nameOrlast_name/"
        # Test with keyword "Or"
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT + url + "john")
        expected = {"success": True, "users": [{"id": person.id, **USER_DATA}]}

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # first_name or last_name or email must contains "bob"
        url = "filter/first_nameOrlast_nameOremail/"
        # Test with keyword "Or" "And"
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT + url + "bob")
        expected = {
            "success": True,
            "users": [
                {"id": person2.id, **USER_DATA_WITH_SAME_NAME},
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # last_name doesn't contain 'alic' word so it should fail
        url = "filter/first_nameAndlast_nameAndemail/"
        # Test with keyword "And"
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT + url + "alic")
        expected = {"success": False, "users": [], "detail": "Not Found"}

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

    async def test_delete_user(self):

        # User doesn't exist
        user_ID = 100
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.delete(f"{API_ROOT}{user_ID}")
        expected = {
            "success": False,
            "user": {},
            "detail": f"User with ID {user_ID} doesn't exist",
        }
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Create new User
        person = await Person.create(**USER_DATA)
        assert person.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.delete(f"{API_ROOT}{person.id}")
        expected = {
            "success": True,
            "user": {**USER_DATA, "id": person.id},
            "detail": f"User {person.id} delete successfully ⭐",
        }
        deleted_user = await Person.filter(id=person.id).first()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == expected
        assert None is deleted_user
