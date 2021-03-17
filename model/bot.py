from model.strategies.tradingstrategy import TradingStrategy
import threading
import model.config as config
import model.utils as utils
import time


class Bot(threading.Thread):
    def __init__(self, owner, strategy):
        super().__init__(target=self.__run_strategy, daemon=True)
        self.strategy: TradingStrategy = strategy
        self.__owner = owner
        self.__id = owner.next_bot_id()

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

    def __run_strategy(self):
        try:
            while True:
                time.sleep(config.STEP_FREQUENCY * 60)
                self.strategy.update()
                if self.strategy.should_exit():
                    break
        except BaseException as e:
            self.strategy.on_exit()
            utils.raise_exception(e)

        self.__owner.unregister_bot(self.id)