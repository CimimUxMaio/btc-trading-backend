from model.strategies.gridtrading.gridtrading import GridTrading


class GridTradingBuildException(Exception):
    def __init__(self, missing_components):
        super().__init__(f"Could not build grid trading strategy. Mising components: {missing_components}.")

class GridTradingBuilder:
    def __init__(self):
        self.__components = {}
        for component in ["inversion", "range", "levels", "starting_price", "exchange", "pricehandler"]:
            self.__components[component] = None

    def set_config(self, inversion, range, levels, starting_price):
        self.__components["inversion"] = inversion
        self.__components["range"] = range
        self.__components["levels"] = levels
        self.__components["starting_price"] = starting_price

    def set_exchange_config(self, exchange, pricehandler):
        self.__components["exchange"] = exchange
        self.__components["pricehandler"] = pricehandler

    def build(self):
        missing_components = []
        for component in self.__components.keys():
            if self.__components.get(component, None) is None:
                missing_components.append(component)

        if len(missing_components) > 0:
            raise GridTradingBuildException(missing_components)

        return GridTrading(**self.__components)
