import subprocess

import uvicorn
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.models.tortoise import Person
from api.api_v1.api import router as api_router
from api.api_v1.storage.database import Database
from api.api_v1.settings import CORS_MIDDLEWARE_CONFIG
from api.utils import API_functools

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

app.add_middleware(
    CORSMiddleware,
    **CORS_MIDDLEWARE_CONFIG
)

API_BASE_URL = "/api/v1"

Database.connect(app)


@app.get('/')
async def index() -> Dict[str, Any]:
    """root path, returns some API paths

    Returns:
        Dict[str, Any]: Api routes 
    """
    count_db_data = await Person.all().count()
    if count_db_data == 0:
        await API_functools.insert_default_data()

    return {
        "detail": "Welcome to FastAPI",
        "apis": ["/api/v1/users"],
        "docs": ["/docs", "/redoc"],
        "openapi": "/openapi.json"
    }

app.include_router(api_router, prefix=API_BASE_URL)

if __name__ == '__main__':
    # Run app
    uvicorn.run(app, host="0.0.0.0", port=80)
