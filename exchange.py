import threading
from os import stat
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

class Client:
    def __init__(self, usdt):
        self.my_USDT = usdt
        self.my_BTC = 0
        self.fee_factor = 1 - 0.001  # 0.1% fee
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

    def buy(self, usdt):
        self.__log_market_price()
        USDT_spent = min(usdt, self.my_USDT)
        BTC_bought = self.usdt_to_btc_with_fee(USDT_spent)
        self.my_USDT -= USDT_spent
        self.my_BTC += BTC_bought
        logger.info(logger.BUY, "Bought %f BTC for a total of $ %f USDT" % (BTC_bought, USDT_spent))
        self.__log_wallet_status()

    def sell(self, btc):
        self.__log_market_price()
        BTC_sold = min(btc, self.my_BTC)
        USDT_bought = self.btc_to_usdt_with_fee(BTC_sold)
        self.my_USDT += USDT_bought
        self.my_BTC -= BTC_sold
        logger.info(logger.SELL, "Sold %f BTC for a total of $ %f USDT" % (BTC_sold, USDT_bought))
        self.__log_wallet_status()

    def wallet_status(self):
        return { "USDT": self.my_USDT, "BTC": self.my_BTC, "BALANCE": self.total_balance_in_USDT() }

    def total_balance_in_USDT(self):
        return self.my_USDT + self.btc_to_usdt(self.my_BTC)

    def btc_to_usdt_with_fee(self, btc):
        return self.current_price() * btc * self.fee_factor

    def usdt_to_btc_with_fee(self, usdt):
        return usdt * self.fee_factor / self.current_price()

    def btc_to_usdt(self, btc):
        return self.current_price() * btc

    def usdt_to_btc(self, usdt):
        return usdt / self.current_price()

    def __log_wallet_status(self):
        status = self.wallet_status()
        logger.info(logger.STATUS, "BTC: %f   USDT: %f   BALANCE: %f" % (status["BTC"], status["USDT"], status["BALANCE"]))

    def __force_get_current_price(self):
        res = _get_resource("/ticker/price", { "symbol": "BTCUSDT" })
        return float(res["price"])

    def __log_market_price(self):
        logger.info(logger.MARKET, "Current: 1 BTC = $ %f USDT" % self.current_price())
