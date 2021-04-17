from fastapi import FastAPI

from api.api_v1.storage.database import Database
from api.api_v1.api import router as api_router


app = FastAPI(
    title="My Super Project",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="1.0.0"
    # , servers=[
    #     {"url": "https://stag.example.com", "description": "Staging environment"},
    #     {"url": "https://prod.example.com", "description": "Production environment"},
    # ],
    # root_path="/api/v1",
    # root_path_in_servers=False,
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
