import time
import exchange
from strategies import gridtrading
import config
import logger
import matplotlib.pyplot as plt
import threads
import gui
import sys
import utils

class NotEnoughArgumentsException(Exception):
    def __init__(self):
        super().__init__("Required: <INVERSION> <RANGE> <+/- LEVLES_FROM_MIDDLE> <DISPLAY_GRAPHS? (True/False)>")


ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = gui.get_settings()

if(len(ARGS) < 4):
    raise NotEnoughArgumentsException()

INVERSION = float(ARGS[0])
RANGE = float(ARGS[1])
LEVELS = int(ARGS[2])
DISPLAY_GRAPHS = utils.toBoolean(ARGS[3])

print(ARGS)

client = exchange.Client(INVERSION)
strategy = gridtrading.GridTrading(INVERSION, RANGE / 100, 0.5, LEVELS, client)

def run_strategy():
    while not strategy.should_exit():
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.update()

    logger.info(logger.EXIT, "Program terminated with wallet status: %s" % str(client.wallet_status()))


if DISPLAY_GRAPHS:
    strategy_thread = threads.Thread(run = run_strategy)
    strategy_thread.start()
    anim = strategy.init_plot_animation()
    plt.show()
else:
    run_strategy()