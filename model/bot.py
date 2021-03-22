class Bot:
    def __init__(self, id, strategy):
        self.strategy = strategy
        self.__id = id

    @property
    def id(self):
        return self.__id

    def stop(self):
        self.strategy.stop()

    def dto(self):
        return {
            "id": self.id,
            "strategy": self.strategy.dto()
        }