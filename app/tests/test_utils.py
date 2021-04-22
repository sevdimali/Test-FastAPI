from typing import List

from fastapi import Request
from httpx import AsyncClient
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
        assert API_functools.get_or_default(list_object, 0, None) == {
            "name": "John Doe"}
        assert API_functools.get_or_default(list_object, 1, None) == {
            "name": "Bob Doe"}
        assert API_functools.get_or_default(list_object, 2, None) == {
            "name": "Alice Doe"}
        assert API_functools.get_or_default(list_object, 3, None) == None

    async def test_instance_of(self):
        obj = await Person.create(**INIT_DATA[0])
        elements = {
            "Hello World": str,
            1: int,
            obj: Person,
            (1, 2, 3, 4): tuple,
        }
        for el, instance in elements.items():
            assert API_functools.instance_of(el, instance) == True

    def test_valid_order(self):
        # valid order must consist of an attribute of the Person class
        # and the word "asc" or "desc"
        orders = [
            ("first_name:asc", "first_name"),
            ("first_name:desc", "-first_name"),

            ("notattributte:asc", None),
            ("id:notvalidkeyword", None)
        ]
        for order in orders:
            assert API_functools.valid_order(User, order[0]) == order[1]
            assert API_functools.valid_order(User, order[0]) == order[1]

    def test_manage_next_previous_page(self):
        scope = {
            "type": "http",
            "path": "/",
            "method": "GET"
        }
        request = Request(scope)
        # scene 1 next=None, previous=None
        actual = API_functools.manage_next_previous_page(
            request,
            data=[],
            nb_total_data=0,
            limit=5,
            offset=0)
        expected = {
            "next": None,
            "previous": None,
            "users": []
        }
        assert actual == expected
        # scene 2 next=Link, previous=Link
        actual = API_functools.manage_next_previous_page(
            request,
            data=[],
            nb_total_data=15,
            limit=5,
            offset=5)
        expected = {
            "next": "/?limit=5&offset=10",
            "previous": "/?limit=5&offset=0",
            "users": []
        }
        assert actual == expected

        # scene 3 next=Link, previous=None
        actual = API_functools.manage_next_previous_page(
            request,
            data=[],
            nb_total_data=10,
            limit=5,
            offset=0)
        expected = {
            "next": "/?limit=5&offset=5",
            "previous": None,
            "users": []
        }
        assert actual == expected

        # scene 4 next=None, previous=Link
        actual = API_functools.manage_next_previous_page(
            request,
            data=[],
            nb_total_data=10,
            limit=5,
            offset=5)
        expected = {
            "next": None,
            "previous": "/?limit=5&offset=0",
            "users": []
        }
        assert actual == expected

    async def test_insert_default_data(self):
        users_inserted = INIT_DATA[:4]
        await API_functools.insert_default_data(data=users_inserted)
        nb_users = await Person.all().count()
        assert nb_users == len(users_inserted)

    async def test_create_default_person(self):
        user_to_create = INIT_DATA[0]
        user_created = await API_functools._create_default_person(user_to_create)
        actual = {
            **user_created.__dict__,
            "gender": user_created.gender.value,
            "date_of_birth": user_created.date_of_birth.strftime("%Y-%m-%d")
        }
        actual.pop('_partial')
        actual.pop('_saved_in_db')
        actual.pop('_custom_generated_pk')
        actual.pop('id')
        assert user_to_create == actual
