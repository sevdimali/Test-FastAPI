from fastapi import FastAPI

from api.api_v1.api import router as api_router
from api.api_v1.storage.database import Database


app = FastAPI(
    title="My Super Project",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="1.0.0"
)

API_BASE_URL = "/api/v1"

Database.connect(app)


@app.get('/')
async def index():
    return {
        "detail": "Welcome to my API build with Python FastApi",
        "apis": ["/api/v1/users"],
        "docs": ["/docs", "/redoc"],
        "openapi": "/openapi.json"
    }

app.include_router(api_router, prefix=API_BASE_URL)
