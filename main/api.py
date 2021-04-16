from functools import cache

import uvicorn
from fastapi import FastAPI
from tortoise import Tortoise, run_async
from typing import Optional

from utils import API_functools
from settings import DATABASE_CONFIG
from baseModels import PartialUser, User
from models import Person, Person_Pydantic_List
from database import Database
app = FastAPI(title="My Super Project",
              description="This is a very fancy project, with auto docs for the API and everything",
              version="1.0.0")

Database.connect(app)


@app.get('/')
async def index():
    p = Person(
        is_admin=True,
        first_name="John", last_name="DOE",
        email="john.doe@gmail.com", gender="Female",
        date_of_birth="1970-01-01", country_of_birth="No where"
    )
    # re = await p.save()
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
        "openapi": "/openapi.json"
    }


@cache
@app.get('/users/')
async def users(limit: Optional[int] = 50, offset: Optional[int] = 0, sort: Optional[str] = "id:asc"):
    """Get users from data(DB)\n

    Args:\n
        limit (int, optional): max number of returned users. Defaults to 100.\n
        offset (int, optional): first user to return (use with limit). Defaults to 1.\n
        sort (str, optional): the order of the result. \
            attribute:(asc {ascending} or desc {descending}). Defaults to "id:asc".\n
        default (list, optional): default value if not found. Defaults to [].\n
    Returns:\n
        List[User]: list of users found\n
    """
    if offset < 0 or limit < 1:
        return {
            "success": False,
            "users": [],
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
    nb_users = await Person.all().count()  # UserTable.number_user()

    users = await Person_Pydantic_List.from_queryset(
        Person.all().limit(limit).offset(offset))
    users = users.dict()['__root__']
    data = {
        "next": None,
        "users": users
    }
    if len(users) == 0:
        return data

    # manage next data
    if offset < nb_users-1 and limit <= nb_users:
        offset += limit
        data['next'] = f'/users/?limit={limit}&offset={offset}'
    return data


@cache
@app.get('/users/{id}')
async def users_by_id(id: int):
    """Get user api\n

    Args:\n
        id (int): user ID\n
    Returns:\n
        User: user found\n
    """
    user = await Person_Pydantic_List.from_queryset(
        Person.filter(pk=id))
    data = {
        "success": True,
        "user": API_functools.get_or_default(
            user.dict()['__root__'], 0, {}),
    }
    if len(data['user'].keys()) == 0:
        data["detail"] = "Not found"
    return data


@app.post('/users/')
def create_user(user: PartialUser):
    """Create new users\n

    Args:\n
        user_data (PartialUser): User to create\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.post_user(user)


@app.patch('/users/{id}')
def fix_user(id: int, user: PartialUser):
    """Fix some users attributes except his ID\n

    Args:\n
        user_id (int): user ID\n
        user_data (PartialUser): new data\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.patch_user(id, user)


@app.put('/users/{id}')
def update_user(id: int, new_user: User):
    """Replace user by another\n

    Args:\n
        user_id (int): user to replace, his ID\n
        new_user (User): new user\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.put_user(id, new_user)


@app.delete('/users/{id}')
def delete_user(id: int):
    """Delete a user\n

    Args:\n
        user_id (int): user to delete, his ID\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.delete_user(id)
