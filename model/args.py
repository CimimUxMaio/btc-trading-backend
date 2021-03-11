import envargparse

# parser = envargparse.EnvArgParser()

# # Mandatory
# name = "inversion"
# parser.add_argument(f"--{name}", required=True, env_var=name.upper(), type=float,
#                         help="The amount of USDT to be used by the bot")

# name = "range"
# parser.add_argument(f"--{name}", required=True, env_var=name.upper(), type=float,
#                         help="The range from the starting price (%%) where the bot will operate")

# name = "levels"
# parser.add_argument(f"--{name}", required=True, env_var=name.upper(), type=int,
#                         help="The amount of levels to be set on the grid divided by two")

# # Optional
# name = "starting_price"
# parser.add_argument(f"--{name}", env_var=name.upper(), type=float, nargs="?",
#                         help="Starting price at with the bot will start to operate in USDT")

# ARGS = parser.parse_args()