from tortoise.contrib import test
from api.api_v1.models.pydantic import User, PartialUser


class TestPydantic(test.TestCase):
    def test_user_attributes(self):
        user_attributes = (
            "first_name",
            "last_name",
            "email",
            "avatar",
            "company",
            "job",
            "is_admin",
            "gender",
            "date_of_birth",
            "country_of_birth",
        )
        assert User.attributes() == user_attributes
        partialUser_attributes = (
            "first_name",
            "last_name",
            "email",
            "avatar",
            "company",
            "job",
        )
        assert PartialUser.attributes() == partialUser_attributes
