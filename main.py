import time
import exchange
from strategies import gridtrading
import config
import logger
import matplotlib.pyplot as plt
import threads
import gui
import sys

class NotEnoughArgumentsException(Exception):
    def __init__(self):
        super().__init__("Required: <INVERSION> <RANGE> <+/- LEVLES_FROM_MIDDLE>")

arg_len = len(sys.argv)
if(arg_len == 1):
    ARGS = gui.get_settings()
elif(len(sys.argv) < 4):
    raise NotEnoughArgumentsException()
else:
    ARGS = sys.argv[1:]

INVERSION = float(ARGS[0])
RANGE = float(ARGS[1])
LEVELS = int(ARGS[2])

client = exchange.Client(INVERSION)
strategy = gridtrading.GridTrading(INVERSION, RANGE / 100, 0.5, LEVELS, client)

def run_strategy():
    while not strategy.should_exit():
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.step()

    logger.info(logger.EXIT, "Program terminated with wallet status: %s" % str(client.wallet_status()))


strategy_thread = threads.Thread(run = run_strategy)
strategy_thread.start()

anim = strategy.init_plot_animation()
plt.show()