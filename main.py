from exchange.fakebinance import FakeBinance
import time
from strategies import gridtrading
import config
import matplotlib.pyplot as plt
import threads
import args

exchange = FakeBinance()
strategy = gridtrading.GridTrading(args.INVERSION, args.RANGE / 100, args.LEVELS, exchange, *args.OPTIONALS)

def run_strategy():
    while True:
        time.sleep(config.STEP_FREQUENCY * 60)
        strategy.update()
        if strategy.should_exit():
            break

if args.DISPLAY_GRAPHS:
    strategy_thread = threads.Thread(run = run_strategy)
    strategy_thread.start()
    anim = strategy.init_plot_animation()
    plt.show()
else:
    run_strategy()