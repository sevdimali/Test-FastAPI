import itertools
from functools import cache
from models import PartialUser, User, UserModel, Gender
import data
import json
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
def filter_user_by_id(id, default=()):
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
    return found[0] if len(found) > 0 else dict(default)


def post_user(user: PartialUser):
    users = []
    with open("db.json", "r") as js_f:
        users = json.load(js_f)
    with open('db.json', 'w') as js_f:
        users.append({
            **user.__dict__,
            "gender": user.gender.value,
            "date_of_birth": user.date_of_birth.__str__(),
        })
        json.dump(users, js_f, sort_keys=True, indent=2)
        return user


def patch_user(id: int, new_data: PartialUser):
    users = []
    updated_user = None
    with open('db.json', 'r') as js_f:
        for user in json.load(js_f):
            users.append(user)
            if user['id'] == id:
                del users[-1]
                updated_user = {
                    **user,
                    **new_data.__dict__,
                    "gender": new_data.gender.value,
                    "date_of_birth": new_data.date_of_birth.__str__(),
                }
                users.append(updated_user)
    override_db(users)
    return updated_user


def put_user(id: int, new_user: User):
    users = []
    with open('db.json', 'r') as js_f:
        for user in json.load(js_f):
            users.append(user)
            if user['id'] == id:
                del users[-1]
                user = {
                    **new_user.__dict__,
                    "gender": new_user.gender.value,
                    "date_of_birth": new_user.date_of_birth.__str__(),
                }
                users.append(user)
    override_db(users)
    return new_user


def delete_user(id: int):
    users = []
    with open("db.json", "r") as js_f:
        users = list(filter(lambda u: u["id"] != id, json.load(js_f)))
    with open('db.json', 'w') as js_f:
        json.dump(users, js_f, sort_keys=True, indent=2)
        return {"id": id, "deleted": True}


def override_db(users):
    with open('db.json', 'w') as js_f:
        json.dump(users, js_f, sort_keys=True, indent=2)


@cache
def next_id():
    last_user = max(users, key=lambda u: u['id'])
    id = last_user['id'] + 1
    return id
