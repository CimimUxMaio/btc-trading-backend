import matplotlib.animation
import matplotlib.pyplot as plt
import config

def init_price_over_time_animation(exchange, strategy):
    plt.title("BTC recent price history (24hs)")
    plt.xlabel("x%.2f min" % config.STEP_FREQUENCY)
    plt.ylabel("USDT")

    level_prices = []
    for lvl in range((strategy.LEVELS * 2) + 1):
        color = "k"
        if lvl == 0:
            color = "r"
        elif lvl == (strategy.LEVELS * 2):
            color = "g"

        lvl_price = strategy.LOWER_BOUND + lvl * strategy.LEVEL_HEIGHT
        level_prices.append(lvl_price)
        plt.plot([lvl_price] * config.GRAPH_LENGTH, color + ":")

    plt.yticks(level_prices)

    prices = [exchange.current_price()]
    lines = plt.plot(prices)
    def update_graph(i):
        nonlocal lines
        current_price = exchange.current_price()
        prices.append(current_price)
        if len(prices) > config.GRAPH_LENGTH:
            prices.pop(0)

        price_line = lines.pop()
        price_line.remove()
        lines = plt.plot(prices, "m-", linewidth=1)

    return matplotlib.animation.FuncAnimation(plt.gcf(), update_graph, interval=1000*60*config.STEP_FREQUENCY)