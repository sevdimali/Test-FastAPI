from tortoise.contrib import test

from api.api_v1 import settings
from api.api_v1.models.tortoise import Person, Comment
from api.api_v1.models.pydantic import default_content

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


class TestPersonAPi(test.TestCase):
    async def test__str__repr__(self):
        owner = await Person.create(**USER_DATA)
        comment = await Comment.create(owner=owner, content=default_content)

        expected_repr = "Class({!r})[{!r}]".format(
            comment.__class__.__name__,
            comment.content[:10],
        )
        expected_str = "{!s}({!s})".format(
            comment.__class__.__name__, comment.content[:10]
        )
        assert comment.__repr__() == expected_repr
        assert comment.__str__() == expected_str
