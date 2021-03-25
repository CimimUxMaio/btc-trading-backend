import http


class HttpError(Exception):
    def __init__(self, message, code):
        super().__init__(f"{message}")
        self.code = code


def TokenNotFoundError():
    return HttpError("Token not found", http.HTTPStatus.UNAUTHORIZED)

def BadParametersError():
    return HttpError("Bad parameters", http.HTTPStatus.BAD_REQUEST)

def BotNotFoundError():
    return HttpError("Bot not found", http.HTTPStatus.NOT_FOUND)

def UserAlreadyExistsError():
    return HttpError("User already exists", http.HTTPStatus.CONFLICT)

def BotStillRunningError():
    return HttpError("Bot is still running", http.HTTPStatus.FORBIDDEN)
