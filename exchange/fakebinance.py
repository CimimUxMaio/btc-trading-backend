from exchange.exchange import Exchange
import threading
import requests
from datetime import datetime
import config

HOST = "https://api.binance.com/api/v3"

def _get_resource(resource, params = {}):
    # include API-KEY if needed
    url = HOST + resource
    res = requests.get(url, params)
    res.raise_for_status()
    return res.json()

class FakeBinance(Exchange):
    def __init__(self, fee=0.001):
        self.fee = fee
        self.__last_price_time = datetime.now()
        self.__last_price = self.__force_get_current_price()
        self.__price_mutex = threading.Lock()
        self.__order_id_acum = 1
        self.__order_prices = {}

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

    def set_limit_buy_order(self, usdt, price):
        return self.__generate_order(price)

    def set_limit_sell_order(self, btc, price):
        return self.__generate_order(price)

    def was_filled(self, order_id):
        price_when_ordered = self.__order_prices[order_id][0]
        order_price = self.__order_prices[order_id][1]
        current_price = self.current_price()
        return price_when_ordered <= order_price <= current_price or price_when_ordered >= order_price >= current_price

    def __force_get_current_price(self):
        res = _get_resource("/ticker/price", { "symbol": "BTCUSDT" })
        return float(res["price"])

    def __generate_order(self, price):
        order_id = self.__order_id_acum
        self.__order_id_acum += 1
        self.__order_prices[order_id] = (self.current_price(), price)
        return order_id

    def __get_fees(self):
        pass