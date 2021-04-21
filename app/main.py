from typing import Dict, Any
import uvicorn
from starlette.responses import RedirectResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.settings import get_config_env
from api.api_v1.models.tortoise import Person
from api.api_v1.api import router as api_router
from api.api_v1.storage.database import Database
from api.api_v1.settings import CORS_MIDDLEWARE_CONFIG
from api.utils import API_functools

API_BASE_URL = "/api/v1"
app = FastAPI(
    title="My Super API",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="1.0.0"
    # , servers=[
    #     {"url": "https://stag.example.com", "description": "Staging environment"},
    #     {"url": "https://prod.example.com", "description": "Production environment"},
    # ],
    # root_path= API_BASE_URL,
    # root_path_in_servers=False,
)

app.add_middleware(
    CORSMiddleware,
    **CORS_MIDDLEWARE_CONFIG
)


@app.get('/data')
async def index() -> Dict[str, Any]:
    """loading fake data

    Returns:
        redirect to root path / 
    """
    await API_functools.insert_default_data()
    return RedirectResponse(url='/')


@app.get('/')
async def index() -> Dict[str, Any]:
    """root path, returns some API paths

    Returns:
        Dict[str, Any]: Api routes 
    """
    return {
        "detail": "Welcome to FastAPI",
        "apis": ["/api/v1/users"],
        "fake_data": "/data",
        "docs": ["/docs", "/redoc"],
        "openapi": "/openapi.json"
    }

app.include_router(api_router, prefix=API_BASE_URL)

if __name__ == '__main__':
    # DB connection
    Database.connect(app)

    # Run app
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=get_config_env()['port'])
