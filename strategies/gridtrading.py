import logger
import matplotlib.animation
import matplotlib.pyplot as plt
import config

class GridTrading:
    def __init__(self, inversion, range, start_factor, levels, exchange):
        self.__should_exit = False

        self.exchange = exchange
        self.INVERSION = inversion
        self.LEVELS = levels
        self.DELTA = range * 100
        self.STARTING_PRICE = self.exchange.current_price()
        self.UPPER_BOUND = self.STARTING_PRICE * (1 + range)
        self.LOWER_BOUND = self.STARTING_PRICE * (1 - range)
        self.LEVEL_HEIGHT = (self.UPPER_BOUND - self.LOWER_BOUND) / (2 * self.LEVELS)
        self.INITIAL_BTC_INVERSION = inversion * start_factor
        self.PER_LEVEL_BUY = self.INITIAL_BTC_INVERSION / self.LEVELS

        self.mid_level = self.STARTING_PRICE
        self.upper_level = self.mid_level + self.LEVEL_HEIGHT
        self.lower_level = self.mid_level - self.LEVEL_HEIGHT

        self.__on_start()

        self.__log_config()

    def update(self):
        current_price = self.exchange.current_price()
        if self.__price_out_of_bounds(current_price):
            self.__should_exit = True
            logger.info(logger.EXIT, "Program terminated.")
            self.__log_status()
        elif current_price <= self.lower_level:
            self.__level_down()
            self.__on_level_down()
        elif current_price >= self.upper_level:
            self.__level_up()
            self.__on_level_up()

    def should_exit(self):
        return self.__should_exit

    def init_plot_animation(self):
        _, axs = plt.subplots(2, sharex=True)
        price_over_time = axs[0]
        profit_over_time = axs[1]
        profit_over_time.set_xlim([0, config.GRAPH_LENGTH+1])
        profit_over_time.set_ylim([-5, 10])

        level_prices = []
        for lvl in range((self.LEVELS * 2) + 1):
            color = "k"
            if lvl == 0:
                color = "r"
            elif lvl == (self.LEVELS * 2):
                color = "g"

            lvl_price = self.LOWER_BOUND + lvl * self.LEVEL_HEIGHT
            level_prices.append(lvl_price)
            price_over_time.axhline(y=lvl_price, color=color, linestyle=":", linewidth=0.5)

        price_over_time.set_title("BTC recent price history (last 24hs)")
        price_over_time.set(ylabel="USDT", yticks=level_prices)

        profit_over_time.set_title("Profit over time (last 24hs)")
        profit_over_time.set(xlabel="x%.2f min" % config.STEP_FREQUENCY, ylabel="Profit (USDT)")

        prices = [self.exchange.current_price()]
        profits = [self.profit]

        price_lines = price_over_time.plot(prices)
        profit_lines = profit_over_time.plot(profits)
        profit_h_line = profit_over_time.axhline(y=self.profit, linestyle=":", linewidth=0.5)

        def update_graph(i):
            nonlocal price_lines, profit_lines, profit_h_line
            
            current_price = self.exchange.current_price()
            prices.append(current_price)
            if len(prices) > config.GRAPH_LENGTH:
                prices.pop(0)

            price_lines.pop().remove()
            price_lines = price_over_time.plot(prices, "m-", linewidth=1)

            profits.append(self.profit)
            if len(profits) > config.GRAPH_LENGTH:
                profits.pop(0)
            
            profit_lines.pop().remove()
            profit_lines = profit_over_time.plot(profits, "g-", linewidth=3)
            profit_h_line.remove()
            profit_h_line = profit_over_time.axhline(y=self.profit, linestyle=":", linewidth=0.5)

        return matplotlib.animation.FuncAnimation(plt.gcf(), update_graph, interval=1000*60*config.STEP_FREQUENCY)

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
        return self.usdt + self.exchange.btc_to_usdt_with_fee(self.btc, self.__current_level_price())

    def __log_current_level_market_price(self):
        logger.info(logger.MARKET, f"{self.__current_level_price()} USDT / BTC")

    def __return_percentaje(self, buy_price, sell_price):
        return 100 * ((sell_price / buy_price) * self.exchange.tao() -1)
        
    def __estimated_profit_per_sell_range(self):
        min_sell_price = self.LOWER_BOUND + self.LEVEL_HEIGHT
        max_profit = self.__return_percentaje(self.LOWER_BOUND, min_sell_price)
        max_buy_price = self.UPPER_BOUND - self.LEVEL_HEIGHT
        min_profit = self.__return_percentaje(max_buy_price, self.UPPER_BOUND)
        return [min_profit, max_profit]

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
        """ % (self.INVERSION, self.INITIAL_BTC_INVERSION, self.DELTA, self.STARTING_PRICE, self.UPPER_BOUND, self.LOWER_BOUND, self.LEVELS * 2, self.LEVEL_HEIGHT, self.PER_LEVEL_BUY, profit_range[0], profit_range[1], profit_range[0]*self.PER_LEVEL_BUY/100, profit_range[1]*self.PER_LEVEL_BUY / 100)
        logger.info(logger.INIT, config_description)
        self.__log_status()

    def __log_status(self):
        logger.info(logger.STATUS, f"USDT: {self.usdt}    BTC: {self.btc}    PROFIT: {self.profit} USDT    CURRENT BALANCE: {self.__balance()} USDT")

    def __on_start(self):
        self.INITIAL_BTC = self.exchange.set_and_wait_limit_buy_order(self.INITIAL_BTC_INVERSION, self.STARTING_PRICE)
        self.__sold_initial_buy = {}
        self.profit = self.INITIAL_BTC_INVERSION * (self.exchange.tao() - 1)
        self.usdt = self.INVERSION - self.INITIAL_BTC_INVERSION
        self.btc = self.INITIAL_BTC

        # Upper levels
        for lvl in range(self.__initial_level()+1, 2*self.LEVELS+1):
            self.exchange.set_limit_sell_order(self.INITIAL_BTC/self.LEVELS, self.__level_price(lvl))
            self.__sold_initial_buy[lvl] = False

        # Lower levels
        for lvl in range(0, self.__initial_level()):
            self.exchange.set_limit_buy_order(self.PER_LEVEL_BUY, self.__level_price(lvl))

    def __on_level_down(self):
        # Set sell order level+1
        amount_bought = self.exchange.usdt_to_btc_with_fee(self.PER_LEVEL_BUY, self.__current_level_price())
        next_level_price = self.__level_price(self.__current_level()+1)
        self.exchange.set_limit_sell_order(amount_bought, next_level_price)

        # Notify buy
        self.usdt -= self.PER_LEVEL_BUY
        self.btc += amount_bought
        self.__log_current_level_market_price()
        logger.info(logger.BUY, f"Bought {amount_bought} BTC for a total of {self.PER_LEVEL_BUY} USDT.")
        self.__log_status()

    def __on_level_up(self):
        # Set buy order for level-1
        previous_level_price = self.__level_price(self.__current_level()-1)
        self.exchange.set_limit_buy_order(self.PER_LEVEL_BUY, previous_level_price)

        # Notify sell
        current_lvl = self.__current_level()
        previous_price = previous_level_price
        if(not self.__sold_initial_buy.get(current_lvl, True)):
            previous_price = self.STARTING_PRICE
            self.__sold_initial_buy[current_lvl] = True
            
        amount_sold = self.exchange.usdt_to_btc_with_fee(self.PER_LEVEL_BUY, previous_price)
        usdt_obtained = self.exchange.btc_to_usdt_with_fee(amount_sold, self.__current_level_price())
        profit_gain = usdt_obtained - self.PER_LEVEL_BUY
        self.profit += profit_gain
        self.usdt += usdt_obtained
        self.btc -= amount_sold
        self.__log_current_level_market_price()
        logger.info(logger.SELL, f"Sold {amount_sold} BTC for a total of {usdt_obtained} USDT.")
        logger.info(logger.PROFIT, f"Profit gained: + {profit_gain} USDT.")
        self.__log_status()
