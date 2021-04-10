import itertools
from functools import cache
from models import PartialUser, User
import data

users = getattr(data, "users", [])


@cache
def get_users(limit=100, offset=1, sort="id:asc", default=[]):
    """Get users from data(DB)\n

    Args:\n
        limit (int, optional): max number of returned users. Defaults to 100.\n
        offset (int, optional): first user to return (use with limit). Defaults to 1.\n
        sort (str, optional): the order of the result. \
            attribute:(asc {ascending} or desc {descending}). Defaults to "id:asc".\n
        default (list, optional): default value if not found. Defaults to [].\n
    Returns:\n
        List[User]: list of users found\n
    """
    key, order, *_ = sort.lower().split(':')
    reverse = order == "desc"
    if offset < 1 or limit < 1:
        return default
    limit += offset
    limit = len(users)+1 if limit > len(users) else limit
    data = {
        "next": None,
        "users": sorted(
            [
                users[i-1] for i in range(offset, limit)
            ],
            key=lambda u: u[key], reverse=reverse
        ),
    }
    # manage next data
    if offset < len(users) and limit <= len(users):
        limit -= offset
        offset = limit + 1
        data['next'] = f'/users/?limit={limit}&offset={offset}'
    return data


@cache
def filter_user_by_id(id, default={}):
    """Get user api\n

    Args:\n
        id (int): user ID\n
        default (dict, optional): default value if not found. Defaults to {}.\n
    Returns:\n
        User: user found\n
    """
    found = tuple(
        filter(
            lambda u: u['id'] == id,
            users
        )
    )
    return found[0] if len(found) > 0 else default


@cache
def post_user(user: tuple):
    global users
    user = dict(user)
    user = {**user, "id": next_id()}
    users = [*users, user]
    setattr(data, "users", users)
    return user


def patch_user(id: int, user: PartialUser):
    global users
    users = list(map(
        lambda u: u if u['id'] != id else {**u, **user.__dict__},
        users
    ))
    setattr(data, "users", users)
    return users


def put_user(id: int, user: User):
    global users
    users = list(map(
        lambda u: u if u['id'] != id else user,
        users
    ))
    setattr(data, "users", users)
    return users


@cache
def next_id():
    last_user = max(users, key=lambda u: u['id'])
    id = last_user['id'] + 1
    return id
