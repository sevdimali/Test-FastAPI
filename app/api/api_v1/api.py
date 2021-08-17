from fastapi import APIRouter

from .endpoints import persons
from .endpoints import comments
from .endpoints import votes

router = APIRouter()

router.include_router(persons.router, prefix="/users", tags=["users"])
router.include_router(comments.router, prefix="/comments", tags=["comments"])
router.include_router(votes.router, prefix="/votes", tags=["votes"])
