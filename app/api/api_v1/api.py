from fastapi import APIRouter

from .endpoints import persons

router = APIRouter()

router.include_router(persons.router, prefix="/users", tags=["users"])
