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
        super().__init__("Required: <STARTING_PRICE> <INVERSION> <RANGE (%)> <+/- LEVLES_FROM_MIDDLE> <DISPLAY_GRAPHS? (True/False)>")


ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = gui.get_settings()

if(len(ARGS) < 4):
    raise NotEnoughArgumentsException()

STARTING_PRICE = float(ARGS[0])
INVERSION = float(ARGS[1])
RANGE = float(ARGS[2])
LEVELS = int(ARGS[3])
DISPLAY_GRAPHS = utils.toBoolean(ARGS[4])

client = FakeBinance()
strategy = gridtrading.GridTrading(STARTING_PRICE, INVERSION, RANGE / 100, LEVELS, client)

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