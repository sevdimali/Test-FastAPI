from fastapi import Request
from tortoise.contrib import test

from api.utils import API_functools
from api.api_v1.models.tortoise import Person
from api.api_v1.models.pydantic import User
from api.api_v1.storage.initial_data import INIT_DATA


class TestUtils(test.TestCase):
    def test_get_or_default(self):
        list_object = (
            {"name": "John Doe"},
            {"name": "Bob Doe"},
            {"name": "Alice Doe"},
        )
        for index, obj in enumerate(list_object):
            assert (
                API_functools.get_or_default(list_object, index, None) == obj
            )

    async def test_instance_of(self):
        obj = await Person.create(**INIT_DATA[0])
        elements = {
            "Hello World": str,
            1: int,
            obj: Person,
            (1, 2, 3, 4): tuple,
        }
        for el, instance in elements.items():
            assert API_functools.instance_of(el, instance) is True

    def test_get_attributes(self):
        expected = (
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
        assert API_functools.get_attributes(User) == expected

    def test_valid_order(self):
        # valid order must consist of an attribute of the Person class
        # and the word "asc" or "desc"
        orders = [
            ("first_name:asc", "first_name"),
            ("first_name:desc", "-first_name"),
            ("notattributte:asc", None),
            ("id:notvalidkeyword", None),
        ]
        for order in orders:
            assert API_functools.valid_order(User, order[0]) == order[1]
            assert API_functools.valid_order(User, order[0]) == order[1]

    def test_is_attribute_of(self):
        for attr in API_functools.get_attributes(User):
            assert API_functools.is_attribute_of(attr, User) is True
        assert API_functools.is_attribute_of("id", User) is False
        assert API_functools.is_attribute_of("invalid", User) is False

    def test_manage_next_previous_page(self):
        scope = {"type": "http", "path": "/", "method": "GET"}
        request = Request(scope)
        data = []
        scenes = [
            {
                "data": (0, 5, 0),  # nb_total_data, limit, offset
                "expected": {"next": None, "previous": None, "users": []},
            },
            {
                "data": (15, 5, 5),
                "expected": {
                    "next": "/?limit=5&offset=10",
                    "previous": "/?limit=5&offset=0",
                    "users": [],
                },
            },
            {
                "data": (10, 5, 0),
                "expected": {
                    "next": "/?limit=5&offset=5",
                    "previous": None,
                    "users": [],
                },
            },
            {
                "data": (10, 5, 5),
                "expected": {
                    "next": None,
                    "previous": "/?limit=5&offset=0",
                    "users": [],
                },
            },
        ]
        for scene in scenes:
            # scene 1 next=None, previous=None
            actual = API_functools.manage_next_previous_page(
                request, data, *scene["data"]
            )
            assert actual == scene["expected"]

    async def test_insert_default_data(self):
        nb_users_inserted = 4
        await API_functools.insert_default_data(
            data=INIT_DATA[:nb_users_inserted]
        )
        nb_users = await Person.all().count()
        assert nb_users == nb_users_inserted

    async def test_create_default_person(self):
        user_to_create = INIT_DATA[0]
        user_created = await API_functools._create_default_person(
            user_to_create
        )
        actual = {
            **user_created.__dict__,
            "gender": user_created.gender.value,
            "date_of_birth": user_created.date_of_birth.strftime("%Y-%m-%d"),
        }
        actual.pop("_partial")
        actual.pop("_saved_in_db")
        actual.pop("_custom_generated_pk")
        actual.pop("id")
        assert user_to_create == actual
