from model.httperrors import UserAlreadyExistsError


__users = []

def get_by_email(email):
    return next((u for u in __users if u.email == email), None)


def get_by_id(id):
    return next((u for u in __users if u.id == id), None)


def email_exists(email):
    return get_by_email(email) is not None

def add(user):
    if email_exists(user.email):
        raise UserAlreadyExistsError()
    
    __users.append(user)