from model.exchange.exchange import Exchange
import model.logger as logger
import model.pricehandler as pricehandler

class FakeBinance(Exchange):
    def __init__(self, fee=0.001):
        self.fee = fee
        self.__order_id_acum = 1
        self.__order_prices = {}

    def transaction_fee(self):
        return self.fee

    def set_limit_buy_order(self, usdt, price):
        return self.__generate_order(price)

    def set_limit_sell_order(self, btc, price):
        return self.__generate_order(price)

    def was_filled(self, order_id):
        price_when_ordered = self.__order_prices[order_id][0]
        order_price = self.__order_prices[order_id][1]
        current_price = self.__current_price()
        return price_when_ordered <= order_price <= current_price or price_when_ordered >= order_price >= current_price

    def cancel_order(self, order_id):
        logger.info(logger.ORDER_CANCEL, f"Order {order_id} was canceled.")

    def __generate_order(self, price):
        order_id = self.__order_id_acum
        self.__order_id_acum += 1
        self.__order_prices[order_id] = (self.__current_price(), price)
        return order_id

    def __current_price(self):
        return pricehandler.INSTANCE.peek_price()
