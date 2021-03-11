from model.strategies.tradingstrategy import TradingStrategy
from model.exchange.exchange import Exchange
import model.logger as logger

class GridTrading(TradingStrategy):
    def __init__(self, inversion, range, levels, exchange, starting_price: float=None):

        self.__should_exit = False

        self.exchange: Exchange = exchange
        self.INVERSION = inversion
        self.LEVELS = levels
        self.DELTA = range
        self.STARTING_PRICE = starting_price if starting_price is not None else self.exchange.current_price()
        self.UPPER_BOUND = self.STARTING_PRICE * (1 + range/100)
        self.LOWER_BOUND = self.STARTING_PRICE * (1 - range/100)
        self.LEVEL_HEIGHT = (self.UPPER_BOUND - self.LOWER_BOUND) / (2 * self.LEVELS)
        self.INITIAL_BTC_INVERSION = inversion * 0.5
        self.PER_LEVEL_BUY = self.INITIAL_BTC_INVERSION / self.LEVELS

        self.mid_level = self.STARTING_PRICE
        self.upper_level = self.mid_level + self.LEVEL_HEIGHT
        self.lower_level = self.mid_level - self.LEVEL_HEIGHT

        self.INITIAL_BUY_ORDER = self.exchange.set_limit_buy_order(self.INITIAL_BTC_INVERSION, self.STARTING_PRICE)
        self.INITIAL_BTC = self.exchange.usdt_to_btc_with_fee(self.INITIAL_BTC_INVERSION, self.STARTING_PRICE)
        self.active_orders = { self.__initial_level(): (self.INITIAL_BUY_ORDER,) } 

        self.__started = False

        self.profit = 0
        self.usdt = self.INVERSION
        self.btc = 0

        self.__log_config()

    def update(self):
        if not self.__started and self.__should_start():
            self.__started = True
            self.__on_start()

        current_price = self.exchange.current_price()  
        if self.__started:
            previous_level = self.__current_level() - 1
            next_level = self.__current_level() + 1
            if self.__price_out_of_bounds(current_price):
                self.stop()
                self.on_exit()
            elif current_price <= self.lower_level and self.exchange.was_filled(self.active_orders[previous_level][0]):
                self.__level_down()
                self.__on_level_down()
            elif current_price >= self.upper_level and self.exchange.was_filled(self.active_orders[next_level][0]):
                self.__level_up()
                self.__on_level_up()

    def should_exit(self):
        return self.__should_exit

    def on_exit(self):
        logger.info(logger.EXIT, "Exiting program.")
        self.__log_status()

        for order_id in self.active_orders.values():
            self.exchange.cancel_order(order_id[0])

    def stop(self):
        self.__should_exit = True

    def __should_start(self):
        return self.exchange.was_filled(self.INITIAL_BUY_ORDER)

    def __initial_level(self):
        return self.LEVELS # round((self.STARTING_PRICE - self.LOWER_BOUND) / self.LEVEL_HEIGHT)

    def __current_level(self):
        return round((self.mid_level - self.LOWER_BOUND) / self.LEVEL_HEIGHT)

    def __current_level_price(self):
        return self.mid_level # self.__level_price(self.__current_level())

    def __level_price(self, level):
        return self.LOWER_BOUND + level * self.LEVEL_HEIGHT

    def __price_out_of_bounds(self, price):
        return price <= self.LOWER_BOUND - self.LEVEL_HEIGHT or price >= self.UPPER_BOUND + self.LEVEL_HEIGHT

    def __level_up(self):
        self.lower_level = self.mid_level
        self.mid_level = self.upper_level
        self.upper_level += self.LEVEL_HEIGHT

    def __level_down(self):
        self.upper_level = self.mid_level
        self.mid_level = self.lower_level
        self.lower_level -= self.LEVEL_HEIGHT

    def __balance(self):
        return self.usdt + self.exchange.btc_to_usdt_with_fee(self.btc, self.exchange.current_price())

    def __log_current_level_market_price(self):
        logger.info(logger.MARKET, f"{self.__current_level_price()} USDT / BTC")

    def __return_percentaje(self, buy_price, sell_price):
        return 100 * ((sell_price / buy_price) * self.exchange.tao() -1)
        
    def __estimated_profit_per_sell_range(self):
        max_profit = self.__return_percentaje(self.LOWER_BOUND, self.LOWER_BOUND + self.LEVEL_HEIGHT)
        min_profit = self.__return_percentaje(self.UPPER_BOUND - self.LEVEL_HEIGHT, self.UPPER_BOUND)
        return [min_profit, max_profit]

    def __config(self):
        return {
                "inversion": self.INVERSION, 
                "initial_inversion": self.INITIAL_BTC_INVERSION, 
                "range": self.DELTA, 
                "starting_price": self.STARTING_PRICE, 
                "upper_bound": self.UPPER_BOUND,
                "lower_bound": self.LOWER_BOUND,
                "total_levels": self.LEVELS * 2,
                "level_height": self.LEVEL_HEIGHT,
                "per_level_inversion": self.PER_LEVEL_BUY,
                "profit_range": self.__estimated_profit_per_sell_range()
               }

    def __log_config(self):
        profit_range = self.__estimated_profit_per_sell_range()
        config_description = """

        INVERSION:                   $ %f USDT
        INITIAL BUY:                 $ %f USDT
        RANGE:                         %f %%
        STARTING PRICE:              $ %f USDT
        UPPER BOUND:                 $ %f USDT
        LOWER BOUND:                 $ %f USDT
        TOTAL LEVELS:                  %d
        LEVEL HEIGHT:                $ %f USDT
        PER LEVEL BUY:               $ %f USDT
        ESTIMATED PROFIT PER SELL:   + %f%% - %f%%   (%f USDT - %f USDT)
        """ % (self.INVERSION, self.INITIAL_BTC_INVERSION, self.DELTA, self.STARTING_PRICE, self.UPPER_BOUND, self.LOWER_BOUND, self.LEVELS * 2, self.LEVEL_HEIGHT, self.PER_LEVEL_BUY, profit_range[0], profit_range[1], profit_range[0]*self.PER_LEVEL_BUY/100, profit_range[1]*self.PER_LEVEL_BUY/100)
        logger.info(logger.INIT, config_description)


    def __status(self):
        return {"usdt": self.usdt, "btc": self.btc, "profit": self.profit, "balance": self.__balance()}

    def __log_status(self):
        logger.info(logger.STATUS, f"USDT: {self.usdt}    BTC: {self.btc}    PROFIT: {self.profit} USDT    CURRENT BALANCE: {self.__balance()} USDT")

    def __log_buy(self, btc_bought, usdt_cost):
        logger.next_line()
        self.__log_current_level_market_price()
        logger.info(logger.BUY, f"Bought {btc_bought} BTC for a total of {usdt_cost} USDT.")
        self.__log_status()

    def __log_sell(self, btc_sold, usdt_obtained, profit_gain):
        logger.next_line()
        self.__log_current_level_market_price()
        logger.info(logger.SELL, f"Sold {btc_sold} BTC for a total of {usdt_obtained} USDT.")
        logger.info(logger.PROFIT, f"Profit gained: + {profit_gain} USDT.")
        self.__log_status()

    def __on_start(self):
        logger.info(logger.START, "Bot started!")

        # Initial buy excecuted
        self.usdt -= self.INITIAL_BTC_INVERSION
        self.btc = self.INITIAL_BTC
        self.__log_buy(self.INITIAL_BTC, self.INITIAL_BTC_INVERSION)

        # Upper levels
        for lvl in range(self.__initial_level()+1, 2*self.LEVELS+1):
            to_sell = self.INITIAL_BTC/self.LEVELS
            id = self.exchange.set_limit_sell_order(to_sell, self.__level_price(lvl))
            self.active_orders[lvl] = (id, to_sell)

        # Lower levels
        for lvl in range(0, self.__initial_level()):
            id = self.exchange.set_limit_buy_order(self.PER_LEVEL_BUY, self.__level_price(lvl))
            self.active_orders[lvl] = (id,)

    def __on_level_down(self):
        # Set sell order level+1
        amount_bought = self.exchange.usdt_to_btc_with_fee(self.PER_LEVEL_BUY, self.__current_level_price())
        next_level_price = self.__level_price(self.__current_level()+1)
        new_order = self.exchange.set_limit_sell_order(amount_bought, next_level_price)
        self.active_orders[self.__current_level()+1] = (new_order, amount_bought)

        # Register buy
        self.usdt -= self.PER_LEVEL_BUY
        self.btc += amount_bought
        self.__log_buy(amount_bought, self.PER_LEVEL_BUY)

        self.active_orders.pop(self.__current_level())

    def __on_level_up(self):
        # Set buy order for level-1
        previous_level = self.__current_level()-1
        previous_level_price = self.__level_price(previous_level)
        new_order = self.exchange.set_limit_buy_order(self.PER_LEVEL_BUY, previous_level_price)
        self.active_orders[previous_level] = (new_order,)

        # Register sell
        current_lvl = self.__current_level()
        order_info = self.active_orders[current_lvl]
        amount_sold = order_info[1]
        usdt_obtained = self.exchange.btc_to_usdt_with_fee(amount_sold, self.__current_level_price())
        profit_gain = usdt_obtained - self.PER_LEVEL_BUY
        self.profit += profit_gain
        self.usdt += usdt_obtained
        self.btc -= amount_sold
        self.__log_sell(amount_sold, usdt_obtained, profit_gain)

        self.active_orders.pop(self.__current_level())


    def dto(self):
        return {
            "configuration": self.__config(),
            "status": self.__status()
        }
