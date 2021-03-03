from matplotlib.animation import FuncAnimation


class TradingStrategy:
    def update(self):
        pass

    def should_exit(self) -> bool:
        pass

    def init_plot_animation(self) -> FuncAnimation:
        pass

    def on_exit(self):
        pass