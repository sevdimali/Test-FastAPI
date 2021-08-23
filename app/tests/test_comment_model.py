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
        user = await Person.create(**INIT_DATA.get("person", [])[0])
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

        # Insert new Comment
        comment_inserted = INIT_DATA.get("comment", [])[0]
        await self.insert_comments(
            [comment_inserted], [INIT_DATA.get("person", [])[0]]
        )

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        expected = {
            "next": None,
            "previous": None,
            "comments": [
                {
                    "id": 1,
                    "user_id": 1,
                    "added": comment_inserted["added"],
                    "content": comment_inserted["content"],
                }
            ],
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    async def test_get_comments_with_limit_offset(self):
        limit = 4
        offset = 0
        comments = INIT_DATA.get("comment", [])[: limit + 4]
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
        content_asc = "content:asc"
        # sort by date added descending order
        added_desc = "added:desc"
        data_nbr = 4

        comments = INIT_DATA.get("comment", [])[:data_nbr]
        users = INIT_DATA.get("person", [])[:data_nbr]

        await self.insert_comments(comments, users)
        assert await Comment.all().count() == data_nbr

        # Test order by user id ASC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": content_asc})

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
                key=lambda u: u[content_asc.split(":")[0]],
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
        comment.pop("user", None)
        comment["user_id"] = 1
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.post(API_ROOT, data=json.dumps(comment))

        expected = {
            "success": False,
            "comment": {},
            "detail": "Comment owner doesn't exist",
        }
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected

        comment_owner = await Person.create(**INIT_DATA.get("person", [])[0])
        comment["user_id"] = comment_owner.id
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.post(API_ROOT, data=json.dumps(comment))

        expected = {
            "success": True,
            "comment": {"id": 1, **comment},
            "detail": "Comment successfully created",
        }
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected

    async def test_get_comment_by_ID(self):
        comment_ID = 1
        comment = INIT_DATA.get("comment", [])[0]
        comment["user_id"] = comment.pop("user", 1)

        # Not found
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}{comment_ID}")
        expected = {"success": False, "comment": {}, "detail": "Not Found"}

        assert response.status_code == 404
        assert response.json() == expected

        # Insert new Comment
        await self.insert_comments([comment], [INIT_DATA.get("person", [])[0]])

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}{comment_ID}")

        expected = {"success": True, "user": {"id": comment_ID, **comment}}

        assert response.status_code == 200
        assert response.json() == expected

    async def test_patch_comment(self):
        comment_ID = 1
        comment = INIT_DATA.get("comment", [])[0]
        comment["user_id"] = comment.pop("user", 1)

        # Comment doesn't exist
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.patch(
                f"{API_ROOT}{comment_ID}", data=json.dumps(comment)
            )
        expected = {
            "success": False,
            "comment": {},
            "detail": f"Comment with ID {comment_ID} doesn't exist.",
        }
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Insert new Comment
        await self.insert_comments([comment], [INIT_DATA.get("person", [])[0]])

        # patch comment content
        new_content = {"content": INIT_DATA.get("comment", [])[1]["content"]}
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.patch(
                f"{API_ROOT}{comment_ID}", data=json.dumps(new_content)
            )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {
            "success": True,
            "comment": {**comment, "content": new_content},
            "detail": "Comment successfully patched",
        }

    async def test_put_comment(self):
        # test comment doesn't exist
        comment_ID = 1
        comment = INIT_DATA.get("comment", [])[0]
        comment["user_id"] = comment.pop("user", 1)
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.put(
                f"{API_ROOT}{comment_ID}",
                data=json.dumps(comment),
            )
        expected = {
            "success": False,
            "comment": {},
            "detail": f"Comment with ID {comment_ID} doesn't exist.",
        }

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Insert new Comment
        await self.insert_comments([comment], [INIT_DATA.get("person", [])[0]])

        # Get first comment
        new_owner = await Person.create(**INIT_DATA.get("person", [])[1])
        new_comment_data = INIT_DATA.get("comment", [])[1]
        new_comment_data.pop("user", None)
        new_comment_data["user_id"] = new_owner.id
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.put(
                f"{API_ROOT}{comment_ID}",
                data=json.dumps(new_comment_data),
            )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {
            "success": True,
            "comment": {"id": 1, **new_comment_data},
            "detail": "Comment successfully edited",
        }
