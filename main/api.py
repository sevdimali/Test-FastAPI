from functools import cache

import uvicorn
from fastapi import FastAPI
from typing import Optional

from utils import API_functools
from baseModels import PartialUser, User
from models import Person
from models import Person_Pydantic
from database import Database
app = FastAPI(title="My Super Project",
              description="This is a very fancy project, with auto docs for the API and everything",
              version="1.0.0")

Database.connect(app)


@app.get('/')
async def index():
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
@app.get('/users/{user_id}')
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


@app.patch('/users/{user_id}')
async def fix_user(user_id: int, user: PartialUser):
    """Fix some users attributes except his ID\n

    Args:\n
        user_id (int): user ID\n
        user_data (PartialUser): new data\n

    Returns:\n
        dict: Success operation\n
    """
    response = {
        "success": False,
        "user": {}
    }
    # await Person.filter(id=user_id).update(**user.dict(exclude_unset=True))
    # return await Person_Pydantic.from_queryset_single(Person.get(id=user_id))

    """
    Prefer this method to use the Pydantic validator which is more maintainable
    than the tortoiseORM validator.py in my opinion
    see: https://pydantic-docs.helpmanual.io/usage/validators/
    """
    if user_id == 1:
        response['detail'] = "Cannot patch user with ID {user_id}. 🥺"
        return response

    user_found = await Person.get_or_none(id=user_id)
    if user_found is None:
        response['detail'] = "User with ID {user_id} doesn't exist."
        return response

    user_updated = user_found.update_from_dict(
        {**user.__dict__, "id": user_found.id,
         "is_admin": user_found.is_admin}
    )
    await user_updated.save()
    return await Person_Pydantic.from_tortoise_orm(user_updated)


@app.put('/users/{user_id}')
async def update_user(user_id: int, new_user: User):
    """Replace user by another\n

    Args:\n
        user_id (int): user to replace, his ID\n
        new_user (User): new user\n

    Returns:\n
        dict: Success operation\n
    """
    response = {
        "success": False,
        "user": {}
    }
    if user_id == 1:
        response['detail'] = "Cannot update user with ID {user_id}. 🥺"

    if user_id == new_user.id:
        response['detail'] = "Please use Patch route instead."
        return response

    old_user_found = await Person.get_or_none(id=user_id)
    if old_user_found is None:
        response["detail"] = f"User with ID {user_id} doesn't exist."
        return response

    # check if new id is already in use
    new_user_found = await Person.get_or_none(id=new_user.id)
    if not new_user_found is None:
        response['detail'] = f"This ID {new_user.id} is already in use"
        return response
    """
    clone the old user
    update the clone's attributes and save it
    delete the old user
    """
    # del data['id']
    # new_user = old_user_found.clone(pk=new_user.id)
    # await new_user.update_from_dict(data).save()
    # await new_user.save(force_create=True, update_fields=True)
    await old_user_found.delete()
    new_user = await Person.create(**new_user.__dict__)
    return await Person_Pydantic.from_tortoise_orm(new_user)


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    """Delete a user\n

    Args:\n
        user_id (int): user to delete, his ID\n

    Returns:\n
        dict: Success operation\n
    """
    response = {
        "success": False,
        "user": {}
    }
    if user_id == 1:
        response['detail'] = f"Cannot delete user with ID {user_id}. 🥺"
        return response

    user_found = await Person.get_or_none(id=user_id)
    return_data = {

    }
    if not user_found:
        response['detail'] = f"User with ID {user_id} doesn't exist"
        return response

    await user_found.delete()
    print("ID", user_found.id)
    user_still_there = await Person.exists(id=user_id)
    print("user still there", user_still_there)
    if user_still_there:
        response['detail'] = f"Error while deleting user {user_id}"
        return response

    response['success'] = True
    response['user'] = user_found.__dict__
    del response['user']['_partial']
    del response['user']['_saved_in_db']
    response['detail'] = f"User {user_id} delete successfully ⭐"
    return response
