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
            print(el, instance)
            assert API_functools.instance_of(el, instance) == True
