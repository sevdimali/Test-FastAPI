from datetime import date

from pydantic import BaseModel
from typing import Optional

from customTypes import Gender


class PartialUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender
    date_of_birth: date
    country_of_birth: str


class User(PartialUser):
    id: int
