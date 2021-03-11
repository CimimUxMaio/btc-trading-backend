__users = []

def get_by_user(username):
    return next((u for u in __users if u.username == username), None)


def get_by_id(id):
    return next((u for u in __users if u.id == id), None)


def add(user):
    __users.append(user)