from fastapi import FastAPI
from typing import Optional
from utils import get_users, filter_user_by_id
app = FastAPI()


@app.get('/')
def index():
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/users"],
        "docs": ["/docs", "/redoc"],
    }


@app.get('/users')
def users(limit: Optional[int] = 100, offset: Optional[int] = 1, sort: Optional[str] = "id:asc"):
    return get_users(limit, offset, sort)


@app.get('/users/{id}')
def users_by_id(id: int):
    return filter_user_by_id(
        id, {"detail": "Not Found"}
    )
