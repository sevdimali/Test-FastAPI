from fastapi import FastAPI
from utils import get_users, filter_user_by_id

app = FastAPI()

data = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@gmail.com",
        "is_admin": True,
        "is_staff": True,
        "is_active": True,
    },
    {
        "id": 2,
        "first_name": "Marie",
        "last_name": "Smith",
        "email": "marie.smith@gmail.com",
        "is_admin": False,
        "is_staff": True,
        "is_active": True,
    },
    {
        "id": 3,
        "first_name": "Anne",
        "last_name": "Jones",
        "email": "anne.jones@gmail.com",
        "is_admin": False,
        "is_staff": False,
        "is_active": True,
    },
    {
        "id": 4,
        "first_name": "Adam",
        "last_name": "Parker",
        "email": "adam.parker@hotmail.com.uk",
        "is_admin": False,
        "is_staff": False,
        "is_active": True,
    }
]


@app.get('/')
def index():
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
    }


@app.get('/users')
def users(limit: int = 100, offset: int = 1, sort: str = "id:asc"):
    """Get users api

    Args:
        limit (int, optional): max number of returned users. Defaults to 100.
        offset (int, optional): first user to return (use with limit). Defaults to 1.
        sort (str, optional): the order of the result. \
            attribute:(ascending [asc] or descending [desc]). Defaults to "id:asc".
    Returns:
        [List]: list of users found 
    """
    return get_users(data, limit, offset, sort)


@app.get('/users/{id}')
def users_by_id(id: int):
    """Get user api

    Args:
        id (int): user ID

    Returns:
        [object]: user found
    """
    return filter_user_by_id(
        data, id, {"detail": "Not Found"}
    )


@app.get('/about')
def about():
    data = {'name': "About page"}
    return data
