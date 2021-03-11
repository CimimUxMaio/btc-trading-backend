from matplotlib.animation import FuncAnimation


class TradingStrategy:
    def update(self):
        pass

    def should_exit(self) -> bool:
        pass

    def on_exit(self):
        pass

    def log_history(self):
        pass

    def dto(self):
        pass

    def stop(self):
        pass