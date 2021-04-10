def filter_user_by_id(users, id, default={}):
    found = tuple(filter(lambda u: u['id'] == id, users))
    return found[0] if len(found) > 0 else default
