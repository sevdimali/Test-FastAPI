from datetime import date

from pydantic import BaseModel, ValidationError, validator
from typing import Optional
from email_validator import validate_email, EmailNotValidError

from api.api_v1.models.types import Gender


class PartialUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender
    date_of_birth: date
    country_of_birth: str

    @validator('last_name', 'first_name', 'country_of_birth')
    def between_3_and_50_characters(cls, value, **kwargs):
        value = value.title().strip()
        if not (3 <= len(value) <= 50):
            raise ValueError(
                f"{kwargs['field'].name} must contain between 3 and 50 characters.")
        return value

    @validator('email')
    def valid_email(cls, value, **kwargs):
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
                "first_name": "John",
                "last_name": "DOE",
                "email": "john.doe@eliam-lotonga.fr",
                "gender": "Male",
                "date_of_birth": "1970-01-01",
                "country_of_birth": "No where",
            }
        }


class User(PartialUser):
    id: int
    is_admin: Optional[bool] = False

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "is_admin": False,
                "first_name": "John",
                "last_name": "DOE",
                "email": "john.doe@eliam-lotonga.fr",
                "gender": "Male",
                "date_of_birth": "1970-01-01",
                "country_of_birth": "No where",
            }
        }
