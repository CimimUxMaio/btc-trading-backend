import http


class HttpError(Exception):
    def __init__(self, message, code):
        super().__init__(f"{message}. Code: {code}")
        self.code = code


def TokenNotFoundError():
    return HttpError("Token not found", http.HTTPStatus.UNAUTHORIZED)

def BadParametersError():
    return HttpError("Bad parameters", http.HTTPStatus.BAD_REQUEST)

def BotNotFoundError():
    return HttpError("Bot not found", http.HTTPStatus.NOT_FOUND)