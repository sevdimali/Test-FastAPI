from functools import cache

import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise import Tortoise, run_async
from typing import Optional, List

from utils import API_functools
from settings import DATABASE_CONFIG
from baseModels import PartialUser, User
from models import Person
from models import Person_Pydantic, PersonIn_Pydantic
from database import Database
app = FastAPI(title="My Super Project",
              description="This is a very fancy project, with auto docs for the API and everything",
              version="1.0.0")

Database.connect(app)


@app.get('/')
async def index():
    # re = await p.save()
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
        "openapi": "/openapi.json"
    }


@cache
@app.get('/users/')
async def users(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    sort: Optional[str] = "id:asc"
):
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

    users = await Person_Pydantic.from_queryset(
        Person.all().limit(limit).offset(offset))
    data = {
        "next": None,
        "users": users
    }
    if len(users) == 0:
        data['detail'] = "Not Found"
        return data

    # manage next data
    if offset < nb_users-1 and limit <= nb_users:
        offset += limit
        data['next'] = f'/users/?limit={limit}&offset={offset}'
    return data


@cache
@app.get('/users/{id}')
async def users_by_id(user_id: int):
    """Get user api\n

    Args:\n
        id (int): user ID\n
    Returns:\n
        User: user found\n
    """
    user = await Person_Pydantic.from_queryset(
        Person.filter(pk=user_id))
    data = {
        "success": True,
        "user": API_functools.get_or_default(
            user, 0, {}),
    }
    if not API_functools.instance_of(data['user'], Person):
        data["detail"] = "Not Found"
    return data


@app.post('/users/', response_model=Person_Pydantic)
async def create_user(user: PartialUser):
    """Create new users\n

    Args:\n
        user_data (PartialUser): User to create\n

    Returns:\n
        dict: Success operation\n
    """
    user = await Person.create(
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        email=user.email,
        date_of_birth=user.date_of_birth,
        country_of_birth=user.country_of_birth
    )
    return user


@app.patch('/users/{id}', response_model=Person_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def fix_user(user_id: int, user: PersonIn_Pydantic):
    """Fix some users attributes except his ID\n

    Args:\n
        user_id (int): user ID\n
        user_data (PartialUser): new data\n

    Returns:\n
        dict: Success operation\n
    """
    # TODO with pydantic or tortoise validator
    await Person.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await Person_Pydantic.from_queryset_single(Person.get(id=user_id))


@ app.put('/users/{id}')
def update_user(id: int, new_user: User):
    """Replace user by another\n

    Args:\n
        user_id (int): user to replace, his ID\n
        new_user (User): new user\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.put_user(id, new_user)


@ app.delete('/users/{id}')
def delete_user(id: int):
    """Delete a user\n

    Args:\n
        user_id (int): user to delete, his ID\n

    Returns:\n
        dict: Success operation\n
    """
    return []  # user_table.delete_user(id)
