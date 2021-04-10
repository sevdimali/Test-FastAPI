from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    is_admin: Optional[bool] = False
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = False
