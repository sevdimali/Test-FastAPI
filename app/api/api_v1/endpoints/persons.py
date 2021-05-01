from functools import cache
from fastapi import APIRouter, Request
from typing import Optional, Dict, List, Any

from api.utils import API_functools
from api.api_v1.models.pydantic import User, PartialUser
from api.api_v1.models.tortoise import Person, Person_Pydantic

router = APIRouter()


@cache
@router.get("/")
async def users(
    request: Request,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    sort: Optional[str] = "id:asc",
) -> Optional[List[Dict[str, Any]]]:
    """Get users from data(DB)\n

    Args:\n
        limit (int, optional): max number of returned users. \
        Defaults to 100.\n
        offset (int, optional): first user to return (use with limit). \
        Defaults to 1.\n
        sort (str, optional): the order of the result. \
        attribute:(asc {ascending} or desc {descending}). \
        Defaults to "id:asc".\n
    Returns:\n
        Optional[List[Dict[str, Any]]]: list of users found or \
        Dict with error\n
    """
    response = {
        "success": False,
        "users": [],
    }
    order_by = API_functools.valid_order(User, sort)
    if order_by is None:
        return {
            **response,
            "detail": "Invalid sort parameters. it must match \
            attribute:order. ex: id:asc or id:desc",
        }

    if offset < 0 or limit < 1:
        return {
            **response,
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
    nb_users = await Person.all().count()

    users = await Person_Pydantic.from_queryset(
        Person.all().limit(limit).offset(offset).order_by(order_by)
    )

    if len(users) == 0:
        return {**response, "detail": "Not Found"}

    return API_functools.manage_next_previous_page(
        request, users, nb_users, limit, offset
    )


@cache
@router.get("/{user_id}")
async def users_by_id(user_id: int) -> Dict[str, Any]:
    """Get user api\n

    Args:\n
        user_id (int): user ID\n
    Returns:\n
        Dict[str, Any]: contains user found\n
    """
    user = await Person_Pydantic.from_queryset(Person.filter(pk=user_id))
    data = {
        "success": True,
        "user": API_functools.get_or_default(user, 0, {}),
    }
    if not API_functools.instance_of(data["user"], Person):
        data["success"] = False
        data["detail"] = "Not Found"
    return data


@cache
@router.get("/filter/{user_attribute}/{value}")
async def users_by_attribute(
    user_attribute: Any, value: Any
) -> List[Dict[str, Any]]:
    """Get user by attribute except ID attribute\n

    Args:
        user_attribute (Any): user's attribute\n

    Returns:
        List[Dict[str, Any]]: List of users found
    """
    response = {"success": False, "users": []}
    if not API_functools.is_attribute_of(user_attribute, User):
        return {
            **response,
            "detail": f"""
            Invalid attribute filter.
            Try with: {User.attributes()}
            """,
        }
    kwargs = {}
    kwargs[user_attribute] = value
    person = await Person.get_or_none(**kwargs)

    if person is None:
        return {**response, "detail": "Not Found"}

    data = {**person.__dict__}
    data.pop("_partial", None)
    data.pop("_saved_in_db", None)

    return {"success": True, "users": [data]}


@router.post("/", response_model=Person_Pydantic)
async def create_user(user: User) -> Dict[str, Any]:
    """Create new users\n

    Args:\n
        user (User): User to create\n

    Returns:\n
        Dict[str, Any]: User created\n
    """
    user = await Person.create(**user.__dict__)
    return user


@cache
@router.patch("/{user_id}")
async def fix_user(user_id: int, user: PartialUser) -> Dict[str, Any]:
    """Fix some users attributes except his ID\n

    Args:\n
        user_id (int): user ID\n
        user_data (User): new data\n

    Returns:\n
        Dict[str, Any]: contains User new data or error\n
    """
    response = {"success": False, "user": {}}

    """(More control to the validator)
    Prefer this method to use the Pydantic validator \
    which is more maintainable
    than the tortoiseORM validator in my opinion
    see: https://pydantic-docs.helpmanual.io/usage/validators/
    """
    user_found = await Person.get_or_none(id=user_id)
    if user_found is None:
        response["detail"] = "User with ID {user_id} doesn't exist."
        return response

    user_updated = user_found.update_from_dict(
        {**user.__dict__, "id": user_found.id}
    )
    await user_updated.save()
    return await Person_Pydantic.from_tortoise_orm(user_updated)


@cache
@router.put("/{user_id}")
async def update_user(user_id: int, new_data: User) -> Dict[str, Any]:
    """Transfer data from one user to another\n

    Args:\n
        user_id (int): user who transfers the data and will be deleted\n
        new_user (int): user receiving data, \
        its data will be updated with the data of the first user\n

    Returns:\n
        Dict[str, Any]: contains User new data or error\n
    """
    response = {"success": False, "user": {}}

    # check if user exists
    curr_user = await Person.get_or_none(id=user_id)
    if curr_user is None:  # pragma no cover
        response["detail"] = f"User with ID {user_id} doesn't exist."
        return response

    curr_user = await curr_user.update_from_dict(new_data.__dict__)
    await curr_user.save()
    return await Person_Pydantic.from_tortoise_orm(curr_user)


@router.delete("/{user_id}")
async def delete_user(user_id: int) -> Dict[str, Any]:
    """Delete a user\n

    Args:\n
        user_id (int): user to delete\n

    Returns:\n
        Dict[str, Any]: contains deleted User data or error\n
    """
    response = {"success": False, "user": {}}

    user_found = await Person.get_or_none(id=user_id)
    if not user_found:
        response["detail"] = f"User with ID {user_id} doesn't exist"
        return response

    await user_found.delete()

    response["success"] = True
    response["user"] = user_found.__dict__
    response["user"].pop("_partial", None)
    response["user"].pop("_saved_in_db", None)
    response["detail"] = f"User {user_id} delete successfully ⭐"
    return response
