import itertools


def get_users(users, limit=100, offset=1, default=[]):
    if offset < 1 or limit < 1:
        print(offset, limit, "Hmm")
        return default
    limit += 1
    limit = len(users) if limit > len(users) else limit
    return [users[i] for i in range(offset-1, limit)]


def filter_user_by_id(users, id, default={}):
    found = tuple(
        filter(
            lambda u: u['id'] == id,
            users
        )
    )
    return found[0] if len(found) > 0 else default
