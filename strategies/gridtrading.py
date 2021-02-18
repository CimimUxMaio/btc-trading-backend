import logger
import matplotlib.animation
import matplotlib.pyplot as plt
import config
import time

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

    def step(self):
        current_price = self.EXCHANGE.current_price()
        if self.__price_out_of_bounds(current_price):
            self.__should_exit = True
        elif current_price <= self.lower_level:
            self.level_down()
            self.EXCHANGE.buy(self.PER_LEVEL_BUY)
            self.register_buy(self.EXCHANGE.usdt_to_btc_with_fee(self.PER_LEVEL_BUY))
            logger.debug("bought_per_level", str(self.bought_per_level_lengths()))
        elif current_price >= self.upper_level:
            self.level_up()
            self.EXCHANGE.sell(self.to_sell())
            logger.debug("bought_per_level", str(self.bought_per_level_lengths()))

    def should_exit(self):
        return self.__should_exit

    def bought_per_level_lengths(self):
        result = {}
        for lvl, buys in self.bought_per_level.items():
            result[lvl] = len(buys)

        return result

    def init_plot_animation(self):
        plt.title("BTC recent price history (24hs)")
        plt.xlabel("x%.2f min" % config.STEP_FREQUENCY)
        plt.ylabel("USDT")

        level_prices = []
        for lvl in range((self.LEVELS * 2) + 1):
            color = "k"
            if lvl == 0:
                color = "r"
            elif lvl == (self.LEVELS * 2):
                color = "g"

            lvl_price = self.LOWER_BOUND + lvl * self.LEVEL_HEIGHT
            level_prices.append(lvl_price)
            plt.plot([lvl_price] * config.GRAPH_LENGTH, color + ":")

        plt.yticks(level_prices)

        prices = [self.EXCHANGE.current_price()]
        lines = plt.plot(prices)
        def update_graph(i):
            nonlocal lines
            current_price = self.EXCHANGE.current_price()
            prices.append(current_price)
            if len(prices) > config.GRAPH_LENGTH:
                prices.pop(0)

            price_line = lines.pop()
            price_line.remove()
            lines = plt.plot(prices, "m-", linewidth=1)

        return matplotlib.animation.FuncAnimation(plt.gcf(), update_graph, interval=1000*60*config.STEP_FREQUENCY)

    def __price_out_of_bounds(self, price):
        return price <= self.LOWER_BOUND - self.LEVEL_HEIGHT or price >= self.UPPER_BOUND + self.LEVEL_HEIGHT
