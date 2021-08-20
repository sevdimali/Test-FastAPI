from fastapi import Request
from tortoise.contrib import test

from app.api.utils import API_functools
from app.api.api_v1.models.tortoise import Person
from app.api.api_v1.models.pydantic import User, PartialUser
from app.api.api_v1.storage.initial_data import INIT_DATA


class TestUtils(test.TestCase):
    def test_strip_spaces(self):
        s = API_functools.strip_spaces("       Hello         World       ")
        assert s == "Hello World"

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
        assert (
            API_functools.get_or_default(list_object, len(list_object), None)
            is None
        )

    async def test_instance_of(self):
        obj = await Person.create(**INIT_DATA.get("person", [])[0])
        elements = {
            "Hello World": str,
            1: int,
            obj: Person,
            (1, 2, 3, 4): tuple,
        }
        for el, instance in elements.items():
            assert API_functools.instance_of(el, instance) is True
        assert API_functools.instance_of("Hello", int) is False

    def test_get_attributes(self):
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
        assert API_functools.get_attributes(User) == user_attributes
        assert API_functools.get_attributes(PartialUser) == user_attributes[:6]

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

    def test_is_attribute_of(self):
        for attr in API_functools.get_attributes(User):
            assert API_functools.is_attribute_of(attr, User) is True
        assert API_functools.is_attribute_of("id", User) is False
        assert API_functools.is_attribute_of("invalid", User) is False

    def test_manage_next_previous_page(self):
        scope = {"type": "http", "path": "/", "method": "GET"}
        request = Request(scope)
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
                request, [], *scene["data"], data_type="users"
            )
            assert actual == scene["expected"]

    async def test_insert_default_data(self):
        nb_users_inserted = 4
        await API_functools.insert_default_data(
            table="person",
            data=INIT_DATA.get("person", [])[:nb_users_inserted],
        )
        assert await Person.all().count() == nb_users_inserted

    async def test__insert_default_data(self):
        user_to_create = INIT_DATA.get("person", [])[0]
        user_created = await API_functools._insert_default_data(
            "person", user_to_create
        )
        assert API_functools.instance_of(user_created, Person) is True
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
