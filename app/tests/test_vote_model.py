from fastapi import status
from httpx import AsyncClient
from tortoise.contrib import test

from main import app
from app.api.api_v1 import settings
from app.api.api_v1.storage.initial_data import INIT_DATA
from app.api.api_v1.models.pydantic import default_content
from app.api.api_v1.models.tortoise import Person, Comment, Vote

TORTOISE_TEST_DB = getattr(settings, "TORTOISE_TEST_DB", "sqlite://:memory:")
BASE_URL = "http://127.0.0.1:8000"
API_ROOT = "/api/v1/votes/"


class TestPersonAPi(test.TestCase):
    async def test__str__repr__(self):
        user = await Person.create(**INIT_DATA.get("person", [])[0])
        comment = await Comment.create(user=user, content=default_content)
        vote = await Vote.create(user=user, comment=comment)
        expected_repr = "Class({!r})(User={!r}, Comment={!r},...)".format(
            vote.__class__.__name__,
            vote.user.first_name,
            vote.comment.content[:10],
        )
        expected_str = "{!s}(User={!s}, Comment={!s},...)".format(
            vote.__class__.__name__,
            vote.user.first_name,
            vote.comment.content[:10],
        )
        assert vote.__repr__() == expected_repr
        assert vote.__str__() == expected_str

    async def test_get_votes(self):
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            response = await ac.get(API_ROOT)

        expected = {"detail": "Not Found", "success": False, "votes": []}

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected
