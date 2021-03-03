import sys
import gui
import utils
import os
import json

class NotEnoughArgumentsException(Exception):
    def __init__(self):
        super().__init__("Required: <DISPLAY_GRAPHS? (True/False)> <INVERSION> <RANGE (%)> <+/- LEVLES_FROM_MIDDLE> <STARTING_PRICE (OPTIONAL)>")


def get_environmet_variables():
    args = []
    args.append(os.environ.get("DISPLAY_GRAPHS"))
    args.append(os.environ.get("INVERSION"))
    args.append(os.environ.get("RANGE"))
    args.append(os.environ.get("LEVELS"))
    optionals = json.loads(os.environ.get("OPTIONALS"))
    for opt in optionals:
        args.append(opt)

    return list(filter(lambda a: a is not None, args))

ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = get_environmet_variables()
    if(len(ARGS) < 4):
        ARGS = gui.get_settings()

if(len(ARGS) < 4):
    raise NotEnoughArgumentsException()

DISPLAY_GRAPHS = utils.toBoolean(ARGS[0])
INVERSION = float(ARGS[1])
RANGE = float(ARGS[2])
LEVELS = int(ARGS[3])
OPTIONALS = ARGS[4:]




