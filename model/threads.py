import threading

class Thread(threading.Thread):
    def __init__(self, target):
        super().__init__(target=target, daemon=True)