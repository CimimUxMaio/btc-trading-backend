from enum import Enum
import datetime


class Event(Enum):
    BUY = "BUY"
    SELL = "SELL"
    START = "START"
    TERMINATE = "TERMINATE"


class StrategyLog:
    def __init__(self, event, market_price, status):
        self.__event = event
        self.__time = datetime.datetime.now()
        self.__market_price = market_price
        self.__status = status

    @property
    def event(self):
        return self.__event

    @property
    def time(self):
        return self.__time

    @property
    def market_price(self):
        return self.__market_price

    @property
    def status(self):
        return self.__status

    def dto(self):
        return {
            "event": self.event.name,
            "time": self.time,
            "market_price": self.market_price,
            "status": self.status
        }