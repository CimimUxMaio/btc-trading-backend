import threading

class Thread(threading.Thread):
    def __init__(self, run):
        super().__init__()
        self.setDaemon(True)
        self.__run_lambda = run
    
    def run(self):
        self.__run_lambda()
