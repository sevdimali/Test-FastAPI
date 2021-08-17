from functools import cache

from fastapi import APIRouter, status, Request, Response

router = APIRouter()


@cache
@router.get("/", status_code=status.HTTP_200_OK)
async def votes(req: Request, res: Response):
    return []
