import json

import concurrent.futures as futures

from fastapi import status
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from app.api.api_v1 import settings
from app.api.utils import API_functools
from app.api.api_v1.models.tortoise import Person, Comment
from app.api.api_v1.storage.initial_data import INIT_DATA
from app.api.api_v1.models.pydantic import default_content as lorem

TORTOISE_TEST_DB = getattr(settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"
API_ROOT = "/api/v1/comments/"
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


class TestPersonAPi(test.TestCase):
    async def insert_comments(
        self, comments: list[dict], users: list[dict]
    ) -> None:
        """Test util method: insert some comments data

        Args:
            comments (list[dict]): list of comments
            users (list[dict]): list of persons (comment owner)

        Returns:
            None
        """
        # Insert data
        with futures.ProcessPoolExecutor() as executor:
            for comment, user in zip(comments, users):
                executor.map(
                    await API_functools._insert_default_data("person", user)
                )
                executor.map(
                    await API_functools._insert_default_data(
                        "comment", comment
                    )
                )

    async def test__str__repr__(self):
        user = await Person.create(**USER_DATA)
        comment = await Comment.create(user=user, content=lorem)

        expected_repr = "Class({!r})[{!r}]".format(
            comment.__class__.__name__,
            comment.content[:10],
        )
        expected_str = "{!s}({!s})".format(
            comment.__class__.__name__, comment.content[:10]
        )
        assert comment.__repr__() == expected_repr
        assert comment.__str__() == expected_str

    async def test_get_comments(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)

        expected = {"detail": "Not Found", "success": False, "comments": []}

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Create new User
        person = await Person.create(**USER_DATA)
        comment = await Comment.create(user=person, content=lorem)
        assert comment.id == 1

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "next": None,
            "previous": None,
            "comments": [
                {
                    "id": comment.id,
                    "user_id": person.id,
                    "added": comment.added.isoformat(),
                    "content": API_functools.strip_spaces(lorem),
                }
            ],
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    async def test_get_comments_with_limit_offset(self):
        limit = 4
        offset = 0
        comments = sorted(
            INIT_DATA.get("comment", []), key=lambda c: c["user"]
        )[: limit + 4]
        users = INIT_DATA.get("person", [])[: limit + 4]

        await self.insert_comments(comments, users)

        assert await Comment.all().count() == len(comments)

        # Scene 1 get first data, previous=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                API_ROOT, params={"limit": limit, "offset": offset}
            )

        expected = {
            "next": f"{API_ROOT}?limit={limit}&offset={limit}",
            "previous": None,
            "comments": [
                {
                    "id": n,
                    "added": comment["added"],
                    "content": comment["content"],
                    "user_id": comment["user"],
                }
                for n, comment in enumerate(comments[:limit], start=1)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # Scene 2 get last data, next=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                API_ROOT, params={"limit": limit, "offset": limit}
            )
        expected = {
            "next": None,
            "previous": f"{API_ROOT}?limit={limit}&offset={offset}",
            "comments": [
                {
                    "id": n,
                    "added": comment["added"],
                    "content": comment["content"],
                    "user_id": comment["user"],
                }
                for n, comment in enumerate(comments[limit:], start=limit + 1)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        limit = 0
        offset = -1
        # Test bad limit and offset values
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                API_ROOT, params={"limit": limit, "offset": limit}
            )
        expected = {
            "success": False,
            "comments": [],
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected

    async def test_comments_sorted_by_attribute(self):
        # sort by user id ascending order
        user_asc = "user_id:asc"
        # sort by date added descending order
        added_desc = "added:desc"
        data_nbr = 4

        comments = sorted(
            INIT_DATA.get("comment", []), key=lambda c: c["user"]
        )[:data_nbr]
        users = INIT_DATA.get("person", [])[:data_nbr]

        await self.insert_comments(comments, users)
        assert await Comment.all().count() == data_nbr

        # Test order by user id ASC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": user_asc})

        expected = {
            "next": None,
            "previous": None,
            "comments": sorted(
                [
                    {
                        "id": n,
                        "added": c["added"],
                        "content": c["content"],
                        "user_id": c["user"],
                    }
                    for n, c in enumerate(comments, start=1)
                ],
                key=lambda u: u[user_asc.split(":")[0]],
            ),
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

        # Test order by added DESC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": added_desc})
        expected = {
            "next": None,
            "previous": None,
            "comments": sorted(
                [
                    {
                        "id": n,
                        "added": c["added"],
                        "content": c["content"],
                        "user_id": c["user"],
                    }
                    for n, c in enumerate(comments, start=1)
                ],
                key=lambda u: u[added_desc.split(":")[0]],
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
            "comments": [],
            "detail": detail,
        }
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected

    async def test_create_comment(self):
        comment = INIT_DATA.get("comment", [])[0]
        comment["user_id"] = comment.pop("user", None)
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.post(API_ROOT, data=json.dumps(comment))

        expected = {"id": 1, **comment}
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected
