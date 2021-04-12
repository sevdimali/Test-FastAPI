import uvicorn
from fastapi import FastAPI
from typing import Optional
from functools import cache
from models import User, PartialUser
from Database import UserTable

app = FastAPI()
user_table = UserTable()


@app.get('/')
def index():
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
    }


@cache
@app.get('/users/')
def users(limit: Optional[int] = 50, offset: Optional[int] = 1, sort: Optional[str] = "id:asc"):
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
    nb_users = UserTable.number_user()
    if offset < 0 or limit < 1:
        return default
    data = {
        "next": None,
        "users": user_table.get_users(limit, offset, sort)
    }
    # manage next data
    if offset < nb_users-1 and limit <= nb_users:
        offset += limit
        data['next'] = f'/users/?limit={limit}&offset={offset}'
    return data


@cache
@app.get('/users/{id}')
def users_by_id(id: int):
    """Get user api\n

    Args:\n
        id (int): user ID\n
    Returns:\n
        User: user found\n
    """
    return user_table.get_user_by_id(id)


@app.post('/users/')
def create_user(user: PartialUser):
    return user_table.post_user(user)


@app.patch('/users/{id}')
def fix_user(id: int, user: PartialUser):
    return user_table.patch_user(id, user)


@app.put('/users/{id}')
def update_user(id: int, new_user: User):
    return user_table.put_user(id, new_user)


@app.delete('/users/{id}')
def delete_user(id: int):
    return user_table.delete_user(id)
