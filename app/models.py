from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date
from functools import cache
import json


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"


class PartialUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender
    date_of_birth: date
    country_of_birth: str


class User(PartialUser):
    id: int
    is_admin: Optional[bool] = False
