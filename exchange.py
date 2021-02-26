import threading
import requests
from datetime import datetime
import config
import logger

HOST = "https://api.binance.com/api/v3"

def _get_resource(resource, params = {}):
    # include API-KEY if needed
    url = HOST + resource
    res = requests.get(url, params)
    res.raise_for_status()
    return res.json()

class FakeExchange:
    def __init__(self, fee=0.001):
        self.fee = fee
        self.__last_price_time = datetime.now()
        self.__last_price = self.__force_get_current_price()
        self.__price_mutex = threading.Lock()

    def current_price(self):
        self.__price_mutex.acquire()
        now = datetime.now()
        delta_time = now - self.__last_price_time
        max_delta = config.STEP_FREQUENCY * 60 * 0.1
        if(delta_time.seconds >= max_delta):
            self.__last_price_time = now
            self.__last_price = self.__force_get_current_price()
        
        self.__price_mutex.release()
        return self.__last_price

    def transaction_fee(self):
        return self.fee

    def tao(self):
        return pow(1-self.transaction_fee(), 2)

    def usdt_to_btc_with_fee(self, usdt, price):
        return usdt * (1- self.transaction_fee()) / price

    def btc_to_usdt_with_fee(self, btc, price):
        return price * btc * (1 - self.transaction_fee())

    # Returns the expected btc to receive
    def set_limit_buy_order(self, usdt, price):
        btc_to_receive = self.usdt_to_btc_with_fee(usdt, price)
        return btc_to_receive

    # Returns the expected usdt to receive
    def set_limit_sell_order(self, btc, price):
        usdt_to_receive = self.btc_to_usdt_with_fee(btc, price)
        return usdt_to_receive

    def set_and_wait_limit_buy_order(self, usdt, price):
        return self.set_limit_buy_order(usdt, price)
    
    def set_and_wait_limit_sell_order(self, btc, price):
        return self.set_limit_sell_order(btc, price)

    def __force_get_current_price(self):
        res = _get_resource("/ticker/price", { "symbol": "BTCUSDT" })
        return float(res["price"])
