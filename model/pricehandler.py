import threading
import model.config as config
import time
import requests

class BinancePriceEventHandler(threading.Thread):
    def __init__(self):
        super().__init__(target=self.__run_strategy, daemon=True)
        self.observers = []

    def notify_all(self):
        new_price = self.__get_price()
        for observer in self.observers:
            try:
                observer.update_price(new_price)
            except:
                observer.stop()

    def add_observer(self, o):
        self.observers.append(o)

    def remove_observer(self, o):
        self.observers = list(filter(lambda other: other != o, self.observers))

    def peek_price(self):
        return self.__get_price()

    def __get_price(self):
        res = self.__get_resource("/ticker/price", { "symbol": "BTCUSDT" })
        return float(res["price"])

    def __run_strategy(self):
        while True:
            time.sleep(config.STEP_FREQUENCY * 60)
            self.notify_all()

    def __get_resource(self, resource, params = {}):
        # include API-KEY if needed
        url = config.BINANCE_API + resource
        res = requests.get(url, params)
        res.raise_for_status()
        return res.json()


INSTANCE = BinancePriceEventHandler()

def start_instance():
    INSTANCE.start()

