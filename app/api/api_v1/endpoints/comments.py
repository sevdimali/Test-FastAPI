from functools import cache
from typing import Optional, Dict, List, Any

from fastapi import APIRouter, status, Request, Response
from fastapi.encoders import jsonable_encoder

from app.api.utils import API_functools
from app.api.api_v1.models.pydantic import Comment as CommentBaseModel
from app.api.api_v1.models.tortoise import Comment, Person


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
    order_by = API_functools.valid_order(
        CommentBaseModel, sort, replace={"user": "user_id"}
    )

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

    comments = jsonable_encoder(
        await Comment.all()
        .limit(limit)
        .offset(offset)
        .order_by(order_by)
        .values(
            *API_functools.get_attributes(
                CommentBaseModel,
                replace={"user": "user_id"},
                add=("id",),
            )
        )
    )

    if len(comments) == 0:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {**response, "detail": "Not Found"}

    return API_functools.manage_next_previous_page(
        request, comments, nb_comments, limit, offset, data_type="comments"
    )


@cache
@router.get("/{comment_ID}", status_code=status.HTTP_200_OK)
async def comments_by_ID(res: Response, comment_ID: int) -> Dict[str, Any]:
    """Get comment by ID\n

    Args:\n
        comment_ID (int): comment ID\n
    Returns:\n
        Dict[str, Any]: contains comment found\n
    """

    comment = jsonable_encoder(
        await Comment.filter(pk=comment_ID).values(
            *API_functools.get_attributes(
                CommentBaseModel,
                replace={"user": "user_id"},
                add=("id",),
            )
        )
    )
    data = {
        "success": True,
        "comment": API_functools.get_or_default(comment, index=0, default={}),
    }
    if len(comment) == 0:
        res.status_code = status.HTTP_404_NOT_FOUND
        data["success"] = False
        data["detail"] = "Not Found"
    return data


@cache
@router.get("/user/{user_ID}", status_code=status.HTTP_200_OK)
async def comments_by_user(res: Response, user_ID: int) -> Dict[str, Any]:
    """Get comment by ID\n

    Args:\n
        comment_ID (int): comment ID\n
    Returns:\n
        Dict[str, Any]: contains comment found\n
    """
    data = {
        "success": True,
        "comments": [],
    }

    person = await Person.filter(pk=user_ID).first()

    if person is None:
        res.status_code = status.HTTP_404_NOT_FOUND
        data["success"] = False
        data["detail"] = "Comment owner doesn't exist"
        return data

    data["comments"] = jsonable_encoder(
        await Comment.filter(user_id=user_ID).values(
            *API_functools.get_attributes(
                CommentBaseModel,
                replace={"user": "user_id"},
                add=("id",),
            )
        )
    )

    if len(data["comments"]) == 0:
        res.status_code = status.HTTP_404_NOT_FOUND
        data["success"] = False
        data["detail"] = "Not Found"
    return data
