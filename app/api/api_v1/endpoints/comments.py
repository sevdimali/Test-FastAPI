from functools import cache
from typing import Optional, Dict, List, Any

from fastapi import APIRouter, status, Request, Response

from api.utils import API_functools
from api.api_v1.models.pydantic import Comment as CommentBaseModel
from api.api_v1.models.tortoise import Comment, Comment_Pydantic

router = APIRouter()


@cache
@router.get("/", status_code=status.HTTP_200_OK)
async def comments(
    request: Request,
    res: Response,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    sort: Optional[str] = "id:asc",
) -> Optional[List[Dict[str, Any]]]:

    """Get all comments or some of them using 'offset' and 'limit'\n

    Args:\n
        limit (int, optional): max number of returned comments. \
        Defaults to 100.\n
        offset (int, optional): first comment to return (use with limit). \
        Defaults to 1.\n
        sort (str, optional): the order of the result. \
        attribute:(asc {ascending} or desc {descending}). \
        Defaults to "id:asc".\n
    Returns:\n
        Optional[List[Dict[str, Any]]]: list of comments found or \
        Dict with error\n
    """
    response = {
        "success": False,
        "comments": [],
    }
    order_by = API_functools.valid_order(CommentBaseModel, sort)
    if order_by is None:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {
            **response,
            "detail": "Invalid sort parameters. it must match \
            attribute:order. ex: id:asc or id:desc",
        }

    if offset < 0 or limit < 1:
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {
            **response,
            "detail": "Invalid values: offset(>=0) or limit(>0)",
        }
    nb_comments = await Comment.all().count()

    comments = await Comment_Pydantic.from_queryset(
        Comment.all().limit(limit).offset(offset).order_by(order_by)
    )

    if len(comments) == 0:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {**response, "detail": "Not Found"}

    return API_functools.manage_next_previous_page(
        request, comments, nb_comments, limit, offset
    )
