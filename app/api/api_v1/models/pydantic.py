import re
from datetime import date

from pydantic import BaseModel, ValidationError, validator
from typing import Optional
from email_validator import validate_email, EmailNotValidError

from api.api_v1.models.types import Gender


class User(BaseModel):
    is_admin: Optional[bool] = False
    first_name: str
    last_name: str
    email: str
    gender: Gender
    avatar: Optional[str]
    company: Optional[str]
    job: Optional[str]
    date_of_birth: date
    country_of_birth: str

    @validator('last_name', 'first_name', 'country_of_birth', 'job', 'company')
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
                f"{kwargs['field'].name} must contain between 3 and 50 characters.")
        return value

    @validator('avatar')
    def valid_url(cls, value: str, **kwargs) -> str:
        """Validate url\n

        Args:\n
            value (str): url avatar to validate

        Raises:
            ValueError: if constraint not respected

        Returns:
            str: validate attribute
        """
        value = value.title().strip().lower()
        result = re.match(
            '((https?:\/\/(www\.)?|(www\.))([\w\-\_\.]+)(\.[a-z]{2,10})(\/.+)?)',
            value)
        if result is None:
            raise ValueError(
                f"{kwargs['field'].name} must be a valid url.")
        return value

    @validator('email')
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
            valid = validate_email(value)
        except EmailNotValidError:
            raise ValueError(
                f"{kwargs['field'].name} is not a valid email address.")
        return value.lower()

    class Config:
        schema_extra = {
            "example": {
                "is_admin": False,
                "first_name": "John",
                "last_name": "DOE",
                "email": "john.doe@eliam-lotonga.fr",
                "gender": "Male",
                "avatar": "https://robohash.org/autdoloremaccusamus.png?size=150x150&set=set1",
                "job": "Compensation Analyst",
                "company": "Edgetag",
                "date_of_birth": "1970-01-01",
                "country_of_birth": "No where"
            }
        }
