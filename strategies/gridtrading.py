import logger
import matplotlib.animation
import matplotlib.pyplot as plt
import config

class GridTrading:
    def __init__(self, inversion, range, start_factor, levels, exchange):
        self.__should_exit = False

        self.EXCHANGE = exchange
        self.INVERSION = inversion
        self.LEVELS = levels
        self.DELTA = range * 100
        self.STARTING_PRICE = self.EXCHANGE.current_price()
        self.UPPER_BOUND = self.STARTING_PRICE * (1 + range)
        self.LOWER_BOUND = self.STARTING_PRICE * (1 - range)
        self.LEVEL_HEIGHT = (self.UPPER_BOUND - self.LOWER_BOUND) / (2 * self.LEVELS)
        self.INITIAL_BUY = inversion * start_factor
        self.PER_LEVEL_BUY = self.INITIAL_BUY / self.LEVELS

        self.mid_level = self.STARTING_PRICE
        self.upper_level = self.mid_level + self.LEVEL_HEIGHT
        self.lower_level = self.mid_level - self.LEVEL_HEIGHT
        self.profit = 0

        self.print_config()

        self.EXCHANGE.buy(self.INITIAL_BUY)
        self.bought_per_level = { self.level(): [self.EXCHANGE.my_BTC / self.LEVELS] * self.LEVELS }

    def initial_level(self):
        return round((self.STARTING_PRICE - self.LOWER_BOUND) / self.LEVEL_HEIGHT)

    def level(self):
        return round((self.mid_level - self.LOWER_BOUND) / self.LEVEL_HEIGHT)

    def register_buy(self, btc_bought):
        level = self.level()
        self.bought_per_level[level] = [btc_bought] + self.bought_per_level.get(level, [])

    def level_up(self):
        self.lower_level = self.mid_level
        self.mid_level = self.upper_level
        self.upper_level += self.LEVEL_HEIGHT

    def level_down(self):
        self.upper_level = self.mid_level
        self.mid_level = self.lower_level
        self.lower_level -= self.LEVEL_HEIGHT

    def print_config(self):
        config_description = """

        INVERSION:       $ %f USDT
        INITIAL BUY:     $ %f USDT
        DELTA:           %% %f
        STARTING PRICE:  $ %f USDT
        UPPER BOUND:     $ %f USDT
        LOWER BOUND:     $ %f USDT
        TOTAL LEVELS:      %d
        LEVEL HEIGHT:    $ %f USDT
        PER LEVEL BUY:   $ %f USDT
        """ % (self.INVERSION, self.INITIAL_BUY, self.DELTA, self.STARTING_PRICE, self.UPPER_BOUND, self.LOWER_BOUND, self.LEVELS * 2, self.LEVEL_HEIGHT, self.PER_LEVEL_BUY)
        logger.info(logger.INIT, config_description)

    def to_sell(self):
        for lvl in reversed(range(self.level())):
            if len(self.bought_per_level.get(lvl, [])) != 0:
                return self.bought_per_level[lvl].pop()
        return 0

    def step(self):
        current_price = self.EXCHANGE.current_price()
        if self.__price_out_of_bounds(current_price):
            self.__should_exit = True
        elif current_price <= self.lower_level:
            self.level_down()
            self.EXCHANGE.buy(self.PER_LEVEL_BUY)
            self.register_buy(self.EXCHANGE.usdt_to_btc_with_fee(self.PER_LEVEL_BUY))
        elif current_price >= self.upper_level:
            self.level_up()
            amount = self.to_sell()
            self.EXCHANGE.sell(amount)
            self.profit += self.EXCHANGE.btc_to_usdt_with_fee(amount) - self.PER_LEVEL_BUY
            logger.debug("profit", str(self.profit))

    def should_exit(self):
        return self.__should_exit

    def bought_per_level_lengths(self):
        result = {}
        for lvl, buys in self.bought_per_level.items():
            result[lvl] = len(buys)

        return result

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

        prices = [self.EXCHANGE.current_price()]
        profits = [self.profit]

        price_lines = price_over_time.plot(prices)
        profit_lines = profit_over_time.plot(profits)
        profit_h_line = profit_over_time.axhline(y=self.profit, linestyle=":", linewidth=0.5)

        def update_graph(i):
            nonlocal price_lines, profit_lines, profit_h_line
            
            current_price = self.EXCHANGE.current_price()
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

    def __price_out_of_bounds(self, price):
        return price <= self.LOWER_BOUND - self.LEVEL_HEIGHT or price >= self.UPPER_BOUND + self.LEVEL_HEIGHT
