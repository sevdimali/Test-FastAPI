import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, validator
from email_validator import validate_email, EmailNotValidError

from api.api_v1.models.types import Gender

avatar = "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1"


class PartialUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    avatar: Optional[str]
    company: Optional[str]
    job: Optional[str]

    @classmethod
    def attributes(cls):
        """Return class object attributes except ID\n

        Returns:
            tuple[str]: attributes
        """
        return tuple(cls.__dict__.get("__fields__", {}).keys())

    @validator("last_name", "first_name", "job", "company")
    def between_3_and_50_characters(cls, value: str, **kwargs) -> str:
        """Validate str attributes that must contains minimum 3 characters\
            and maximum 50 characters\n

        Args:\n
            value (str): attribute to validate

        Raises:
            ValueError: if constraint not respected

        Returns:
            str: validate attribute
        """
        str_to_validate = value.title().strip()
        if not (3 <= len(str_to_validate) <= 50):
            raise ValueError(
                f"{kwargs['field'].name} must contain between 3 and 50 \
                    characters."
            )
        return value

    @validator("avatar")
    def valid_url_avatar(cls, value: str, **kwargs) -> str:
        """Validate url\n

        Args:\n
            value (str): url avatar to validate

        Raises:
            ValueError: if constraint not respected

        Returns:
            str: validate attribute
        """
        value = value.title().strip().lower()
        patt = (
            r"(https?:\/\/(www\.)?|(www\.))([\w\-\_\.]+)(\.[a-z]{2,10})(\/.+)?"
        )
        result = re.match(
            patt,
            value,
        )
        if result is None:
            raise ValueError(f"{kwargs['field'].name} must be a valid url.")
        return value

    @validator("email")
    def valid_email(cls, value: str, **kwargs) -> str:
        """Validate email attribute using validate_email package

        Args:
            value (str): current email to validate

        Raises:
            ValueError: if email invalid

        Returns:
            [str]: email
        """
        value = value.title().strip()
        try:
            validate_email(value)
        except EmailNotValidError:
            raise ValueError(
                f"{kwargs['field'].name} is not a valid email address."
            )
        return value.lower()

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "DOE",
                "email": "john.doe@eliam-lotonga.fr",
                "avatar": avatar,
                "job": "Compensation Analyst",
                "company": "Edgetag",
            }
        }


class User(PartialUser):
    is_admin: Optional[bool] = False
    gender: Gender
    date_of_birth: date
    country_of_birth: str

    @validator("country_of_birth")
    def between_3_and_50_characters(cls, value: str) -> Optional[str]:
        return super().between_3_and_50_characters(value)

    class Config:
        schema_extra = {
            "example": {
                "is_admin": False,
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
        }
