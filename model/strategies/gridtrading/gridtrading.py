from model.strategylog import StrategyLog, Event
import model.strategies.strategystage as strategystage
import model.loghistory as loghistory
import model.config as config


class GridTrading:
    def __init__(self, inversion, range, levels, starting_price, exchange, pricehandler):
        self.__log_history = loghistory.LogHistory(config.MAX_LOG_HISTORY_SIZE)

        self.exchange = exchange
        self.INVERSION = inversion
        self.LEVELS = levels
        self.DELTA = range
        self.STARTING_PRICE = starting_price
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
        
        self.__stage = strategystage.NEW
        self.__pricehandler = pricehandler
        self.__pricehandler.add_observer(self)

    def update_price(self, current_price):
        if self.__should_start():
            self.__started = True
            self.__on_start()

        if self.__started:
            previous_level = self.__current_level() - 1
            next_level = self.__current_level() + 1

            if self.__price_out_of_bounds(current_price):
                self.stop()
                return

            if current_price <= self.lower_level and self.exchange.was_filled(self.active_orders[previous_level][0]):
                self.__level_down()
                self.__on_level_down()
            elif current_price >= self.upper_level and self.exchange.was_filled(self.active_orders[next_level][0]):
                self.__level_up()
                self.__on_level_up()

    def stop(self):
        self.__log_event(Event.TERMINATE)
        self.__stage = strategystage.TERMINATED
        self.__pricehandler.remove_observer(self)

        for order_id in self.active_orders.values():
            self.exchange.cancel_order(order_id[0])

    def dto(self):
        return {
            "stage": self.__stage,
            "configuration": self.__config(),
            "status": self.__status(),
            "logs": [log.dto() for log in self.__log_history.history]
        }

    @property
    def stage(self):
        return self.__stage

    def __should_start(self):
        return not self.__started and self.exchange.was_filled(self.INITIAL_BUY_ORDER)

    def __initial_level(self):
        return self.LEVELS

    def __current_level(self):
        return round((self.mid_level - self.LOWER_BOUND) / self.LEVEL_HEIGHT)

    def __current_level_price(self):
        return self.mid_level

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

    def __return_percentaje(self, buy_price, sell_price):
        return 100 * ((sell_price / buy_price) * self.exchange.tao() -1)
        
    def __estimated_profit_per_sell_range(self):
        max_profit = self.__return_percentaje(self.LOWER_BOUND, self.LOWER_BOUND + self.LEVEL_HEIGHT)
        min_profit = self.__return_percentaje(self.UPPER_BOUND - self.LEVEL_HEIGHT, self.UPPER_BOUND)
        return [min_profit, max_profit]

    def __config(self):
        return {
                "inversion": self.INVERSION, 
                "initialInversion": self.INITIAL_BTC_INVERSION, 
                "range": self.DELTA, 
                "startingPrice": self.STARTING_PRICE, 
                "upperBound": self.UPPER_BOUND,
                "lowerBound": self.LOWER_BOUND,
                "totalLevels": self.LEVELS * 2,
                "levelHeight": self.LEVEL_HEIGHT,
                "perLevelInversion": self.PER_LEVEL_BUY,
                "profitRange": self.__estimated_profit_per_sell_range()
               }

    def __status(self):
        return {"usdt": self.usdt, "btc": self.btc, "profit": self.profit, "balance": self.__balance()}

    def __balance(self):
        return self.usdt + self.exchange.btc_to_usdt_with_fee(self.btc, self.__pricehandler.peek_price())

    def __on_start(self):
        self.__log_event(Event.START)
        self.__stage = strategystage.RUNNING

        # Initial buy excecuted
        self.usdt -= self.INITIAL_BTC_INVERSION
        self.btc = self.INITIAL_BTC
        self.__log_event(Event.BUY)

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
        self.__log_event(Event.BUY)

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
        self.__log_event(Event.SELL, profit_gain=profit_gain)

        self.active_orders.pop(self.__current_level())

    def __log_event(self, event, profit_gain=0):
        return self.__log_history.add(StrategyLog(event, self.__current_level_price(), profit_gain))
