from fastapi import FastAPI
from utils import filter_user_by_id

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
        "detail": "Welcome to API",
        "routes": ["/users"]
    }


@app.get('/users')
def index():
    return data


@app.get('/users/{id}')
def index(id: int):
    return filter_user_by_id(
        data, id, {"detail": "Not Found"}
    )


@app.get('/about')
def about():
    data = {'name': "About page"}
    return data
