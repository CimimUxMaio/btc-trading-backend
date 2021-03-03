import sys
import model.gui as gui
import model.utils as utils
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

    args = list(filter(lambda a: a is not None, args))
    if len(args) < 4:
        return []

    optionals = []
    opts_json = os.environ.get("OPTIONALS")
    if opts_json is not None:
        optionals = list(json.loads(opts_json))

    args.extend(optionals)
    return args

ARGS = sys.argv[1:]
if(len(ARGS) == 0):
    ARGS = get_environmet_variables()

if(len(ARGS) == 0):
    ARGS = gui.get_settings()


if(len(ARGS) < 4):
    utils.raise_exception(NotEnoughArgumentsException())


DISPLAY_GRAPHS = utils.toBoolean(ARGS[0])
INVERSION = float(ARGS[1])
RANGE = float(ARGS[2])
LEVELS = int(ARGS[3])
OPTIONALS = ARGS[4:]