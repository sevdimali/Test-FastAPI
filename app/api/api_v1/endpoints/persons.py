from functools import cache
from fastapi import APIRouter, Request
from typing import Optional

from api.utils import API_functools
from api.api_v1.models.pydantic import PartialUser, User
from api.api_v1.models.tortoise import Person, Person_Pydantic

router = APIRouter()


@cache
@router.get('/')
async def users(
    request: Request,
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
    order_by = API_functools.valid_order(User, sort)

    if order_by is None:
        return {
            "success": False,
            "users": [],
            "detail": "Invalid sort parameters. it must match attribute:order. ex: id:asc or id:desc"
        }

    if offset < 0 or limit < 1:
        return {
            "success": False,
            "users": [],
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
    nb_users = await Person.all().count()  # UserTable.number_user()

    users = await Person_Pydantic.from_queryset(
        Person.all().limit(limit).offset(offset).order_by(order_by))
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
        base = request.scope.get("path")
        data['next'] = f'{base}?limit={limit}&offset={offset}'
    return data


@cache
@router.get('/{user_id}')
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


@router.post('/', response_model=Person_Pydantic)
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


@router.patch('/{user_id}')
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


@router.put('/{user_id}')
async def update_user(user_id: int, new_user: int):
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
    if user_id == 1 or new_user == 1:
        response['detail'] = "Cannot update user with ID {user_id}. 🥺"

    if user_id == new_user:
        response['detail'] = "Action not allowed."
        return response

    # check if user exists
    user_to_delete = await Person.get_or_none(id=user_id)
    user_to_update = await Person.get_or_none(id=new_user)
    cur_id = user_id if not user_to_delete else new_user
    if user_to_update is None or user_to_delete is None:
        response["detail"] = f"User with ID {cur_id} doesn't exist."
        return response
    data = {**user_to_delete.__dict__}
    data.pop('_partial', None)
    data.pop('_saved_in_db', None)
    data.pop('id', None)
    user_updated = await user_to_update.update_from_dict(data)
    await user_updated.save()
    await user_to_delete.delete()
    return await Person_Pydantic.from_tortoise_orm(user_updated)


@router.delete('/{user_id}')
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
    user_still_there = await Person.exists(id=user_id)
    if user_still_there:
        response['detail'] = f"Error while deleting user {user_id}"
        return response

    response['success'] = True
    response['user'] = user_found.__dict__
    response['user'].pop('_partial', None)
    response['user'].pop('_saved_in_db', None)
    response['detail'] = f"User {user_id} delete successfully ⭐"
    return response
