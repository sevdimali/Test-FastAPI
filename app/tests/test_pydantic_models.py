import pytest

from pydantic import BaseConfig, Field
from pydantic.fields import ModelField
from tortoise.contrib import test

from api.api_v1.models.pydantic import User, PartialUser

url_regex = (
    r"(https?:\/\/(www\.)?|(www\.))([\w\-\_\.]+)(\.[a-z]{2,10})(\/[^\s,%]+)?"
)


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

    def test_between_3_and_50_characters(self):
        f = Field(..., min_length=3, max_length=50)
        field = ModelField(
            name="name",
            type_=str,
            class_validators={},
            field_info=f,
            model_config=BaseConfig,
        )
        with pytest.raises(ValueError):
            long_text = "Lorem Ipsum is simply dummy text of\
                the printing and typesetting industry. "
            PartialUser.between_3_and_50_characters("He", field=field)
            PartialUser.between_3_and_50_characters(
                long_text,
                field=field,
            )
        assert PartialUser.between_3_and_50_characters("Hello") == "Hello"

    def test_valid_url_avatar(self):
        f = Field(
            ...,
            regex=url_regex,
        )
        field = ModelField(
            name="name",
            type_=str,
            class_validators={},
            field_info=f,
            model_config=BaseConfig,
        )
        with pytest.raises(ValueError):
            bad_urls_format = [
                "http://www.example.com/,,main.html",
                "http://www.example.com/ main.html",
                "http:www.example.com/main.html",
            ]
            for url in bad_urls_format:
                PartialUser.valid_url_avatar(url, field=field)

        good_urls_format = [
            "https://www.eliam-lotonga.fr/about",
            "http://www.john-doe.com/",
            "http://www.example.com/main.html",
        ]
        for url in good_urls_format:
            assert PartialUser.valid_url_avatar(url, field=field) == url
