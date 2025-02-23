import logging
import model.config as config

logging.basicConfig(format="[%(asctime)s][%(levelname)s]%(message)s")
__logger = logging.getLogger(__name__)
__logger.setLevel(logging.DEBUG)

def info(event, message):
    __logger.info("[%s] %s" % (event, message))


def debug(target_variable_name, message):
    if(config.DEBUG):
        __logger.debug(" %s: %s" % (target_variable_name, message))

def next_line():
    print()


def error(name, cause):
    __logger.error(msg=f"[{name}] {cause}")

# Events

BUY = "BUY"
SELL = "SELL"
MARKET = "MARKET"
STATUS = "STATUS"
INIT = "INIT"
START = "START"
EXIT = "EXIT"
PROFIT = "PROFIT"
ORDER_CANCEL = "ORDER CANCEL"