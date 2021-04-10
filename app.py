from fastapi import FastAPI
from utils import get_users, filter_user_by_id

app = FastAPI()

data = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@gmail.com"
    },
    {
        "id": 2,
        "first_name": "Marie",
        "last_name": "Smith",
        "email": "marie.smith@gmail.com"
    },
    {
        "id": 3,
        "first_name": "Anne",
        "last_name": "Jones",
        "email": "anne.jones@gmail.com"
    },
    {
        "id": 4,
        "first_name": "Adam",
        "last_name": "Parker",
        "email": "adam.parker@hotmail.com.uk"
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
def users(limit: int = 100, offset: int = 1):
    return get_users(data, limit, offset)


@app.get('/users/{id}')
def users_by_id(id: int):
    return filter_user_by_id(
        data, id, {"detail": "Not Found"}
    )


@app.get('/about')
def about():
    data = {'name': "About page"}
    return data
