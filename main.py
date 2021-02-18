import random
import time
import exchange
import ai
import sys
import config
import logger
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import graph

class NotEnoughArgumentsException(Exception):
    def __init__(self):
        super().__init__("Required: <INVERSION> <RANGE> <START_FACTOR> <+/- LEVLES_FROM_MIDDLE>")


if(len(sys.argv) < 5):
    raise NotEnoughArgumentsException()

ARGS = sys.argv[1:]

INVERSION = float(ARGS[0])
RANGE = float(ARGS[1])
START = float(ARGS[2])
LEVELS = int(ARGS[3])

client = exchange.Client(INVERSION)
strategy = ai.GridTrading(INVERSION, RANGE, START, LEVELS, client)

def run_strategy():
    while not strategy.should_exit():
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.step()

    logger.info(logger.EXIT, "Program terminated with wallet status: %s" % str(client.wallet_status()))


class Thread(threading.Thread):
    def __init__(self, run):
        super().__init__()
        self.setDaemon(True)
        self.__run_lambda = run
    
    def run(self):
        self.__run_lambda()


strategy_thread = Thread(run = run_strategy)
strategy_thread.start()


anim = graph.init_price_over_time_animation(client, strategy)
plt.show()