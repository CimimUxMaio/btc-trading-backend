from model.exchange.fakebinance import FakeBinance
import time
from model.strategies import gridtrading
import model.config as config
import matplotlib.pyplot as plt
import model.threads as threads
import model.args as args
import model.utils as utils

exchange = FakeBinance()
strategy = gridtrading.GridTrading(args.ARGS.inversion, args.ARGS.range / 100, args.ARGS.levels, exchange, starting_price=args.ARGS.starting_price)

def run_strategy():
    try:
        while True:
            time.sleep(config.STEP_FREQUENCY * 60)
            strategy.update()
            if strategy.should_exit():
                break
    except BaseException as e:
        strategy.on_exit()
        utils.raise_exception(e)

if args.ARGS.display_graphs:
    strategy_thread = threads.Thread(target=run_strategy)
    strategy_thread.start()
    anim = strategy.init_plot_animation()
    plt.show()
    if strategy_thread.is_alive():
        strategy.on_exit()
else:
    run_strategy()