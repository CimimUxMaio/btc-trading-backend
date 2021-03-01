class Exchange:
    def current_price(self) -> float:
        pass

    def transaction_fee(self) -> float:
        pass

    def tao(self) -> float:
        pass

    def usdt_to_btc_with_fee(self, usdt, price) -> float:
        pass

    def btc_to_usdt_with_fee(self, btc, price) -> float:
        pass

    def set_limit_buy_order(self, usdt, price) -> int:
        pass

    def set_limit_sell_order(self, btc, price) -> int:
        pass

    def was_filled(self, order_id) -> bool:
        pass