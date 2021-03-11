from model.strategies.tradingstrategy import TradingStrategy
import threading
import model.config as config
import model.utils as utils
import time
import uuid


class Bot(threading.Thread):
    def __init__(self, strategy):
        self.id = uuid.uuid1()
        self.strategy: TradingStrategy = strategy
        super().__init__(target=self.__run_strategy, daemon=True)

    def stop(self):
        self.strategy.stop()

    def dto(self):
        return {
            "id": self.id.int,
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