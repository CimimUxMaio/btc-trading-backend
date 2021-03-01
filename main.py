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
        super().__init__("Required: <INVERSION> <RANGE (%)> <+/- LEVLES_FROM_MIDDLE> <DISPLAY_GRAPHS? (True/False)> <STARTING_PRICE (OPTIONAL)>")


ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = gui.get_settings()

if(len(ARGS) < 4):
    raise NotEnoughArgumentsException()

INVERSION = float(ARGS[0])
RANGE = float(ARGS[1])
LEVELS = int(ARGS[2])
DISPLAY_GRAPHS = utils.toBoolean(ARGS[3])
ARGS = ARGS[4:]

client = FakeBinance()
strategy = gridtrading.GridTrading(INVERSION, RANGE / 100, LEVELS, client, *ARGS)

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