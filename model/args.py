import argparse
import os
import sys

parser = argparse.ArgumentParser()

# Positional
name = "inversion"
parser.add_argument(name, type=float, default=os.environ.get(name.upper()),
                        help="The amount of USDT to be used by the bot")

name = "range"
parser.add_argument(name, type=float, default=os.environ.get(name.upper()),
                        help="The range from the starting price (%%) where the bot will operate")

name = "levels"
parser.add_argument(name, type=int, default=os.environ.get(name.upper()),
                        help="The amount of levels to be set on the grid divided by two")

# Optional
name = "display_graphs"
parser.add_argument(f"--{name}", action="store_true", default=os.environ.get(name.upper()),
                        help="Display the bot's graphs")

name = "starting_price"
parser.add_argument(f"--{name}", type=float, default=os.environ.get(name.upper()),
                        help="Starting price at with the bot will start to operate in USDT")

ARGS = parser.parse_args()