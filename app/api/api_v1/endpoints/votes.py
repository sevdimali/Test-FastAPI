from functools import cache

from fastapi import APIRouter, status, Request, Response

router = APIRouter()


@cache
@router.get("/", status_code=status.HTTP_404_NOT_FOUND)
async def votes(req: Request, res: Response):
    return {"detail": "Not Found", "success": False, "votes": []}
