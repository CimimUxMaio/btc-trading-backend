import time
import exchange
from strategies import gridtrading
import sys
import config
import logger
import matplotlib.pyplot as plt
import threads

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
strategy = gridtrading.GridTrading(INVERSION, RANGE, START, LEVELS, client)

def run_strategy():
    while not strategy.should_exit():
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.step()

    logger.info(logger.EXIT, "Program terminated with wallet status: %s" % str(client.wallet_status()))


strategy_thread = threads.Thread(run = run_strategy)
strategy_thread.start()

anim = strategy.init_plot_animation()
plt.show()