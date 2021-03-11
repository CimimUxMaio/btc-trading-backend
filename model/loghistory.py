

class LogHistory:
    def __init__(self, max_size):
        self.__log_history = []
        self.__max_size = max_size

    def add(self, log):
        if len(self.__log_history) + 1 >= self.__max_size:
            self.__log_history.pop(0)

        self.__log_history.append(log)

    @property
    def history(self):
        return self.__log_history
