import json

with open("config.json") as json_file:
    CONFIG = json.load(json_file)

STEP_FREQUENCY = float(CONFIG["step_frequency"])
DEBUG = CONFIG["debug"].lower() == "true"
GRAPH_LENGTH = round(24 * 60 / STEP_FREQUENCY)