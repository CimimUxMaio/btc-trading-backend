from exchange.fakebinance import FakeBinance
import time
from strategies import gridtrading
import config
import matplotlib.pyplot as plt
import threads
import gui
import sys
import utils

class NotEnoughArgumentsException(Exception):
    def __init__(self):
        super().__init__("Required: <DISPLAY_GRAPHS? (True/False)> <INVERSION> <RANGE (%)> <+/- LEVLES_FROM_MIDDLE> <STARTING_PRICE (OPTIONAL)>")


ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = gui.get_settings()

if(len(ARGS) < 4):
    raise NotEnoughArgumentsException()

DISPLAY_GRAPHS = utils.toBoolean(ARGS[0])
INVERSION = float(ARGS[1])
RANGE = float(ARGS[2])
LEVELS = int(ARGS[3])
ARGS = ARGS[4:]

exchange = FakeBinance()
strategy = gridtrading.GridTrading(INVERSION, RANGE / 100, LEVELS, exchange, *ARGS)

def run_strategy():
    while True:
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.update()
        if strategy.should_exit():
            break

if DISPLAY_GRAPHS:
    strategy_thread = threads.Thread(run = run_strategy)
    strategy_thread.start()
    anim = strategy.init_plot_animation()
    plt.show()
else:
    run_strategy()