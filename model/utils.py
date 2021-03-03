import model.logger as logger

def toBoolean(s):
    return s.lower() == "true"


def raise_exception(ex):
    name = type(ex).__name__
    cause = str(ex)
    logger.error(name, cause)
    exit()