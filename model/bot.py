import model.strategies.strategystage as strategystage


class Bot:
    def __init__(self, id, strategy):
        self.strategy = strategy
        self.__id = id

    @property
    def id(self):
        return self.__id

    def stop(self):
        self.strategy.stop()

    def is_terminated(self):
        return self.strategy.stage == strategystage.TERMINATED
            
    def dto(self):
        return {
            "id": self.id,
            "strategy": self.strategy.dto()
        }
