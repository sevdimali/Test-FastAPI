# import json
from itertools import zip_longest

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

            for comment, user in zip_longest(comments, users):
                if user is not None:
                    executor.map(
                        await API_functools._insert_default_data(
                            "person", user
                        )
                    )
                if comment is not None:
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
        comment_inserted = {**INIT_DATA.get("comment", [])[0]}
        await self.insert_comments(
            [comment_inserted], [INIT_DATA.get("person", [])[0]]
        )

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)
        actual = response.json()
        expected = {
            "next": None,
            "previous": None,
            "comments": [
                {
                    "id": 1,
                    "user_id": 1,
                    "added": comment_inserted["added"],
                    "edited": actual["comments"][0]["edited"],
                    "content": comment_inserted["content"],
                }
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert expected == actual

    async def test_get_comments_with_limit_offset(self):
        limit = 4
        offset = 0
        comments = [*INIT_DATA.get("comment", [])[: limit + 4]]
        users = INIT_DATA.get("person", [])[: limit + 4]

        await self.insert_comments(comments, users)

        assert await Comment.all().count() == len(comments)

        # Scene 1 get first data, previous=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                API_ROOT, params={"limit": limit, "offset": offset}
            )
        actual = response.json()
        expected = {
            "next": f"{API_ROOT}?limit={limit}&offset={limit}",
            "previous": None,
            "comments": [
                {
                    "id": n,
                    "added": comment["added"],
                    "edited": actual["comments"][n - 1]["edited"],
                    "content": comment["content"],
                    "user_id": comment["user"],
                }
                for n, comment in enumerate(comments[:limit], start=1)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert actual == expected

        # Scene 2 get last data, next=Null
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(
                API_ROOT, params={"limit": limit, "offset": limit}
            )
        actual = response.json()

        expected = {
            "next": None,
            "previous": f"{API_ROOT}?limit={limit}&offset={offset}",
            "comments": [
                {
                    "id": n + limit + 1,
                    "added": comment["added"],
                    "edited": actual["comments"][n]["edited"],
                    "content": comment["content"],
                    "user_id": comment["user"],
                }
                for n, comment in enumerate(comments[limit:], start=0)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert actual == expected

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

        comments = [*INIT_DATA.get("comment", [])[:data_nbr]]
        users = INIT_DATA.get("person", [])[:data_nbr]

        await self.insert_comments(comments, users)
        assert await Comment.all().count() == data_nbr

        # Test order by user id ASC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": content_asc})

        actual = response.json()
        comments = sorted(
            comments,
            key=lambda u: u[content_asc.split(":")[0]],
        )
        expected = {
            "next": None,
            "previous": None,
            "comments": [
                {
                    "id": actual["comments"][n]["id"],
                    "added": c["added"],
                    "edited": actual["comments"][n]["edited"],
                    "content": c["content"],
                    "user_id": c["user"],
                }
                for n, c in enumerate(comments, start=0)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert actual == expected

        # Test order by added DESC
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT, params={"sort": added_desc})

        actual = response.json()
        comments = sorted(
            comments, key=lambda u: u[added_desc.split(":")[0]], reverse=True
        )
        expected = {
            "next": None,
            "previous": None,
            "comments": [
                {
                    "id": actual["comments"][n]["id"],
                    "added": c["added"],
                    "edited": actual["comments"][n]["edited"],
                    "content": c["content"],
                    "user_id": c["user"],
                }
                for n, c in enumerate(comments, start=0)
            ],
        }

        assert response.status_code == status.HTTP_200_OK
        assert actual == expected

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

    # async def test_create_comment(self):
    #     comment = INIT_DATA.get("comment", [])[0]
    #     comment.pop("user", None)
    #     comment["user_id"] = 1
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.post(API_ROOT, data=json.dumps(comment))

    #     expected = {
    #         "success": False,
    #         "comment": {},
    #         "detail": "Comment owner doesn't exist",
    #     }
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #     assert response.json() == expected

    #     comment_owner = await Person.create(**INIT_DATA.get("person", [])[0])
    #     comment["user_id"] = comment_owner.id
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.post(API_ROOT, data=json.dumps(comment))

    #     expected = {
    #         "success": True,
    #         "comment": {"id": 1, **comment},
    #         "detail": "Comment successfully created",
    #     }
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.json() == expected

    async def test_get_comment_by_ID(self):
        comment_ID = 1
        comment = {**INIT_DATA.get("comment", [])[0]}

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
        actual = response.json()
        comment["user_id"] = comment.pop("user", 1)
        expected = {
            "success": True,
            "comment": {
                **comment,
                "id": comment_ID,
                "edited": actual["comment"]["edited"],
            },
        }
        assert response.status_code == 200
        assert actual == expected

    async def test_get_comment_by_user(self):
        # Inserted 4 comment with ID 1 as user owner
        owner_ID = 1
        comments = tuple(
            map(
                lambda cm: {**cm, "user": owner_ID},
                [*INIT_DATA.get("comment", [])[:4]],
            )
        )
        await self.insert_comments(
            comments,
            INIT_DATA.get("person", [])[:2],
        )

        # owner doesn't exist
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}user/3")
        expected = {
            "success": False,
            "comments": [],
            "detail": "Comment owner doesn't exist",
        }

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        # Not Found
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}user/2")
        expected = {
            "success": False,
            "comments": [],
            "detail": "Not Found",
        }

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected

        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(f"{API_ROOT}user/{owner_ID}")

        actual = response.json()
        expected_comments = [
            {
                **{k if k != "user" else "user_id": v for k, v in cm.items()},
                "id": pk,
                "edited": actual["comments"][pk - 1]["edited"],
            }
            for pk, cm in enumerate(comments, start=1)
        ]
        expected = {"success": True, "comments": expected_comments}

        assert response.status_code == status.HTTP_200_OK
        assert len(actual["comments"]) == 4
        assert actual == expected

    # async def test_patch_comment(self):
    #     comment_ID = 1
    #     comment = INIT_DATA.get("comment", [])[0]
    #     comment["user_id"] = comment.pop("user", 1)

    #     # Comment doesn't exist
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.patch(
    #             f"{API_ROOT}{comment_ID}", data=json.dumps(comment)
    #         )
    #     expected = {
    #         "success": False,
    #         "comment": {},
    #         "detail": f"Comment with ID {comment_ID} doesn't exist.",
    #     }
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #     assert response.json() == expected

    #     # Insert new Comment
    #     await self.insert_comments([comment], [INIT_DATA.get("person", [])[0]])

    #     # patch comment content
    #     new_content = {"content": INIT_DATA.get("comment", [])[1]["content"]}
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.patch(
    #             f"{API_ROOT}{comment_ID}", data=json.dumps(new_content)
    #         )

    #     assert response.status_code == status.HTTP_202_ACCEPTED
    #     assert response.json() == {
    #         "success": True,
    #         "comment": {**comment, "content": new_content},
    #         "detail": "Comment successfully patched",
    #     }

    # async def test_put_comment(self):
    #     # test comment doesn't exist
    #     comment_ID = 1
    #     comment = INIT_DATA.get("comment", [])[0]
    #     comment["user_id"] = comment.pop("user", 1)
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.put(
    #             f"{API_ROOT}{comment_ID}",
    #             data=json.dumps(comment),
    #         )
    #     expected = {
    #         "success": False,
    #         "comment": {},
    #         "detail": f"Comment with ID {comment_ID} doesn't exist.",
    #     }

    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #     assert response.json() == expected

    #     # Insert new Comment
    #     await self.insert_comments([comment], [INIT_DATA.get("person", [])[0]])

    #     # Get first comment
    #     new_owner = await Person.create(**INIT_DATA.get("person", [])[1])
    #     new_comment_data = INIT_DATA.get("comment", [])[1]
    #     new_comment_data.pop("user", None)
    #     new_comment_data["user_id"] = new_owner.id
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.put(
    #             f"{API_ROOT}{comment_ID}",
    #             data=json.dumps(new_comment_data),
    #         )

    #     assert response.status_code == status.HTTP_202_ACCEPTED
    #     assert response.json() == {
    #         "success": True,
    #         "comment": {"id": 1, **new_comment_data},
    #         "detail": "Comment successfully edited",
    #     }

    # async def test_delete_user(self):

    #     # Comment doesn't exist
    #     comment_ID = 1
    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.delete(f"{API_ROOT}{comment_ID}")
    #     expected = {
    #         "success": False,
    #         "user": {},
    #         "detail": f"Comment with ID {comment_ID} doesn't exist",
    #     }
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #     assert response.json() == expected

    #     # Insert new Comment
    #     self.insert_comments(
    #         [INIT_DATA.get("comment", [])[0]], [INIT_DATA.get("person", [])[0]]
    #     )

    #     async with AsyncClient(app=app, base_url=BASE_URL) as ac:
    #         response = await ac.delete(f"{API_ROOT}{comment_ID}")
    #     expected = {
    #         "success": True,
    #         "user": {**INIT_DATA.get("comment", [])[0], "id": comment_ID},
    #         "detail": f"Comment {comment_ID} delete successfully ⭐",
    #     }
    #     deleted_comment = await Comment.filter(id=comment_ID).first()
    #     assert response.status_code == status.HTTP_202_ACCEPTED
    #     assert response.json() == expected
    #     assert None is deleted_comment
