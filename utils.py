import itertools


def get_users(users, limit=100, offset=1, sort="id:asc", default=[]):

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


def filter_user_by_id(users, id, default={}):
    found = tuple(
        filter(
            lambda u: u['id'] == id,
            users
        )
    )
    return found[0] if len(found) > 0 else default
