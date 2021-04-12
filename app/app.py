import uvicorn
from fastapi import FastAPI
from typing import Optional
from models import User, PartialUser
from utils import get_users, filter_user_by_id
from utils import post_user, put_user, patch_user
from utils import delete_user
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


@app.get('/users/')
def users(limit: Optional[int] = 50, offset: Optional[int] = 1, sort: Optional[str] = "id:asc"):
    return user_table.get_users(limit, offset, sort)


@ app.get('/users/{id}')
def users_by_id(id: int):
    db_user = user_table.get_user_by_id(id)
    print(db_user)
    return filter_user_by_id(
        id, default=(("detail", "Not Found"),)
    )


@ app.post('/users/')
def create_user(user: PartialUser):
    return user_table.post_user(user)


@ app.patch('/users/{id}')
def fix_user(id: int, user: PartialUser):
    return user_table.patch_user(id, user)


@ app.put('/users/{id}')
def update_user(id: int, new_user: User):
    return user_table.put_user(id, new_user)


@ app.delete('/users/{id}')
def delete_user(id: int):
    return user_table.delete_user(id)
