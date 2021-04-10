from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_admin: Option[bool] = False
    is_staff: Option[bool] = False
    is_active: Option[bool] = False
