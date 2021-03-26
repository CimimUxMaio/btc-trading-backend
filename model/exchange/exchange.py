from abc import ABC, abstractmethod

class Exchange(ABC):
    @abstractmethod
    def transaction_fee(self) -> float:
        pass

    @abstractmethod
    def set_limit_buy_order(self, usdt, price):
        pass
    
    @abstractmethod
    def set_limit_sell_order(self, btc, price):
        pass

    @abstractmethod
    def was_filled(self, order_id):
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        pass

    def tao(self):
        return pow(1-self.transaction_fee(), 2)

    def usdt_to_btc_with_fee(self, usdt, price):
        return usdt * (1- self.transaction_fee()) / price

    def btc_to_usdt_with_fee(self, btc, price):
        return price * btc * (1 - self.transaction_fee())

