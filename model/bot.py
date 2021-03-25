import model.strategies.strategystage as strategystage


class Bot:
    def __init__(self, id, name, strategy):
        self.strategy = strategy
        self.__id = id
        self.__name = name

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name

    def stop(self):
        self.strategy.stop()

    def is_terminated(self):
        return self.strategy.stage == strategystage.TERMINATED
            
    def dto(self):
        return {
            "id": self.id,
            "name": self.name,
            "strategy": self.strategy.dto()
        }
