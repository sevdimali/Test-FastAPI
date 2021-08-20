import pytest

from pydantic import BaseConfig, Field
from pydantic.fields import ModelField
from tortoise.contrib import test

from app.api.utils import API_functools
from app.api.api_v1.models.pydantic import Comment


class TestComment(test.TestCase):
    def test_user_attributes(self):
        comment_attributes = ("owner", "added", "content")
        assert API_functools.get_attributes(Comment) == comment_attributes

    def test_as_least_1_character(self):
        f = Field(..., min_length=1)
        field = ModelField(
            name="content",
            type_=str,
            class_validators={},
            field_info=f,
            model_config=BaseConfig,
        )
        with pytest.raises(ValueError):
            Comment.at_least_1_character("        ", field=field)
            Comment.at_least_1_character("", field=field)
        assert Comment.at_least_1_character("First comment") == "First comment"
