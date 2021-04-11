from fastapi import FastAPI
from typing import Optional
from models import User, PartialUser
from utils import get_users, filter_user_by_id
from utils import post_user, put_user, patch_user
from utils import delete_user
app = FastAPI()


@app.get('/')
def index():
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
    }


@app.get('/users/')
def users(limit: Optional[int] = 100, offset: Optional[int] = 1, sort: Optional[str] = "id:asc"):
    return get_users(limit, offset, sort)


@app.get('/users/{id}')
def users_by_id(id: int):
    return filter_user_by_id(
        id, default=(("detail", "Not Found"),)
    )


@app.post('/users/')
def create_user(user: PartialUser):
    return post_user(user)


@app.patch('/users/{id}')
def fix_user(id: int, user: PartialUser):
    return patch_user(id, user)


@app.put('/users/{id}')
def update_user(id: int, new_user: User):
    return put_user(id, new_user)


@app.delete('/users/{id}')
def update_user(id: int):
    return delete_user(id)
